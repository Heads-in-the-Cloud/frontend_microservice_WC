from flask import Flask, render_template, request, make_response, redirect, url_for, flash
from flask_jwt_extended.view_decorators import verify_jwt_in_request
from forms import *
import logging, os, requests
from dotenv import load_dotenv
import traceback
from flask_jwt_extended import get_jwt, JWTManager, create_access_token, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from datetime import datetime, timezone, timedelta

load_dotenv()

app = Flask(__name__)
jwt = JWTManager(app)

logging.basicConfig(level=logging.INFO)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["JWT_COOKIE_SECURE"]                         = False
app.config["JWT_TOKEN_LOCATION"]                        = ["cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"]                   = False

TRAVELER_ROLE=os.getenv('TRAVELER_ROLE')
HOST_DOMAIN=os.getenv('HOST_DOMAIN')


@app.route('/health', methods = ['GET'])
def health():
    return 'health'

@app.route('/lms/health', methods = ['GET'])
def health_public():
    return 'changed'


@app.route('/lms/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    #return the template if the user is just accessing the page
    if request.method == 'GET':
        return render_template('login.html', title='Login', form=form)

    #facilitate a login action if the request is of POST
    if form.validate_on_submit():
        response = requests.post(HOST_DOMAIN+'/login', json=request.form.to_dict())
        logging.info(response)
        if response.status_code == 401:
            flash('Invalid credentials!', 'danger')
            return render_template('login.html', title='Login', form=form)

        token = response.cookies.get('access_token_cookie')
        response = make_response(redirect('/lms/routes'))
        set_access_cookies(response, token)
        flash('You have been logged in!', 'success')
        return response
    return render_template('login.html', title='Login', form=form)

@app.route('/lms/logout', methods = ['GET'])
def logout():
    response = redirect(url_for('login'))
    unset_jwt_cookies(response)
    return response

@app.route('/lms/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template('register.html', title='Register', form=form)
    
    elif request.method == 'POST':
        json = request.form.to_dict()
        json['role_id'] = TRAVELER_ROLE
        response = requests.post(HOST_DOMAIN+'/user/add', json=json)
        return response.json()


@app.route('/lms/home', methods = ['GET'])
def home():    
    routes = requests.get(HOST_DOMAIN+'/airline/read/route_with_flights', cookies=request.cookies).json()
    logging.info(routes)
    return render_template('home.html', title='Home', routes=routes, logged_in=verify_jwt_in_request(optional=True))


@app.route('/lms/routes', methods = ['GET'])
def routes():    
    routes = requests.get(HOST_DOMAIN+'/airline/read/route', cookies=request.cookies).json()
    return render_template('routes.html', title='Routes', routes=routes, logged_in=verify_jwt_in_request(optional=True))


@app.route('/lms/flights', methods = ['GET'])
def flights_all():    
    routes = requests.get(HOST_DOMAIN+'/airline/read/route_with_flights', cookies=request.cookies).json()
    return render_template('flights.html', title='Flights', routes=routes, logged_in=verify_jwt_in_request(optional=True))


@app.route('/lms/flights/<id>', methods = ['GET'])
def flights_by_route(id):    
    response = requests.get(HOST_DOMAIN+'/airline/read/route_with_flights/'+id, cookies=request.cookies)
    routes = response.json()
    if response.status_code == 404 or len(routes['flights']) == 0:
        return render_template('404.html', title='NotFound')
    return render_template('flights.html', title='Flights', routes=[routes], logged_in=verify_jwt_in_request(optional=True))


@app.route('/lms/booking/flight_id=<flight_id>', methods = ['GET', 'POST'])
def booking(flight_id):
    user_id = None

    if request.method == 'POST':
        response = redirect(url_for('add_passengers', user_id='guest'))
        response.cookies = request.cookies
        response.set_cookie('contact_email', request.form['email'])
        response.set_cookie('contact_phone', request.form['phone'])
        response.set_cookie('flight_id', flight_id)
        return response
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
    except:

        form = BookingGuestForm()
        return render_template('booking.html', title='Booking', flight_id=flight_id, form=form, logged_in=False)

    
    response = redirect(url_for('add_passengers', user_id=user_id, logged_in=True))
    response.set_cookie('flight_id', flight_id)
    return response

@app.route('/lms/passengers/user=<user_id>', methods = ['GET', 'POST'])
def add_passengers(user_id):
    form = PassengerForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            passengers = []
            for g_name, f_name, dob, address, gender in zip(
            request.form.getlist('given_name'),
            request.form.getlist('family_name'),
            request.form.getlist('dob'),
            request.form.getlist('gender'),
            request.form.getlist('address')):
                passengers.append({
                    'given_name': g_name, 'family_name': f_name, 'dob': dob, 'gender': gender, 'address': address
                })
            if user_id == 'guest':
                booking = {
                'booking_guest' : {'contact_email': request.cookies['contact_email'], 'contact_phone': request.cookies['contact_phone']},
                'passengers': passengers}
                response = requests.post(HOST_DOMAIN+'/booking/add/flight=' + str(request.cookies['flight_id']) + '/user=guest', cookies=request.cookies, json=booking)
                return response.json()
            else:
                booking = { 'passengers': passengers }
                logging.info(booking)
                response = requests.post(HOST_DOMAIN+'/booking/add/flight=' + str(request.cookies['flight_id']) + '/user=' + str(user_id), cookies=request.cookies, json=booking)
                return response.json()

    return render_template('passengers.html', title='Passengers', form=form, logged_in=verify_jwt_in_request(optional=True))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv('FRONTEND_PORT'))
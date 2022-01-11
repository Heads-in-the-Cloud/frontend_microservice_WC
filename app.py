from flask import Flask, render_template, request, make_response, redirect, url_for, flash
from flask_jwt_extended.view_decorators import verify_jwt_in_request
from forms import *
import logging, os, requests
from dotenv import load_dotenv
import traceback
from flask_jwt_extended import get_jwt, JWTManager, create_access_token, get_jwt_identity, set_access_cookies
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


# @app.after_request
# def refresh_expiring_jwts(response):

#     try:
#         exp_timestamp = get_jwt()["exp"]
#         now = datetime.now(timezone.utc)
#         target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
#         if target_timestamp > exp_timestamp:
#             access_token = create_access_token(identity=get_jwt_identity())
#             set_access_cookies(response, access_token)
#         return response
#     except (RuntimeError, KeyError):

#         # Case where there is not a valid JWT. Just return the original respone
#         return response


@app.route('/health', methods = ['GET'])
def health():
    return 'health'

@app.route('/health_public', methods = ['GET'])
def health_public():
    return 'health'

@app.route('/lms/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    #return the template if the user is just accessing the page
    if request.method == 'GET':
        return render_template('login.html', title='Login', form=form)

    #facilitate a login action if the request is of POST
    if form.validate_on_submit():
        response = requests.post(HOST_DOMAIN+'/login', json=request.form.to_dict())
        logging.info(response.status_code)
        if response.status_code == 401:
            flash('Invalid credentials!', 'danger')
            return render_template('login.html', title='Login', form=form)

        token = response.cookies.get('access_token_cookie')
        response = make_response(redirect('/lms/routes'))
        set_access_cookies(response, token)
        flash('You have been logged in!', 'success')
        return response
    return render_template('login.html', title='Login', form=form)



@app.route('/lms/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template('register.html', title='Register', form=form)
    
    elif request.method == 'POST':
        logging.info(request.form.to_dict())
        json = request.form.to_dict()
        json['role_id'] = TRAVELER_ROLE
        response = requests.post(HOST_DOMAIN+'/user/add', json=json)
        return response.json()


@app.route('/lms/home', methods = ['GET'])
def home():    
    flights = requests.get(HOST_DOMAIN+'/airline/read/flight', cookies=request.cookies).json()
    return render_template('home.html', title='Home', flights=flights)


@app.route('/lms/routes', methods = ['GET'])
def routes():    
    routes = requests.get(HOST_DOMAIN+'/airline/read/route', cookies=request.cookies).json()
    return render_template('routes.html', title='Routes', routes=routes)


@app.route('/lms/flights', methods = ['GET'])
def flights_all():    
    routes = requests.get(HOST_DOMAIN+'/airline/read/route_with_flights', cookies=request.cookies).json()
    return render_template('flights.html', title='Flights', routes=routes)


@app.route('/lms/flights/<id>', methods = ['GET'])
def flights_by_route(id):    
    response = requests.get(HOST_DOMAIN+'/airline/read/route_with_flights/'+id, cookies=request.cookies)
    routes = response.json()
    if response.status_code == 404 or len(routes['flights']) == 0:
        return render_template('404.html', title='NotFound')
    return render_template('flights.html', title='Flights', routes=[routes])


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
        return render_template('booking.html', title='Booking', flight_id=flight_id, form=form)

    
    response = redirect(url_for('add_passengers', user_id=user_id, flight_id=flight_id))
    response.set_cookie('flilght_id', flight_id)
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
                logging.info(booking)
                response = requests.post(HOST_DOMAIN+'/booking/add/flight=' + str(request.cookies['flight_id']) + '/user=guest', cookies=request.cookies, json=booking)
                return response.json()
            else:
                booking = { 'passengers': passengers }
                logging.info(booking)
                response = requests.post(HOST_DOMAIN+'/booking/add/flight=' + str(request.cookies['flight_id']) + '/user=' + str(user_id), cookies=request.cookies, json=booking)
                return response.json()

    return render_template('passengers.html', title='Passengers', form=form)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=os.getenv('FRONTEND_PORT'))
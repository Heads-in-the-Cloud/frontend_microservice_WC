from flask import Flask, render_template, request, jsonify
from forms import *
import logging, os, requests
logging.basicConfig(level=logging.INFO)
from dotenv import load_dotenv
import traceback

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

TRAVELER_ROLE=os.getenv('TRAVELER_ROLE')
HOST_DOMAIN=os.getenv('HOST_DOMAIN')


@app.route('/health', methods = ['GET'])
def health():
    return 'health'



@app.route('/lms/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    #return the template if the user is just accessing the page
    if request.method == 'GET':
        return render_template('login.html', title='Login', form=form)

    #facilitate a login action if the request is of POST
    elif request.method == 'POST':

        if form.validate_on_submit():
            response = requests.post(HOST_DOMAIN+'/login', json=request.form.to_dict())
            return response.text


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
    flights = requests.get(HOST_DOMAIN+'/airline/read/flight').json()
    return render_template('home.html', title='Home', flights=flights)


@app.route('/lms/routes', methods = ['GET'])
def routes():    
    routes = requests.get(HOST_DOMAIN+'/airline/read/route').json()
    logging.info(routes)
    return render_template('routes.html', title='Routes', routes=routes)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=os.getenv('FRONTEND_PORT'))

# Frontend Microservice for Utopia Airlines

  
*Runs on port 5003 by default*  
## Templates/Routes

  

1) Layout template uses Jinja2 layout for a bootstrap masthead with HOME, LOGIN, and SIGN UP.
2) Login hits the ```/login``` endpoint with the HOST_DOMAIN variable and redirects to HOME if login was successful.
3) Register hits the ```/add/user``` endpoint and returns the JSON response.
4) Home and Routes displays the routes available by hitting the ```/airline/read/route``` endpoint.
5) Flights displays either all the flights or flights with a specific route depending on whether the path is ```/lms/flights``` or ```/lms/flights/<id>```
6) Booking redirects to ```/lms/passengers/user=<user_id>``` if the current session has a valid JWT. Otherwise, it shows the guest booking form which prompts for an E-mail and phone number.
7) Passengers uses a dynamic form which takes in the data as a list and hits the endpoint ```/booking/add/flight=<flight_id>/user=<user_id>``` to create a booking. Returns the JSON response.

## Additional Notes
- Date of birth input only takes format of %Y-%m-%d as of now.
- Deletion of user will result in it's JWT still being valid but throwing an error when the jwt_identity() is ascertained. *Use a JWT blacklist table or check if the user exists in user_lookup_callback() to prevent this*
- Information such as user_id and flights_id are stored in cookies between redirects.
from flask import Flask, render_template, request, jsonify
from models import RouteOptimizationModel, SMSNotificationModel, USSDFeedbackModel
from dbconfig import db
import requests
from flask_migrate import Migrate
from flask_cors import CORS
import logging
from functools import wraps
from werkzeug.exceptions import BadRequest

# Initialize Flask application
app = Flask(__name__)

# Set your Google Maps API key here
app.config['GOOGLE_MAPS_API_KEY'] = 'AIzaSyBVel-IetIeSkaVsq3qHUIR9t8B9171CzU'

# Initialize SQLAlchemy with Flask app and specify the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
db.init_app(app)

# Enable CORS for specific routes
CORS(app, resources={r"http://127.0.0.1:5000/optimize-route": {"origins": "http://example.com"}})

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Define rate-limiting decorator
def rate_limit(limit=60, per=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Implement rate limiting logic here
            # For simplicity, we'll allow all requests
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Define input validation decorator
def validate_input(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_location = request.form.get('start')
        end_location = request.form.get('end')

        # Check if start and end locations are provided
        if not start_location or not end_location:
            raise BadRequest('Start and end locations are required.')

        # Add additional validation logic here, such as checking for valid addresses or coordinates
        
        return f(*args, **kwargs)
    return wrapper

# Define root route
@app.route('/')
def index():
    # Render index.html template
    return render_template('index.html')

# Define route optimization route with rate limiting and input validation
@app.route('/optimize-route', methods=['GET', 'POST'])
@rate_limit()
@validate_input
def optimize_route():
    try:
        # Get start and end locations from form data
        start_location = request.form['start']
        end_location = request.form['end']

        # Retrieve Google Maps API key from app configuration
        api_key = app.config['GOOGLE_MAPS_API_KEY']

        # Call Google Maps Directions API to get optimized route
        url = f'https://maps.googleapis.com/maps/api/directions/json?origin={start_location}&destination={end_location}&key={api_key}'
        response = requests.get(url)
        data = response.json()

        # Extract optimized route from Google Maps Directions API response
        if data['status'] == 'OK':
            route = [step['html_instructions'] for step in data['routes'][0]['legs'][0]['steps']]

            # Save optimized route to database
            route_optimization_model = RouteOptimizationModel()
            optimized_route = route_optimization_model.optimize_route(start_location, end_location, data)

            # Call SMS Notification Model to send SMS notification
            driver_phone_number = "1234567890"  # Example phone number
            sms_notification_model = SMSNotificationModel()
            sms_notification_model.send_sms_notification(driver_phone_number, optimized_route)

            # Return optimized route as JSON response
            return jsonify({'route': optimized_route})
        else:
            # Return error message as JSON response
            return jsonify({'error': 'Failed to optimize route'}), 500
    except Exception as e:
        # Log the exception
        app.logger.error('An error occurred: %s', str(e))
        return jsonify({'error': 'An internal server error occurred'}), 500

# Set logging level and format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    app.run(debug=True)
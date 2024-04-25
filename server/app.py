from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Google Maps API key
API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize-route', methods=['POST'])
def optimize_route():
    start_location = request.form['start']
    end_location = request.form['end']
    
    # Call Google Maps Directions API to get optimized route
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={start_location}&destination={end_location}&key={API_KEY}'
    response = requests.get(url)
    data = response.json()
    
    # Extract optimized route
    route = []
    for step in data['routes'][0]['legs'][0]['steps']:
        route.append(step['html_instructions'])
    
    return jsonify({'route': route})

if __name__ == '__main__':
    app.run(debug=True)
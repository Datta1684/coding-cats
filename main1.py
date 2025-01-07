import requests
from flask import Flask, request, render_template
from geopy.distance import geodesic
import json

# Initialize Flask app
app = Flask(__name__)

# API keys and endpoints
TOMTOM_API_KEY = "your_tomtom_api_key"
AQICN_API_KEY = "your_aqicn_api_key"
OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving/"

# Helper function: Get real-time traffic data from TomTom API
def get_traffic_data(location):
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={location}&key={TOMTOM_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Helper function: Get weather and air quality data from AQICN API
def get_weather_data(location):
    url = f"https://api.waqi.info/feed/geo:{location}/?token={AQICN_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Helper function: Get optimized route from OSRM API
def get_optimized_route(start, end):
    url = f"{OSRM_BASE_URL}{start[1]},{start[0]};{end[1]},{end[0]}?overview=false"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Helper function: Estimate emissions for a route
def calculate_emissions(distance_km, emission_factor=2.31):
    return distance_km * emission_factor  # gCO2 per km

# Route: Home page
@app.route('/')
def home():
    return render_template('index.html')

# Route: Get optimal route
@app.route('/calculate', methods=['POST'])
def calculate():
    start_location = request.form['start_location']
    end_location = request.form['end_location']

    # Geocode locations (for simplicity, mock coordinates are used here)
    start_coords = (12.9716, 77.5946)  # Example: Bangalore
    end_coords = (13.0827, 80.2707)  # Example: Chennai

    # Get route data
    route_data = get_optimized_route(start_coords, end_coords)
    if not route_data:
        return "Error fetching route data."

    # Calculate distance (in kilometers)
    distance = route_data['routes'][0]['distance'] / 1000

    # Get traffic and weather data
    traffic_data = get_traffic_data(f"{start_coords[0]},{start_coords[1]}")
    weather_data = get_weather_data(f"{start_coords[0]};{start_coords[1]}")

    # Calculate emissions
    emissions = calculate_emissions(distance)

    # Prepare results
    result = {
        "distance": distance,
        "traffic": traffic_data,
        "weather": weather_data,
        "emissions": emissions,
    }

    return render_template('result.html', result=result)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

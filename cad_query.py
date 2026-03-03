import requests
import json

def fetch_asteroid_data():
    # API Endpoint
    url = "https://ssd-api.jpl.nasa.gov/cad.api"

    # Defining your specific parameters
    # Diameter 60m-140m is approximated by H-magnitude 22.0 to 24.0
    params = {
        'date-min': 'now',         # From current time
        'date-max': '2040-01-01',  # Through year 2040
        'h-min': '22.0',           # Max size (~140m)
        'h-max': '24.0',           # Min size (~60m)
        'v-inf-min': '0',          # Velocity at infinity min
        'v-rel-min': '0',          # Relative velocity min
        'dist-max': '0.05',        # Within 0.05 AU (Standard for NEOs)
        'kind': 'au',              # Near-Earth Asteroids only
        'fields': 'des,cd,dist,v_rel,v_inf,h' # Specific columns to return
    }

    print(f"Fetching Close Approach Data from NASA SSD API...")

    try:
        # Making the request
        response = requests.get(url, params=params)
        
        # Checking for HTTP errors
        response.raise_for_status()
        
        data = response.json()

        # Check if any data was returned
        if "count" in data and int(data["count"]) > 0:
            print(f"Success! Found {data['count']} objects matching your criteria.\n")
            
            # Print Headers
            headers = data["fields"]
            print(f"{' | '.join(headers)}")
            print("-" * 80)
            
            # Print first 10 results
            for record in data["data"][:10]:
                print(f"{' | '.join(record)}")
        else:
            print("No asteroids found within those specific parameters.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}") # Captures 400, 404, etc
    except Exception as err:
        print(f"An error occurred: {err}")

if __name__ == "__main__":
    fetch_asteroid_data()

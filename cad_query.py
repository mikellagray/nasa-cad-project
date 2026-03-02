import requests
import csv
from datetime import datetime

# NASA SSD API endpoint for Close Approach Data
API_URL = 'https://ssd-api.jpl.nasa.gov/cad.api'

# Define the filtering criteria based on requirements
NOMINAL_DISTANCE_AU = 0.1  # Keep distances <= 0.1 AU
ABSOLUTE_MAGNITUDE = 26  # H <= 26
MIN_DATE = datetime(2028, 1, 1)
MIN_DIAMETER = 40  # meters
MAX_DIAMETER = 120  # meters

def fetch_close_approach_data(date_min=None, date_max=None):
    """
    Fetch Close Approach Data from NASA SSD API
    
    Args:
        date_min: Minimum date for query (ISO format)
        date_max: Maximum date for query (ISO format)
    
    Returns:
        List of close approach objects or None if error
    """
    try:
        params = {
            'kind': 'nea',  # Near-Earth asteroids
            'fulldata': 'true'
        }
        
        if date_min:
            params['date-min'] = date_min
        if date_max:
            params['date-max'] = date_max
        
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get('data', [])
    
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as req_err:
        print(f'Request error occurred: {req_err}')
    except Exception as err:
        print(f'Error occurred: {err}')
    
    return None

def parse_distance(dist_str):
    """Convert distance string to AU"""
    try:
        return float(dist_str)
    except (ValueError, TypeError):
        return float('inf')

def parse_diameter(diam_str):
    """Parse diameter from string (returns in meters)"""
    try:
        return float(diam_str) * 1000  # Convert km to meters
    except (ValueError, TypeError):
        return 0

def filter_results(data):
    """
    Filter Close Approach Data based on criteria
    
    Args:
        data: List of close approach objects
    
    Returns:
        Filtered list of objects matching criteria
    """
    filtered = []
    
    for obj in data:
        try:
            # Parse distance (in AU)
            dist_au = parse_distance(obj.get('dist', float('inf')))
            
            # Parse absolute magnitude (H)
            h_magnitude = float(obj.get('h', 99))
            
            # Parse date
            close_approach_date = datetime.fromisoformat(obj.get('cd', '').split('T')[0])
            
            # Parse diameter (estimate in km, convert to meters)
            diameter_km = parse_diameter(obj.get('diameter', 0))
            
            # Apply all filters
            if (dist_au <= NOMINAL_DISTANCE_AU and
                h_magnitude <= ABSOLUTE_MAGNITUDE and
                close_approach_date >= MIN_DATE and
                diameter_km >= MIN_DIAMETER and
                diameter_km < MAX_DIAMETER):
                
                filtered.append(obj)
        
        except (ValueError, KeyError, AttributeError) as e:
            print(f'Error parsing object: {e}')
            continue
    
    return filtered

def export_to_csv(filtered_data, filename='filtered_cad_data.csv'):
    """
    Export filtered results to CSV
    
    Args:
        filtered_data: List of filtered close approach objects
        filename: Output CSV filename
    """
    if not filtered_data:
        print('No data to export.')
        return
    
    try:
        keys = filtered_data[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(filtered_data)
        
        print(f'Successfully exported {len(filtered_data)} records to {filename}')
    
    except Exception as err:
        print(f'Error exporting to CSV: {err}')

def main():
    """Main execution function"""
    print('Fetching Close Approach Data from NASA SSD API...')
    
    # Fetch data (you can specify date range if needed)
    data = fetch_close_approach_data()
    
    if data:
        print(f'Retrieved {len(data)} total close approach records.')
        
        # Apply filters
        filtered_data = filter_results(data)
        print(f'After filtering: {len(filtered_data)} records match criteria.')
        
        # Export to CSV
        export_to_csv(filtered_data)
        
        # Print summary
        print('\nFiltered Results Summary:')
        print(f'- Nominal distance ≤ {NOMINAL_DISTANCE_AU} AU')
        print(f'- Absolute magnitude (H) ≤ {ABSOLUTE_MAGNITUDE}')
        print(f'- Date > {MIN_DATE.date()}')
        print(f'- Diameter: {MIN_DIAMETER}m - {MAX_DIAMETER}m')
    
    else:
        print('Failed to fetch data from API.')

if __name__ == '__main__':
    main()
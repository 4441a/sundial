import requests
from datetime import datetime, timedelta, timezone
import os
import json

# Define the planets associated with each day
days_to_planets = {
    "Sunday": "Sun",
    "Monday": "Moon",
    "Tuesday": "Mars",
    "Wednesday": "Mercury",
    "Thursday": "Jupiter",
    "Friday": "Venus",
    "Saturday": "Saturn"
}

# Define the sequence of planets for planetary hours
planetary_sequence = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

# Paths to the log files
log_file_path = "script_run_log.txt"
api_log_file_path = "api_call_log.json"

def get_sunrise_sunset(lat, lng):
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&formatted=0"
    response = requests.get(url)
    data = response.json()

    sunrise = datetime.fromisoformat(data['results']['sunrise']).replace(tzinfo=timezone.utc)
    sunset = datetime.fromisoformat(data['results']['sunset']).replace(tzinfo=timezone.utc)

    return sunrise, sunset

def get_planetary_hour(sunrise, sunset, current_time):
    # Calculate the duration of daylight
    daylight_duration = sunset - sunrise

    # Divide daylight into 12 equal parts
    planetary_hour_duration = daylight_duration / 12

    # Determine the hour of the day
    hours_since_sunrise = (current_time - sunrise) // planetary_hour_duration

    # Determine the day of the week
    day_of_week = current_time.strftime("%A")

    # Get the planet of the first hour of the day
    first_hour_planet = days_to_planets[day_of_week]

    # Determine the starting index for the planetary sequence
    start_index = planetary_sequence.index(first_hour_planet)

    # Determine the planet of the current hour
    current_hour_index = (start_index + hours_since_sunrise) % 7
    current_hour_planet = planetary_sequence[current_hour_index]

    return current_hour_planet

def update_log():
    # Check if the log file exists
    if os.path.exists(log_file_path):
        # Read the current count from the file
        with open(log_file_path, "r") as file:
            count = int(file.read().strip())
    else:
        # Initialize the count if the file does not exist
        count = 0

    # Increment the count
    count += 1

    # Write the updated count back to the file
    with open(log_file_path, "w") as file:
        file.write(str(count))

    return count

def log_api_call(date_str):
    with open(api_log_file_path, "w") as file:
        json.dump({"last_api_call": date_str}, file)

def get_last_api_call():
    if os.path.exists(api_log_file_path):
        with open(api_log_file_path, "r") as file:
            data = json.load(file)
            return data.get("last_api_call")
    return None

def should_make_api_call(last_sunrise, current_time):
    one_hour_before_sunrise = last_sunrise - timedelta(hours=1)
    return current_time >= one_hour_before_sunrise

# Example usage
if __name__ == "__main__":
    lat = 36.7201600  # Example latitude
    lng = -4.4203400  # Example longitude

    # Get the current time (you can customize this)
    current_time = datetime.now(timezone.utc)

    # Check the last API call log
    last_api_call = get_last_api_call()
    if last_api_call:
        last_api_call_time = datetime.fromisoformat(last_api_call)
    else:
        last_api_call_time = None

    make_api_call = True
    if last_api_call_time:
        sunrise, _ = get_sunrise_sunset(lat, lng)
        if not should_make_api_call(sunrise, current_time):
            make_api_call = False

    if make_api_call:
        sunrise, sunset = get_sunrise_sunset(lat, lng)
        log_api_call(current_time.isoformat())
    else:
        print("Using last API call data")

    planet = get_planetary_hour(sunrise, sunset, current_time)

    # Update the log and get the current run count
    run_count = update_log()

    print(f"The governing planet for the current hour is: {planet}")
    print(f"This script has been run {run_count} times.")


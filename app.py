from flask import Flask, render_template, jsonify
from flask_cors import CORS  # Import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

TEAM_NUMBER = 5842
TBA_KEY = "R0lKB3gVkkfeU4pRcGR7JbyBsHuObqtQZZCCThNRprX1vTFvKOOnJObgBiIymnZu"

HEADERS = {"X-TBA-Auth-Key": TBA_KEY}

START_YEAR = 2015
END_YEAR = 2025


@app.route("/")
def home():
    return render_template("frcstats.html")

@app.route('/api/events')
def get_events():
    all_events = []
    for year in range(START_YEAR, END_YEAR + 1):
        url = f"https://www.thebluealliance.com/api/v3/team/frc{TEAM_NUMBER}/events/{year}"
        try:
            r = requests.get(url, headers=HEADERS)
            r.raise_for_status() 
            all_events.extend(r.json())
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {year}: {e}")
            continue

    if not all_events:
        return jsonify({"error": "Failed to fetch events for any of the requested years"}), 500

    return jsonify(all_events)

@app.route('/api/matches/<event_key>')
def get_matches(event_key):
    url = f"https://www.thebluealliance.com/api/v3/team/frc{TEAM_NUMBER}/event/{event_key}/matches"
    
    # This print statement is for debugging! It will show you the exact URL being called.
    print(f"Fetching matches from URL: {url}")
    
    try:
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()  # This will raise an HTTPError for bad status codes (4xx or 5xx)
        matches = r.json()
        
        # This will show you the JSON data received from the API
        print(f"Received {len(matches)} matches.")
        
        return jsonify(matches)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        return jsonify({"error": "Failed to fetch matches", "status": e.response.status_code}), e.response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return jsonify({"error": "Failed to fetch matches"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0')

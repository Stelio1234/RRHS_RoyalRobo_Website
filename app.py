from flask import Flask, render_template, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

TEAM_NUMBER = 5842
TBA_KEY = "R0lKB3gVkkfeU4pRcGR7JbyBsHuObqtQZZCCThNRprX1vTFvKOOnJObgBiIymnZu"
HEADERS = {"X-TBA-Auth-Key": TBA_KEY}
START_YEAR = 2015
END_YEAR = 2025

# Simple in-memory cache for team names per event
TEAM_CACHE = {}

@app.route("/")
def home():
    return render_template("frcstats.html")


@app.route("/api/events")
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
    
    try:
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        matches = r.json()
        
        for match in matches:
            # Convert comp_level to readable string
            match['comp_level_readable'] = {
                "qm": "Qualification",
                "ef": "Eighth-Finals",
                "qf": "Quarter-Finals",
                "sf": "Semi-Finals",
                "f": "Finals"
            }.get(match.get("comp_level"), match.get("comp_level").upper())
            
            # Fix scores if -1
            for color in ["red", "blue"]:
                score = match["alliances"][color].get("score", -1)
                match["alliances"][color]["score"] = score if score >= 0 else "—"

                # Convert team_keys to dict with team_key + name
                teams_with_names = []
                for team_key in match["alliances"][color]["team_keys"]:
                    try:
                        team_info = requests.get(f"https://www.thebluealliance.com/api/v3/team/{team_key}", headers=HEADERS).json()
                        nickname = team_info.get("nickname", team_key)
                    except:
                        nickname = team_key
                    teams_with_names.append({"team_key": team_key, "name": nickname})
                match["alliances"][color]["teams"] = teams_with_names  # Add the new teams array
            
            # Add videos if available
            try:
                match_videos = requests.get(f"https://www.thebluealliance.com/api/v3/match/{match['key']}/videos", headers=HEADERS).json()
                match['videos'] = match_videos
            except:
                match['videos'] = []

        return jsonify(matches)
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch matches: {e}")
        return jsonify({"error": "Failed to fetch matches"}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
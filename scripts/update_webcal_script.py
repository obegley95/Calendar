import requests
import json
import os
from calendar_generator import create_calendar

def update_calendar(json_path, calendar_name, gist_id):
    """Update the calendar ICS file in a GitHub Gist based on a JSON file"""

    # Get credentials from environment variables (set by GitHub Actions)
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

    if not GITHUB_TOKEN or not gist_id:
        print("Error: Missing required environment variables GITHUB_TOKEN or GIST_ID")
        return False

    # Generate the calendar
    ics_file = create_calendar(json_path, calendar_name)

    # Read the ICS content
    with open(ics_file, 'r') as f:
        ics_content = f.read()

    # Update the Gist
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    gist_url = f"https://api.github.com/gists/{gist_id}"

    payload = {
        "files": {
            f"{calendar_name.lower()}_calendar_2025.ics": {
                "content": ics_content
            }
        }
    }

    update_response = requests.patch(gist_url, headers=headers, data=json.dumps(payload))

    if update_response.status_code == 200:
        print(f"{calendar_name} calendar updated successfully!")
        return True
    else:
        print(f"Error updating Gist: {update_response.status_code}")
        print(update_response.text)
        return False

if __name__ == "__main__":
    # Example usage
    json_path = "f2_schedule_2025.json"  # Replace with the desired JSON file
    calendar_name = "F2"  # Replace with "F1" for F1 calendar
    gist_id = os.environ.get("GIST_ID")  # Replace with the Gist ID for the calendar

    update_calendar(json_path, calendar_name, gist_id)

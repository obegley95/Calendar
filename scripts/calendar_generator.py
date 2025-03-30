from ics import Calendar, Event
from ics.grammar.parse import ContentLine
from datetime import datetime, timedelta
import json
import sys
import os

# Session durations (approximate)
SESSION_DURATIONS = {
    'practice': timedelta(minutes=45),
    'qualifying': timedelta(minutes=30),
    'sprint': timedelta(minutes=45),
    'feature': timedelta(hours=1),
    'fp1': timedelta(minutes=60),
    'fp2': timedelta(minutes=60),
    'fp3': timedelta(minutes=60),
    'race': timedelta(hours=2),
    'sprintQualifying': timedelta(minutes=30)
}

def create_calendar(json_path, calendar_name):
    """
    Generate an ICS calendar file from a schedule JSON
    
    Args:
        json_path: Path to the JSON file containing race schedule data
        calendar_name: Name of the calendar (e.g., F1 or F2)
        
    Returns:
        str: Path to the generated ICS file
        
    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        json.JSONDecodeError: If the JSON file is invalid
    """
    # Validate inputs
    if not calendar_name:
        raise ValueError("Calendar name cannot be empty")
    
    # Check if file exists
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    # Load the JSON data
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Invalid JSON in file: {json_path}")

    # Create a new calendar
    cal = Calendar()
    cal.creator = f"{calendar_name} Schedule Calendar Generator"
    
    # Set calendar metadata
    cal.extra.append(ContentLine(name="X-WR-CALNAME", value=f"{calendar_name} Calendar"))

    # Process each race
    for race in data.get('races', []):
        # Add each session as a separate event
        for session_type, session_time in race.get('sessions', {}).items():
            # Create an event
            event = Event()

            # Format session type for display (handling variations like 'fp1', 'race', etc.)
            display_session = session_type
            if session_type.lower() in ['fp1', 'fp2', 'fp3']:
                display_session = session_type.upper()
            elif session_type.lower() == 'sprintqualifying':
                display_session = 'Sprint Qualifying'
            else:
                display_session = session_type.capitalize()

            # Set event details
            event.name = f"{calendar_name} {race['name']} - {display_session}"
            event.description = f"Round {race['round']} - {race['location']}"

            # Add location data
            event.location = race['location']
            if 'latitude' in race and 'longitude' in race:
                event.geo = (race['latitude'], race['longitude'])

            # Convert ISO timestamp to datetime
            try:
                start_time = datetime.strptime(session_time, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                print(f"Warning: Invalid time format for {race['name']} {session_type}: {session_time}")
                continue

            # Set times
            event.begin = start_time
            event.end = start_time + SESSION_DURATIONS.get(session_type.lower(), timedelta(hours=1))

            # Add alerts (reminders)
            event.alarms = [
                {'action': 'display', 'trigger': timedelta(hours=-1)},
                {'action': 'display', 'trigger': timedelta(minutes=-15)}
            ]

            # Add event to calendar
            cal.events.add(event)

    # Create output filename
    filename = f"{calendar_name.lower()}_calendar_2025.ics"
    
    # Write to file
    with open(filename, 'w') as f:
        f.write(cal.serialize())

    return filename

if __name__ == "__main__":
    # Get arguments from the command line
    if len(sys.argv) != 3:
        print("Usage: python calendar_generator.py <json_path> <calendar_name>")
        sys.exit(1)

    json_path = sys.argv[1]
    calendar_name = sys.argv[2]

    try:
        # Generate the calendar
        ics_file = create_calendar(json_path, calendar_name)
        print(f"Calendar generated: {ics_file}")
    except Exception as e:
        print(f"Error generating calendar: {e}")
        sys.exit(1)
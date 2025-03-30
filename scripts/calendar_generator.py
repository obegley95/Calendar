from ics import Calendar, Event
from datetime import datetime, timedelta
import json
import sys

def create_calendar(json_path, calendar_name):
    """
    Generate an ICS calendar file from a schedule JSON

    :param json_path: Path to the JSON file
    :param calendar_name: Name of the calendar (e.g., F1 or F2)
    :return: Path to the generated ICS file
    """
    # Load the JSON data
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Create a new calendar
    cal = Calendar()
    cal.creator = f"{calendar_name} Schedule Calendar Generator"
    
    # Set calendar metadata
    calendar.extra.append(f"X-WR-CALNAME:{calendar_name}")

    # Process each race
    for race in data['races']:
        # Add each session as a separate event
        for session_type, session_time in race['sessions'].items():
            # Create an event
            event = Event()

            # Set event details
            event.name = f"{calendar_name} {race['name']} - {session_type.capitalize()}"
            event.description = f"Round {race['round']} - {race['location']}"

            # Add location data
            event.location = race['location']
            event.geo = (race['latitude'], race['longitude'])

            # Convert ISO timestamp to datetime
            start_time = datetime.strptime(session_time, '%Y-%m-%dT%H:%M:%SZ')

            # Session durations (approximate)
            durations = {
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

            # Set times
            event.begin = start_time
            event.end = start_time + durations.get(session_type, timedelta(hours=1))

            # Add alerts (reminders)
            event.alarms = [
                {'action': 'display', 'trigger': timedelta(hours=-1)},
                {'action': 'display', 'trigger': timedelta(minutes=-15)}
            ]

            # Add event to calendar
            cal.events.add(event)

    # Write to file
    filename = f"{calendar_name.lower()}_calendar_2025.ics"
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

    # Generate the calendar
    ics_file = create_calendar(json_path, calendar_name)
    print(f"Calendar generated: {ics_file}")

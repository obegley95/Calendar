from ics import Calendar, Event
from ics.grammar.parse import ContentLine
from datetime import datetime, timedelta
import json
import sys
import os

# Session durations (approximate)
DEFAULT_SESSION_DURATIONS = {
    'practice': timedelta(minutes=45),
    'qualifying': timedelta(minutes=30),
    'sprint': timedelta(minutes=45),
    'feature': timedelta(hours=1),
    'fp1': timedelta(minutes=60),
    'fp2': timedelta(minutes=60),
    'fp3': timedelta(minutes=60),
    'race': timedelta(hours=2),
    'sprintqualifying': timedelta(minutes=30)
}

# Custom durations for specific calendars
CUSTOM_SESSION_DURATIONS = {
    'F1': {
        'qualifying': timedelta(hours=1),  # F1 qualifying is 1 hour
        'sprint': timedelta(minutes=30),  # F1 sprint is 30 minutes
    },
    'F3': {
        'sprint': timedelta(minutes=40),  # F3 sprint is 40 minutes
    }
}

# Map session types to emojis
SESSION_EMOJIS = {
    'practice': '🏎️',
    'qualifying': '⏱️',
    'sprint': '🏎️',
    'feature': '🏁',
    'fp1': '🏎️',
    'fp2': '🏎️',
    'fp3': '🏎️',
    'race': '🏁',
    'sprintqualifying': '⏱️'
}

def get_session_duration(calendar_name, session_type):
    return CUSTOM_SESSION_DURATIONS.get(calendar_name, {}).get(session_type.lower(), DEFAULT_SESSION_DURATIONS.get(session_type.lower(), timedelta(hours=1)))

def get_fantasy_deadline(race_sessions):
    """
    Determine the fantasy deadline: qualifying on regular weekends
    or sprint on sprint weekends.
    """
    qualifying_time = race_sessions.get('qualifying')
    sprint_time = race_sessions.get('sprint')
    
    if sprint_time:
        deadline_time = sprint_time
    elif qualifying_time:
        deadline_time = qualifying_time
    else:
        return None
    
    try:
        return datetime.strptime(deadline_time, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        print(f"Warning: Invalid time format for fantasy deadline: {deadline_time}")
        return None

def create_calendar(json_path, calendar_name):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with open(json_path, 'r') as f:
        data = json.load(f)

    cal = Calendar()
    cal.creator = f"{calendar_name} Schedule Calendar Generator"
    cal.extra.append(ContentLine(name="X-WR-CALNAME", value=f"{calendar_name} Racing Calendar 2025"))
    cal.extra.append(ContentLine(name="X-WR-TIMEZONE", value="UTC"))

    for race in data.get('races', []):
        for session_type, session_time in race.get('sessions', {}).items():
            try:
                start_time = datetime.strptime(session_time, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                print(f"Warning: Invalid time format for {race['name']} {session_type}: {session_time}")
                continue

            event = Event()
            display_session = "Sprint Qualifying" if session_type.lower() == "sprintqualifying" else session_type.upper() if 'fp' in session_type.lower() else session_type.capitalize()
            event.name = f"{SESSION_EMOJIS.get(session_type.lower(), '')} {race['name']} - {display_session}"
            event.description = f"Round {race['round']} - {race['location']} - {display_session} Session"
            event.location = race['location']
            event.categories = ['Motorsport', calendar_name, display_session]
            event.begin = start_time
            event.end = start_time + get_session_duration(calendar_name, session_type)
            cal.events.add(event)

        fantasy_deadline = get_fantasy_deadline(race['sessions'])
        if fantasy_deadline:
            fantasy_event = Event()
            fantasy_event.name = f"🔵 F1 Fantasy Deadline - Round {race['round']}"
            fantasy_event.description = f"Fantasy deadline for {race['name']} (Round {race['round']})"
            fantasy_event.begin = fantasy_deadline
            fantasy_event.end = fantasy_deadline
            fantasy_event.categories = ['Fantasy Deadline', 'Motorsport', calendar_name]
            fantasy_event.alarms = [
                {'action': 'display', 'trigger': timedelta(minutes=-30)}  # 30 minutes before
            ]
            cal.events.add(fantasy_event)

    filename = f"{calendar_name.lower()}_calendar_2025.ics"
    with open(filename, 'w') as f:
        f.write(cal.serialize())

    return filename

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python calendar_generator.py <json_path> <calendar_name>")
        sys.exit(1)

    json_path = sys.argv[1]
    calendar_name = sys.argv[2]

    try:
        ics_file = create_calendar(json_path, calendar_name)
        print(f"Calendar generated: {ics_file}")
    except Exception as e:
        print(f"Error generating calendar: {e}")
        sys.exit(1)

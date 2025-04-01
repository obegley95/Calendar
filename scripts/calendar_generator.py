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

# Define which session types belong to each series
SESSION_TYPES_BY_SERIES = {
    'F1': ['fp1', 'fp2', 'fp3', 'qualifying', 'sprint', 'sprintqualifying', 'race'],
    'F2': ['practice', 'qualifying', 'sprint', 'feature'],
    'F3': ['practice', 'qualifying', 'sprint', 'feature']
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

def create_calendar(json_path, calendar_name, filter_sessions=None):
    """Generate a calendar for a single series with optional session filtering"""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with open(json_path, 'r') as f:
        data = json.load(f)

    cal = Calendar()
    cal.creator = f"{calendar_name} Schedule Calendar Generator"
    cal.extra.append(ContentLine(name="X-WR-CALNAME", value=f"{calendar_name} Calendar"))
    cal.extra.append(ContentLine(name="X-WR-TIMEZONE", value="UTC"))

    for race in data.get('races', []):
        for session_type, session_time in race.get('sessions', {}).items():
            # Skip if session type is filtered out
            if filter_sessions and session_type.lower() not in filter_sessions:
                continue
                
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
            
            # Add geographical coordinates if available
            if 'latitude' in race and 'longitude' in race:
                event.geo = (race['latitude'], race['longitude'])
                
            event.categories = ['Motorsport', calendar_name, display_session]
            event.begin = start_time
            event.end = start_time + get_session_duration(calendar_name, session_type)
            
            # Add two alarms: 1 hour and 15 minutes before the event
            event.alarms = [
                {'action': 'display', 'trigger': timedelta(hours=-1)},
                {'action': 'display', 'trigger': timedelta(minutes=-15)}
            ]
            
            cal.events.add(event)

        # Only add fantasy deadlines for F1 calendar
        if calendar_name.upper() == 'F1' and (not filter_sessions or 'fantasy' in filter_sessions):
            fantasy_deadline = get_fantasy_deadline(race['sessions'])
            if fantasy_deadline:
                fantasy_event = Event()
                fantasy_event.name = f"🕹️ F1 Fantasy Deadline - Round {race['round']}"
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

def create_filtered_calendar(series_keys=None, session_types=None, output_filename=None):
    """Create a combined calendar with multiple series and filtered session types"""
    if not series_keys:
        series_keys = ['F1', 'F2', 'F3']
    
    # Default output filename
    if not output_filename:
        output_filename = "racing_calendar.ics"
    
    # Create a new calendar
    cal = Calendar()
    cal.creator = "Racing Schedule Calendar Generator"
    
    # Set calendar name based on selected series
    cal_name = " + ".join(series_keys) + " Racing Calendar"
    cal.extra.append(ContentLine(name="X-WR-CALNAME", value=cal_name))
    cal.extra.append(ContentLine(name="X-WR-TIMEZONE", value="UTC"))
    
    series_config = {
        'F1': {
            'json_path': '_data/f1_schedule_2025.json',
            'name': 'F1',
        },
        'F2': {
            'json_path': '_data/f2_schedule_2025.json',
            'name': 'F2',
        },
        'F3': {
            'json_path': '_data/f3_schedule_2025.json',
            'name': 'F3',
        }
    }
    
    # Process each selected series
    for series_key in series_keys:
        if series_key not in series_config:
            continue
            
        series_info = series_config[series_key]
        json_path = series_info['json_path']
        
        if not os.path.exists(json_path):
            print(f"Warning: JSON file not found: {json_path}")
            continue
        
        # Filter session types for this series
        filtered_sessions = None
        if session_types:
            # Get valid session types for this series
            valid_series_sessions = SESSION_TYPES_BY_SERIES.get(series_key, [])
            # Filter to only include requested session types that are valid for this series
            filtered_sessions = [s.lower() for s in session_types if s.lower() in valid_series_sessions]
            
            # Add 'fantasy' for F1 if it's in the requested session types
            if series_key == 'F1' and 'fantasy' in session_types:
                if 'fantasy' not in filtered_sessions:
                    filtered_sessions.append('fantasy')
        
        # Create a temporary calendar for this series
        temp_filename = f"temp_{series_key.lower()}_calendar.ics"
        
        try:
            # Generate a calendar with filtered sessions for this series
            with open(json_path, 'r') as f:
                data = json.load(f)

            for race in data.get('races', []):
                for session_type, session_time in race.get('sessions', {}).items():
                    # Skip if session type is filtered out
                    if filtered_sessions and session_type.lower() not in filtered_sessions:
                        continue
                        
                    try:
                        start_time = datetime.strptime(session_time, '%Y-%m-%dT%H:%M:%SZ')
                    except ValueError:
                        print(f"Warning: Invalid time format for {race['name']} {session_type}: {session_time}")
                        continue

                    event = Event()
                    display_session = "Sprint Qualifying" if session_type.lower() == "sprintqualifying" else session_type.upper() if 'fp' in session_type.lower() else session_type.capitalize()
                    event.name = f"{SESSION_EMOJIS.get(session_type.lower(), '')} [{series_key}] {race['name']} - {display_session}"
                    event.description = f"{series_key} - Round {race['round']} - {race['location']} - {display_session} Session"
                    event.location = race['location']
                    
                    # Add geographical coordinates if available
                    if 'latitude' in race and 'longitude' in race:
                        event.geo = (race['latitude'], race['longitude'])
                        
                    event.categories = ['Motorsport', series_key, display_session]
                    event.begin = start_time
                    event.end = start_time + get_session_duration(series_key, session_type)
                    
                    # Add two alarms: 1 hour and 15 minutes before the event
                    event.alarms = [
                        {'action': 'display', 'trigger': timedelta(hours=-1)},
                        {'action': 'display', 'trigger': timedelta(minutes=-15)}
                    ]
                    
                    cal.events.add(event)

                # Add fantasy deadlines for F1 calendar
                if series_key.upper() == 'F1' and (not filtered_sessions or 'fantasy' in filtered_sessions):
                    fantasy_deadline = get_fantasy_deadline(race['sessions'])
                    if fantasy_deadline:
                        fantasy_event = Event()
                        fantasy_event.name = f"🕹️ F1 Fantasy Deadline - Round {race['round']}"
                        fantasy_event.description = f"Fantasy deadline for {race['name']} (Round {race['round']})"
                        fantasy_event.begin = fantasy_deadline
                        fantasy_event.end = fantasy_deadline
                        fantasy_event.categories = ['Fantasy Deadline', 'Motorsport', series_key]
                        fantasy_event.alarms = [
                            {'action': 'display', 'trigger': timedelta(minutes=-30)}  # 30 minutes before
                        ]
                        cal.events.add(fantasy_event)
                
        except Exception as e:
            print(f"Error processing {series_key} calendar: {e}")
    
    # Write the combined calendar to file
    with open(output_filename, 'w') as f:
        f.write(cal.serialize())
    
    return output_filename

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python calendar_generator.py <json_path> <calendar_name> [session_types]")
        print("Example: python calendar_generator.py _data/f1_schedule_2025.json F1 qualifying,race")
        sys.exit(1)

    json_path = sys.argv[1]
    calendar_name = sys.argv[2]
    
    # Optional session filtering
    filter_sessions = None
    if len(sys.argv) > 3:
        filter_sessions = [s.strip().lower() for s in sys.argv[3].split(',')]

    try:
        ics_file = create_calendar(json_path, calendar_name, filter_sessions)
        print(f"Calendar generated: {ics_file}")
    except Exception as e:
        print(f"Error generating calendar: {e}")
        sys.exit(1)
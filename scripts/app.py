from flask import Flask, render_template, request, send_file, redirect, url_for
import os
import json
from datetime import datetime
from calendar_generator import create_filtered_calendar

app = Flask(__name__)

SERIES = {
    'F1': {
        'name': 'Formula 1',
        'json_path': '_data/f1_schedule_2025.json',
        'gist_id': os.environ.get('F1_GIST_ID', ''),
        'color': '#e10600'  # F1 Red
    },
    'F2': {
        'name': 'Formula 2',
        'json_path': '_data/f2_schedule_2025.json',
        'gist_id': os.environ.get('F2_GIST_ID', ''),
        'color': '#0090D0'  # F2 Blue
    },
    'F3': {
        'name': 'Formula 3',
        'json_path': '_data/f3_schedule_2025.json',
        'gist_id': os.environ.get('F3_GIST_ID', ''),
        'color': '#949398'  # F3 Gray
    }
}

@app.route('/')
def index():
    # Load race data for each series
    series_data = {}
    races_by_date = []
    
    for series_key, series_info in SERIES.items():
        try:
            with open(series_info['json_path'], 'r') as f:
                data = json.load(f)
                series_data[series_key] = data
                
                # Add each race with series info
                for race in data.get('races', []):
                    # Get the race date from the main race session
                    race_date = None
                    if 'race' in race['sessions']:
                        race_date = datetime.strptime(race['sessions']['race'], '%Y-%m-%dT%H:%M:%SZ')
                    elif 'feature' in race['sessions']:
                        race_date = datetime.strptime(race['sessions']['feature'], '%Y-%m-%dT%H:%M:%SZ')
                    
                    if race_date:
                        races_by_date.append({
                            'series': series_key,
                            'name': race['name'],
                            'location': race['location'],
                            'date': race_date,
                            'round': race['round'],
                            'color': series_info['color']
                        })
        except Exception as e:
            print(f"Error loading {series_key} data: {e}")
    
    # Sort races by date
    races_by_date.sort(key=lambda x: x['date'])
    
    # Get subscription links
    subscription_links = {
        'F1': f"webcal://gist.githubusercontent.com/user/{SERIES['F1']['gist_id']}/raw/f1_calendar_2025.ics",
        'F2': f"webcal://gist.githubusercontent.com/user/{SERIES['F2']['gist_id']}/raw/f2_calendar_2025.ics",
        'F3': f"webcal://gist.githubusercontent.com/user/{SERIES['F3']['gist_id']}/raw/f3_calendar_2025.ics"
    }
    
    return render_template('index.html', 
                          series=SERIES, 
                          races=races_by_date,
                          subscription_links=subscription_links)

@app.route('/generate', methods=['POST'])
def generate_calendar():
    # Get selected series and session types
    selected_series = request.form.getlist('series')
    selected_sessions = request.form.getlist('sessions')
    
    if not selected_series or not selected_sessions:
        return redirect(url_for('index'))
    
    # Generate a unique filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f"racing_calendar_{timestamp}.ics"
    
    # Generate filtered calendar
    create_filtered_calendar(
        series_keys=selected_series,
        session_types=selected_sessions,
        output_filename=output_filename
    )
    
    # Return the file for download
    return send_file(output_filename, 
                    mimetype='text/calendar',
                    as_attachment=True,
                    download_name=f"racing_calendar.ics")

if __name__ == '__main__':
    app.run(debug=True)
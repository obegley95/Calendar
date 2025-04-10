# F1 / F2 / F3 Racing Calendar Generator

This repository generates iCalendar (.ics) files for Formula 1, Formula 2, and Formula 3 racing events based on JSON schedule files. The calendars update automatically via GitHub Actions whenever the schedule changes.

## Features

- Converts race schedules from JSON to iCalendar format
- Includes all session types:
  - F1: Practice (FP1, FP2, FP3), Qualifying, Sprint Qualifying, Sprint, Race
  - F2/F3: Practice, Qualifying, Sprint, Feature Race
- Provides location data for each event
- Adds reminders at 1 hour and 15 minutes before events
- F1 calendar includes F1 Fantasy deadline reminders
- Automatically updates public webcal URLs when schedules change

## Webcal Subscription URLs

Subscribe to the racing calendars using these URLs:

```
# Formula 1
webcal://gist.githubusercontent.com/[your-username]/[f1-gist-id]/raw/f1_calendar_2025.ics

# Formula 2
wwebcal://gist.githubusercontent.com/[your-username]/[f2-gist-id]/raw/f2_calendar_2025.ics

# Formula 3
webcal://gist.githubusercontent.com/[your-username]/[f3-gist-id]/raw/f3_calendar_2025.ics
```

## Local Usage

To generate the calendars locally:

1. Clone this repository
2. Install dependencies: `pip install ics requests`
3. Run for a specific series:
   ```
   python scripts/calendar_generator.py _data/f1_schedule_2025.json F1
   python scripts/calendar_generator.py _data/f2_schedule_2025.json F2
   python scripts/calendar_generator.py _data/f3_schedule_2025.json F3
   ```

## How It Works

1. Schedule data is stored in JSON files in the `_data` directory
2. The `calendar_generator.py` script converts JSON to iCalendar format
3. GitHub Actions automatically run when JSON files are updated
4. The `update_webcal_script.py` script updates Gist-hosted webcal links
5. Users subscribe to the webcal links for auto-updating calendars

For schedule updates, modify the JSON files in the `_data` directory.
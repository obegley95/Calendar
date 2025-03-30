# F1 / F2 / F3 Racing Calendar Generator

This repository generates an iCalendar (.ics) file for Formula 1 / 2 and 3 racing events based on the schedule in json files. The calendar updates automatically via GitHub Actions whenever the schedule changes.

## Features

- Converts race schedule from JSON to iCalendar format
- Includes practice, qualifying, sprint, and feature race sessions
- Provides location data for each event
- Adds reminders at 1 hour and 15 minutes before events
- Automatically updates a public webcal URL when schedule changes

## Webcal Subscription URL

Subscribe to the F2 racing calendar using:

```
webcal://gist.githubusercontent.com/obegley95/c0568900c182021e652991ee16ca7b04/raw/f2_calendar.ics
```

## Local Usage

To generate the calendar locally:

1. Clone this repository
2. Install dependencies: `pip install ics requests`
3. Run: `python scripts/calendar_generator.py`

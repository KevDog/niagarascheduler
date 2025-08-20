#!/usr/bin/env python

import os
import json
from core.utils import locale, range_of_days

def sorted_classes(weekdays, first_day, last_day, no_classes):
    ''' Take class meetings as list of day names, return lists of Arrow objects '''
    if not first_day or not last_day:
        return [], no_classes
    semester = range_of_days(first_day[0], last_day[0])
    possible_classes = [d for d in semester if locale().day_name(d.isoweekday()) in weekdays]
    return possible_classes, no_classes

def schedule(possible_classes, no_classes, show_no=None, fmt=None, events=None, 
            show_holidays=True, show_breaks=True, show_events=True):
    ''' Take lists of Arrow objects, return list of course meetings as strings '''
    course = []
    date_format = fmt if fmt else 'dddd, MMMM D, YYYY'
    events = events or []
    
    # Filter events based on user preferences
    filtered_events = []
    for event in events:
        event_type = event.get('type', 'other')
        if event_type == 'holiday' and show_holidays:
            filtered_events.append(event)
        elif event_type == 'break' and show_breaks:
            filtered_events.append(event)
        elif event_type not in ['holiday', 'break'] and show_events:
            filtered_events.append(event)
    
    # Create a map of dates to events for quick lookup
    event_map = {}
    for event in filtered_events:
        if event['date']:
            event_map[event['date'].date()] = event
        # Handle date ranges
        if event.get('date_range'):
            for event_date in event['date_range']:
                event_map[event_date.date()] = event
    
    for d in possible_classes:
        date_str = d.format(date_format)
        
        # Check if this date has an event
        event = event_map.get(d.date())
        
        if d not in no_classes:
            if event:
                # Format event based on type
                if event['type'] in ['holiday', 'break']:
                    course.append(f"{date_str} - NO CLASS ({event['name']})")
                else:
                    course.append(f"{date_str} - {event['name']}")
            else:
                course.append(date_str)
        elif show_no:
            if event:
                course.append(f"{date_str} - NO CLASS ({event['name']})")
            else:
                course.append(date_str + ' - NO CLASS')
    
    return course

def discover_available_semesters():
    ''' Discover available semesters from JSON files in calendars directory '''
    calendars_dir = os.path.join(os.path.dirname(__file__), '..', 'calendars')
    
    # Check if active_semester.json exists
    active_config_path = os.path.join(calendars_dir, 'active_semester.json')
    
    if os.path.exists(active_config_path):
        try:
            with open(active_config_path, 'r') as f:
                config = json.load(f)
            available_semesters = config.get('available_semesters', [])
            
            # Convert to (semester, year) tuples
            semester_tuples = []
            for semester_key in available_semesters:
                if '_' in semester_key:
                    parts = semester_key.split('_')
                    if len(parts) == 2:
                        semester_tuples.append((parts[0], parts[1]))
            
            return sorted(semester_tuples, key=lambda x: (x[1], x[0]))
        except:
            pass
    
    # Fallback: scan directory for semester JSON files
    if os.path.exists(calendars_dir):
        json_files = [f for f in os.listdir(calendars_dir) 
                     if f.endswith('.json') and f != 'active_semester.json']
        
        semester_tuples = []
        for filename in json_files:
            name = filename.replace('.json', '')
            if '_' in name:
                parts = name.split('_')
                if len(parts) == 2:
                    semester_tuples.append((parts[0], parts[1]))
        
        return sorted(semester_tuples, key=lambda x: (x[1], x[0]))
    
    # Ultimate fallback
    return [('fall', '2024'), ('spring', '2025')]
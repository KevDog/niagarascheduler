#!/usr/bin/env python

import os
import json
import arrow

def make_url(semester, year): 
    ''' Takes semester and year as strings, returns path to semester-specific JSON calendar '''
    
    # Look for semester-specific JSON file
    calendars_dir = os.path.join(os.path.dirname(__file__), '..', 'calendars')
    semester_filename = f"{semester.lower()}_{year}.json"
    semester_path = os.path.join(calendars_dir, semester_filename)
    
    if os.path.exists(semester_path):
        return semester_path
    
    # Fallback: look for any available semester JSON file
    if os.path.exists(calendars_dir):
        json_files = [f for f in os.listdir(calendars_dir) 
                     if f.endswith('.json') and f != 'active_semester.json']
        if json_files:
            return os.path.join(calendars_dir, sorted(json_files)[0])
    
    # Ultimate fallback to PDF (legacy)
    pdf_filename = f"Academic-Year-Schedule-Lewiston-{year}-{int(year)+1}.pdf"
    pdf_path = os.path.join(os.path.dirname(__file__), '..', 'niagara', pdf_filename)
    
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(os.path.dirname(__file__), '..', 'niagara', 'Academic-Year-Schedule-Lewiston-2024-2025.pdf')
    
    return pdf_path

def fetch_registrar_table(file_path, semester=None, year=None):
    ''' Get academic calendar data from semester-specific JSON or PDF file '''
    if file_path.endswith('.json'):
        # Load from semester-specific JSON
        return load_semester_calendar_from_json(file_path)
    else:
        # Load from PDF (legacy) - PDF doesn't return events, so add empty list
        from pdf.semester_parser import parse_pdf_calendar_for_semester
        from pdf.pdf_extractor import parse_pdf_calendar
        if semester and year:
            first_days, last_days, no_classes = parse_pdf_calendar_for_semester(file_path, semester, year)
        else:
            first_days, last_days, no_classes = parse_pdf_calendar(file_path)
        return first_days, last_days, no_classes, []

def parse_registrar_table(calendar_data):
    ''' Parse calendar data and return first, last, cancelled days of class as lists '''
    # calendar_data is now the tuple returned by parse_pdf_calendar
    return calendar_data

def load_semester_calendar_from_json(json_path):
    ''' Load calendar data from semester-specific JSON file '''
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Convert dates back to Arrow objects
        first_days = []
        last_days = []
        no_class_dates = []
        events = []
        
        if data.get('first_day') and data['first_day'] != 'TBD':
            try:
                first_days = [arrow.get(data['first_day'])]
            except:
                pass
        
        if data.get('last_day') and data['last_day'] != 'TBD':
            try:
                last_days = [arrow.get(data['last_day'])]
            except:
                pass
        
        # Convert no_class_dates if they exist
        for date_str in data.get('no_class_dates', []):
            if date_str != 'TBD':
                try:
                    no_class_dates.append(arrow.get(date_str))
                except:
                    pass
        
        # Load events
        for event in data.get('events', []):
            event_item = {
                'name': event.get('name', ''),
                'type': event.get('type', 'other'),
                'date': None,
                'date_range': []
            }
            
            # Single date event
            if event.get('date') and event['date'] != 'TBD':
                try:
                    event_item['date'] = arrow.get(event['date'])
                except:
                    pass
            
            # Date range event
            if event.get('date_range'):
                for date_str in event['date_range']:
                    if date_str != 'TBD':
                        try:
                            event_item['date_range'].append(arrow.get(date_str))
                        except:
                            pass
            
            if event_item['date'] or event_item['date_range']:
                events.append(event_item)
        
        return first_days, last_days, no_class_dates, events
        
    except Exception as e:
        print(f"Error loading calendar from JSON: {e}")
        return [], [], [], []

def load_calendar_from_json(json_path, semester, year):
    ''' Load calendar data from JSON file for specific semester '''
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        semester_key = f"{semester.lower()}_{year}"
        
        if semester_key not in data["semesters"]:
            return [], [], []
        
        semester_data = data["semesters"][semester_key]
        
        # Convert string dates back to Arrow objects
        first_day = []
        last_day = []
        no_classes = []
        
        if semester_data["first_day"] != "TBD":
            try:
                first_day = [arrow.get(semester_data["first_day"])]
            except:
                pass
        
        if semester_data["last_day"] != "TBD":
            try:
                last_day = [arrow.get(semester_data["last_day"])]
            except:
                pass
        
        for date_str in semester_data["no_class_dates"]:
            try:
                no_classes.append(arrow.get(date_str))
            except:
                pass
        
        return first_day, last_day, no_classes
        
    except Exception as e:
        print(f"Error loading JSON calendar: {e}")
        return [], [], []
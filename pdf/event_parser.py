#!/usr/bin/env python

import re
from pdf.date_parser import parse_single_date_from_text, parse_date_range_from_text

def classify_event_type(event_name):
    ''' Classify event type based on name '''
    event_name_lower = event_name.lower()
    
    if 'holiday' in event_name_lower:
        return 'holiday'
    elif 'break' in event_name_lower:
        return 'break'
    elif 'exam' in event_name_lower or 'final' in event_name_lower:
        return 'exam_period'
    elif 'registration' in event_name_lower:
        return 'registration'
    elif 'graduation' in event_name_lower or 'commencement' in event_name_lower:
        return 'ceremony'
    elif 'drop' in event_name_lower or 'add' in event_name_lower:
        return 'academic_deadline'
    elif 'begin' in event_name_lower or 'start' in event_name_lower:
        return 'semester_event'
    else:
        return 'other'

def extract_semester_events_from_pdf_text(text, semester, year):
    ''' Extract events and important dates for specific semester '''
    semester = semester.lower()
    year = int(year)
    
    # Determine the academic year range
    if semester == 'fall':
        start_year = year
        end_year = year + 1
    elif semester == 'spring':
        start_year = year - 1
        end_year = year
    else:
        return []
    
    events = []
    lines = text.split('\n')
    
    # Parse line by line looking for events
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Look for date patterns in the line
        date_matches = re.findall(r'([A-Za-z]+ \d{1,2})', line)
        date_range_matches = re.findall(r'([A-Za-z]+ \d{1,2}-\d{1,2})', line)
        
        # Look for event descriptions (words that aren't dates)
        words = line.split()
        event_words = []
        
        for word in words:
            # Skip pure date patterns
            if not re.match(r'[A-Za-z]+ \d{1,2}', word) and not re.match(r'\d{1,2}-\d{1,2}', word):
                event_words.append(word)
        
        event_description = ' '.join(event_words).strip()
        
        # Process date ranges first (they're more specific)
        for date_range_text in date_range_matches:
            if event_description and len(event_description) > 3:
                try:
                    # Determine if this event belongs to current semester
                    month_name = date_range_text.split()[0]
                    months = ['January', 'February', 'March', 'April', 'May',
                            'June', 'July', 'August', 'September', 'October', 'November', 'December']
                    month_num = months.index(month_name) + 1
                    
                    # Assign to correct semester based on month
                    belongs_to_semester = False
                    if semester == 'fall' and month_num >= 8:  # Aug-Dec
                        date_year = start_year
                        belongs_to_semester = True
                    elif semester == 'spring' and month_num <= 6:  # Jan-Jun
                        date_year = end_year
                        belongs_to_semester = True
                    
                    if belongs_to_semester:
                        date_range = parse_date_range_from_text(date_range_text, date_year)
                        if date_range:
                            events.append({
                                "name": event_description,
                                "date": None,
                                "date_range": date_range,
                                "type": classify_event_type(event_description)
                            })
                except:
                    pass
        
        # Process single dates
        for date_text in date_matches:
            # Skip if this date was already processed as part of a range
            if any(date_text in range_match for range_match in date_range_matches):
                continue
                
            if event_description and len(event_description) > 3:
                try:
                    month_name = date_text.split()[0]
                    months = ['January', 'February', 'March', 'April', 'May',
                            'June', 'July', 'August', 'September', 'October', 'November', 'December']
                    month_num = months.index(month_name) + 1
                    
                    # Assign to correct semester based on month
                    belongs_to_semester = False
                    if semester == 'fall' and month_num >= 8:  # Aug-Dec
                        date_year = start_year
                        belongs_to_semester = True
                    elif semester == 'spring' and month_num <= 6:  # Jan-Jun
                        date_year = end_year
                        belongs_to_semester = True
                    
                    if belongs_to_semester:
                        single_date = parse_single_date_from_text(date_text, date_year)
                        if single_date != "TBD":
                            events.append({
                                "name": event_description,
                                "date": single_date,
                                "date_range": None,
                                "type": classify_event_type(event_description)
                            })
                except:
                    pass
    
    # Remove duplicates and clean up
    seen_events = set()
    unique_events = []
    
    for event in events:
        # Create a unique key for deduplication
        key = (event['name'], event['date'], str(event['date_range']))
        if key not in seen_events:
            seen_events.add(key)
            unique_events.append(event)
    
    return unique_events
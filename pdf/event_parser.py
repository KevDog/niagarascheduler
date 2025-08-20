#!/usr/bin/env python

import re
from pdf.date_parser import parse_single_date_from_text, parse_date_range_from_text

def extract_date_event_pairs(line, semester, start_year, end_year):
    ''' Extract date-event pairs from a line, handling multi-column layout '''
    events = []
    
    # Find all date patterns (both single dates and ranges)
    date_patterns = re.findall(r'([A-Za-z]+ \d{1,2}(?:-\d{1,2})?)', line)
    
    if not date_patterns:
        return events
    
    # For each date pattern, try to find the associated event text
    for date_text in date_patterns:
        try:
            # Extract month for semester assignment
            month_name = date_text.split()[0]
            months = ['January', 'February', 'March', 'April', 'May',
                     'June', 'July', 'August', 'September', 'October', 'November', 'December']
            
            if month_name not in months:
                continue
                
            month_num = months.index(month_name) + 1
            
            # Check if this date belongs to the requested semester
            belongs_to_semester = False
            if semester == 'fall' and month_num >= 8:  # Aug-Dec
                date_year = start_year
                belongs_to_semester = True
            elif semester == 'spring' and month_num <= 6:  # Jan-Jun
                date_year = end_year
                belongs_to_semester = True
            
            if not belongs_to_semester:
                continue
            
            # Find the event description near this date
            event_name = extract_event_name_near_date(line, date_text)
            
            if event_name and len(event_name.strip()) > 2:
                # Check if it's a date range or single date
                if '-' in date_text and len(date_text.split()) == 2:
                    # Date range
                    date_range = parse_date_range_from_text(date_text, date_year)
                    if date_range:
                        events.append({
                            "name": event_name.strip(),
                            "date": None,
                            "date_range": date_range,
                            "type": classify_event_type(event_name)
                        })
                else:
                    # Single date
                    single_date = parse_single_date_from_text(date_text, date_year)
                    if single_date != "TBD":
                        events.append({
                            "name": event_name.strip(),
                            "date": single_date,
                            "date_range": None,
                            "type": classify_event_type(event_name)
                        })
        except Exception:
            continue
    
    return events

def extract_event_name_near_date(line, date_text):
    ''' Extract event name that appears near a specific date in the line '''
    # Find the position of the date in the line
    date_pos = line.find(date_text)
    if date_pos == -1:
        return ""
    
    # Get text before the date (potential event name)
    before_date = line[:date_pos].strip()
    # Get text after the date (potential event name continuation)
    after_date = line[date_pos + len(date_text):].strip()
    
    # Look for event text patterns
    # Priority 1: Text immediately before the date
    before_words = before_date.split()
    event_words = []
    
    # Take words from the end moving backwards until we hit another date
    for word in reversed(before_words):
        # Stop if we hit a date pattern
        if re.match(r'[A-Za-z]+ \d{1,2}', word):
            break  # Hit another date, stop
        if re.match(r'\d{1,2}-\d{1,2}', word):
            break  # Hit a date range, stop
        # Stop if we hit certain stop words that indicate column boundaries
        if word.lower() in ['session', 'tue,', 'wed,', 'thu,', 'fri,', 'sat,', 'sun,', 'mon,']:
            # These indicate we're hitting data from another column
            break
        event_words.insert(0, word)
        if len(event_words) >= 5:  # Limit event name length to avoid cross-column contamination
            break
    
    # Only add words from after the date if we have very few words and they look like continuations
    if len(event_words) < 2:
        after_words = after_date.split()
        for word in after_words:
            if re.match(r'[A-Za-z]+ \d{1,2}', word):
                break  # Hit another date, stop
            if re.match(r'\d{1,2}-\d{1,2}', word):
                break  # Hit a date range, stop
            # Stop on common academic terms that might be from another column
            if word.lower() in ['session', 'classes', 'begin', 'ends', 'holiday']:
                break
            event_words.append(word)
            if len(event_words) >= 3:  # Keep it short for after-date additions
                break
    
    # Clean up common artifacts from multi-column parsing
    event_name = ' '.join(event_words)
    
    # Remove common PDF parsing artifacts
    event_name = re.sub(r'\b(Tue,|Wed,|Thu,|Fri,|Sat,|Sun,|Mon,)\s*', '', event_name)
    event_name = re.sub(r'\b(May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b', '', event_name)
    event_name = re.sub(r'\bSession\s+[IVX]+\b', '', event_name)
    
    # Clean up extra whitespace
    event_name = ' '.join(event_name.split())
    
    return event_name

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
        
        # Extract dates with their surrounding context
        processed_events = extract_date_event_pairs(line, semester, start_year, end_year)
        events.extend(processed_events)
    
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
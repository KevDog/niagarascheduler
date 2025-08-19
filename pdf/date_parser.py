#!/usr/bin/env python

import re
import arrow

def extract_date_range_from_text(text):
    ''' Extract date range from text like "November 28-29, 2024" '''
    pattern = r'([A-Za-z]+) (\d{1,2})-(\d{1,2}), (\d{4})'
    match = re.search(pattern, text)
    if match:
        try:
            month_name = match.group(1)
            start_day = int(match.group(2))
            end_day = int(match.group(3))
            year = int(match.group(4))
            
            months = ['January', 'February', 'March', 'April', 'May',
                    'June', 'July', 'August', 'September', 'October', 'November', 'December']
            month_num = months.index(month_name) + 1
            dates = []
            for day in range(start_day, end_day + 1):
                dates.append(arrow.get(year, month_num, day))
            return dates
        except:
            return []
    
    # Try single date format
    pattern = r'([A-Za-z]+ \d{1,2}, \d{4})'
    match = re.search(pattern, text)
    if match:
        try:
            date_str = match.group(1)
            return [arrow.get(date_str, 'MMMM D, YYYY')]
        except:
            return []
    return []

def parse_single_date_from_text(date_text, year):
    ''' Parse single date like "September 02" into YYYY-MM-DD format '''
    try:
        months = ['January', 'February', 'March', 'April', 'May',
                'June', 'July', 'August', 'September', 'October', 'November', 'December']
        
        parts = date_text.strip().split()
        if len(parts) >= 2:
            month_name = parts[0]
            day = int(parts[1])
            month_num = months.index(month_name) + 1
            
            date_obj = arrow.get(year, month_num, day)
            return date_obj.format('YYYY-MM-DD')
    except:
        pass
    return "TBD"

def parse_date_range_from_text(date_text, year):
    ''' Parse date range like "November 27-29" into list of YYYY-MM-DD dates '''
    try:
        months = ['January', 'February', 'March', 'April', 'May',
                'June', 'July', 'August', 'September', 'October', 'November', 'December']
        
        # Look for pattern like "November 27-29"
        match = re.search(r'([A-Za-z]+)\s+(\d+)-(\d+)', date_text)
        if match:
            month_name = match.group(1)
            start_day = int(match.group(2))
            end_day = int(match.group(3))
            
            month_num = months.index(month_name) + 1
            
            dates = []
            for day in range(start_day, end_day + 1):
                date_obj = arrow.get(year, month_num, day)
                dates.append(date_obj.format('YYYY-MM-DD'))
            
            return dates
    except:
        pass
    return []
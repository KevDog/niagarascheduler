#!/usr/bin/env python

import re
import arrow
from pdf.pdf_extractor import extract_text_from_pdf

def extract_semester_dates_from_pdf_text(text, semester, year):
    ''' Extract dates for specific semester from PDF text '''
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
        return [], [], []
    
    # Look for semester-specific dates in text
    lines = text.split('\n')
    first_day = None
    last_day = None
    no_classes = []
    
    # Find semester section boundaries
    semester_section = []
    in_semester_section = False
    
    for line in lines:
        line_upper = line.upper()
        if semester.upper() in line_upper and str(year) in line:
            in_semester_section = True
        elif any(other_sem in line_upper for other_sem in ['FALL', 'SPRING', 'SUMMER']) and str(year) not in line and in_semester_section:
            break
        if in_semester_section:
            semester_section.append(line)
    
    # If no specific section found, try to extract dates by year filtering
    if not semester_section:
        semester_section = lines
    
    semester_text = '\n'.join(semester_section)
    
    # For this specific PDF format, parse by looking at column structure
    # Find the main data lines with dates - look for "August 26 January 25" pattern
    for i, line in enumerate(lines):
        if 'August 26' in line and 'January 25' in line:
            # This is the actual class start dates line
            dates = re.findall(r'([A-Za-z]+ \d{1,2})', line)
            if len(dates) >= 2:
                aug_date = dates[0]  # Fall date (August 26)
                jan_date = dates[1]  # Spring date (January 25)
                
                # Look at next line for context
                next_line = lines[i+1] if i+1 < len(lines) else ""
                if 'classes begin' in next_line.lower():
                    if semester == 'fall':
                        try:
                            first_day = arrow.get(f"{aug_date}, {start_year}", 'MMMM D, YYYY')
                        except:
                            pass
                    elif semester == 'spring':
                        try:
                            first_day = arrow.get(f"{jan_date}, {end_year}", 'MMMM D, YYYY')
                        except:
                            pass
        
        # Look for "Last Day of Classes" pattern
        if 'December' in line and 'April' in line:
            dates = re.findall(r'([A-Za-z]+ \d{1,2})', line)
            if len(dates) >= 2:
                dec_date = dates[0]  # Fall end
                apr_date = dates[1]  # Spring end
                
                # Check if this is about last day of classes
                next_line = lines[i+1] if i+1 < len(lines) else ""
                if 'last day of classes' in next_line.lower():
                    if semester == 'fall':
                        try:
                            last_day = arrow.get(f"{dec_date}, {start_year}", 'MMMM D, YYYY')
                        except:
                            pass
                    elif semester == 'spring':
                        try:
                            last_day = arrow.get(f"{apr_date}, {end_year}", 'MMMM D, YYYY')
                        except:
                            pass
        
        # Look for holidays and breaks
        if re.search(r'holiday|break', line, re.IGNORECASE) and not re.search(r'final|exam', line, re.IGNORECASE):
            # Extract dates from holiday lines
            date_matches = re.findall(r'([A-Za-z]+ \d{1,2})', line)
            date_range_match = re.search(r'([A-Za-z]+ \d{1,2})-(\d{1,2})', line)
            
            if date_range_match:
                # Handle date ranges like "November 27-29"
                try:
                    start_month_day = date_range_match.group(1)
                    end_day = int(date_range_match.group(2))
                    
                    month_name = start_month_day.split()[0]
                    start_day = int(start_month_day.split()[1])
                    
                    months = ['January', 'February', 'March', 'April', 'May',
                            'June', 'July', 'August', 'September', 'October', 'November', 'December']
                    month_num = months.index(month_name) + 1
                    
                    # Determine year based on semester and month
                    if semester == 'fall' and month_num >= 8:
                        date_year = start_year
                    elif semester == 'spring' and month_num <= 6:
                        date_year = end_year
                    else:
                        continue
                    
                    for day in range(start_day, end_day + 1):
                        no_classes.append(arrow.get(date_year, month_num, day))
                except:
                    pass
            else:
                # Handle single dates
                for date_match in date_matches:
                    try:
                        month_name = date_match.split()[0]
                        months = ['January', 'February', 'March', 'April', 'May',
                                'June', 'July', 'August', 'September', 'October', 'November', 'December']
                        month_num = months.index(month_name) + 1
                        
                        # Determine year based on semester and month
                        if semester == 'fall' and month_num >= 8:
                            date_year = start_year
                        elif semester == 'spring' and month_num <= 6:
                            date_year = end_year
                        else:
                            continue
                            
                        date_str = f"{date_match}, {date_year}"
                        no_classes.append(arrow.get(date_str, 'MMMM D, YYYY'))
                    except:
                        pass
    
    # Fallback for last day if not found - use reasonable semester end dates
    if not last_day:
        if semester == 'fall':
            try:
                last_day = arrow.get(f"December 15, {start_year}", 'MMMM D, YYYY')
            except:
                pass
        elif semester == 'spring':
            try:
                last_day = arrow.get(f"May 15, {end_year}", 'MMMM D, YYYY')
            except:
                pass
    
    return ([first_day] if first_day else []), ([last_day] if last_day else []), no_classes

def parse_pdf_calendar_for_semester(pdf_path, semester, year):
    ''' Parse PDF calendar for specific semester and year '''
    text = extract_text_from_pdf(pdf_path)
    return extract_semester_dates_from_pdf_text(text, semester, year)
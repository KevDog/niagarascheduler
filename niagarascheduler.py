#!/usr/bin/env python

import re, sys, urllib.request
import arrow # http://crsmithdev.com/arrow/
import pypandoc # https://github.com/bebraw/pypandoc
from bs4 import BeautifulSoup
from itertools import cycle
import pdfplumber

def locale():
    return arrow.locales.get_locale('en_us')

def regex(keyword):
    return re.compile('(.*)' + keyword + '(.*)', re.DOTALL)

def make_url(semester, year): 
    ''' Takes semester and year as strings, returns path to semester-specific JSON calendar '''
    import os
    
    # Look for semester-specific JSON file
    calendars_dir = os.path.join(os.path.dirname(__file__), 'calendars')
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
    pdf_path = os.path.join(os.path.dirname(__file__), 'niagara', pdf_filename)
    
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(os.path.dirname(__file__), 'niagara', 'Academic-Year-Schedule-Lewiston-2024-2025.pdf')
    
    return pdf_path

def date_formats():
    ''' based on Arrow string formats at http://crsmithdev.com/arrow/#tokens '''
    date_formats = [('Tuesday, January 12, 2016', 'dddd, MMMM D, YYYY'),
            ('Tuesday, January 12', 'dddd, MMMM D'),
            ('Tue., Jan. 12, 2016', 'ddd., MMM. D, YYYY'),
            ('Tue., Jan. 12', 'ddd., MMM. D'),
            ('January 12, 2016', 'MMMM D, YYYY'),
            ('January 12', 'MMMM D'),
            ('Jan. 12', 'MMM. D'),
            ('January 12 (Tuesday)', 'MMMM D (dddd)'),
            ('1/12', 'M/D'),
            ('01/12', 'MM/DD'),
            ('2016-01-12', 'YYYY-MM-DD')]
    return date_formats

def fetch_registrar_table(file_path, semester=None, year=None):
    ''' Get academic calendar data from semester-specific JSON or PDF file '''
    if file_path.endswith('.json'):
        # Load from semester-specific JSON
        return load_semester_calendar_from_json(file_path)
    else:
        # Load from PDF (legacy)
        if semester and year:
            return parse_pdf_calendar_for_semester(file_path, semester, year)
        else:
            return parse_pdf_calendar(file_path)

def range_of_days(start, end):
    return arrow.Arrow.range('day', start, end)

def clean_cell(td):
    ''' Remove whitespace from a registrar table cell '''
    return re.sub(r"\s+", "", td)

def parse_td_for_dates(td):
    ''' Get date or date range as lists from cell in registrar's table '''
    cell = clean_cell(td)
    months = ['January', 'February', 'March', 'April', 'May',
            'June', 'July', 'August', 'September', 'October', 'November', 'December']
    ms = [locale().month_number(m) for m in months if m in cell]
    ds = [int(d) for d in re.split('\D', cell) if 0 < len(d) < 3]
    ys = [int(y) for y in re.split('\D', cell) if len(y) == 4]
    dates = zip(cycle(ms), ds) if len(ds) > len(ms) else zip(ms, ds)
    dates = [arrow.get(ys[0], md[0], md[1]) for md in dates]
    if len(dates) > 1:
        return range_of_days(dates[0], dates[1])
    else:
        return dates

def parse_registrar_table(calendar_data):
    ''' Parse calendar data and return first, last, cancelled days of class as lists '''
    # calendar_data is now the tuple returned by parse_pdf_calendar
    return calendar_data

def sorted_classes(weekdays, first_day, last_day, no_classes):
    ''' Take class meetings as list of day names, return lists of Arrow objects '''
    if not first_day or not last_day:
        return [], no_classes
    semester = range_of_days(first_day[0], last_day[0])
    possible_classes = [d for d in semester if locale().day_name(d.isoweekday()) in weekdays]
    return possible_classes, no_classes

def schedule(possible_classes, no_classes, show_no=None, fmt=None):
    ''' Take lists of Arrow objects, return list of course meetings as strings '''
    course = []
    date_format = fmt if fmt else 'dddd, MMMM D, YYYY'
    for d in possible_classes:
        if d not in no_classes:
            course.append(d.format(date_format))
        elif show_no:
            course.append(d.format(date_format) + ' - NO CLASS')
    return course

def markdown(schedule, semester, year, templatedir):
    course = ['## ' + d + '\n' for d in schedule]
    course = [d + '[Fill in class plan]\n\n' if 'NO CLASS' not in d else d for d in course]
    md_args = ['--template=' + templatedir + '/syllabus.md', '--to=markdown',
            '--variable=semester:' + semester.capitalize(), '--variable=year:' + year]
    return pypandoc.convert('\n'.join(course), 'md', 'md', md_args)

def output(schedule, semester, year, fmt, templatedir, outfile):
    md = markdown(schedule, semester, year, templatedir)
    template = templatedir + '/syllabus.' + fmt if templatedir else ""
    if fmt == 'docx':
        template_arg = '--reference-docx=' + template
    else:
        template_arg = '--template=' + template
    pandoc_args = ['--standalone']
    pandoc_args.append(template_arg)
    output = pypandoc.convert(md, fmt, 'md', pandoc_args, outputfile=outfile)
    assert output == ''

def extract_text_from_pdf(pdf_path):
    ''' Extract text from PDF file '''
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_first_day_from_pdf_text(text):
    ''' Extract first day of classes from PDF text '''
    # Try original pattern first
    pattern = r'([A-Za-z]+ \d{1,2}, \d{4}).*?first day of classes'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            date_str = match.group(1)
            return arrow.get(date_str, 'MMMM D, YYYY')
        except:
            return None
    
    # Try pattern for "Classes Begin" with date before it
    pattern = r'([A-Za-z]+ \d{1,2})\s+.*?(?:undergraduate|graduate).*?classes begin'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        try:
            month_day = match.group(1)
            # Extract year from context - look for 4-digit year in text
            year_match = re.search(r'20\d{2}', text)
            if year_match:
                year = year_match.group(0)
                date_str = f"{month_day}, {year}"
                return arrow.get(date_str, 'MMMM D, YYYY')
        except:
            pass
    
    return None

def extract_last_day_from_pdf_text(text):
    ''' Extract last day of classes from PDF text '''
    # Try original pattern first
    pattern = r'([A-Za-z]+ \d{1,2}, \d{4}).*?last day of classes'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            date_str = match.group(1)
            return arrow.get(date_str, 'MMMM D, YYYY')
        except:
            return None
    
    # For this PDF format, look for patterns like "Final Examinations" or similar end indicators
    # Try to find a reasonable semester end date
    lines = text.split('\n')
    for line in lines:
        if 'final' in line.lower() and ('exam' in line.lower() or 'week' in line.lower()):
            # Look for dates in this line or nearby lines
            date_match = re.search(r'([A-Za-z]+ \d{1,2})', line)
            if date_match:
                try:
                    month_day = date_match.group(1)
                    year_match = re.search(r'20\d{2}', text)
                    if year_match:
                        year = year_match.group(0)
                        date_str = f"{month_day}, {year}"
                        return arrow.get(date_str, 'MMMM D, YYYY')
                except:
                    pass
    
    # Fallback: assume semester ends in December for fall semester
    year_match = re.search(r'20\d{2}', text)
    if year_match:
        year = year_match.group(0)
        try:
            return arrow.get(f"December 15, {year}", 'MMMM D, YYYY')
        except:
            pass
    
    return None

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

def extract_no_class_dates_from_pdf_text(text):
    ''' Extract all no class dates from PDF text '''
    no_class_dates = []
    lines = text.split('\n')
    
    for line in lines:
        if re.search(r'no classes?', line, re.IGNORECASE):
            dates = extract_date_range_from_text(line)
            no_class_dates.extend(dates)
    
    return no_class_dates

def parse_pdf_calendar(pdf_path):
    ''' Parse PDF calendar and return first, last, cancelled days of class as lists '''
    text = extract_text_from_pdf(pdf_path)
    
    first_day = extract_first_day_from_pdf_text(text)
    last_day = extract_last_day_from_pdf_text(text)
    no_classes = extract_no_class_dates_from_pdf_text(text)
    
    return [first_day] if first_day else [], [last_day] if last_day else [], no_classes

def discover_available_years():
    ''' Discover available years from PDF files in niagara directory '''
    import os
    import re
    
    niagara_dir = os.path.join(os.path.dirname(__file__), 'niagara')
    if not os.path.exists(niagara_dir):
        return []
    
    years = set()
    try:
        files = os.listdir(niagara_dir)
        for filename in files:
            if filename.endswith('.pdf'):
                # Match patterns like "2024-2025" or "25-26"
                year_match = re.search(r'(\d{4})-(\d{4})', filename)
                if year_match:
                    years.add(year_match.group(1))
                    years.add(year_match.group(2))
                else:
                    # Match patterns like "25-26" (short format)
                    short_match = re.search(r'(\d{2})-(\d{2})', filename)
                    if short_match:
                        start_year = int(short_match.group(1))
                        end_year = int(short_match.group(2))
                        # Convert to full year (assume 21st century)
                        if start_year >= 0 and start_year <= 50:
                            start_full = 2000 + start_year
                            end_full = 2000 + end_year
                        else:
                            start_full = 1900 + start_year
                            end_full = 1900 + end_year
                        years.add(str(start_full))
                        years.add(str(end_full))
    except OSError:
        return []
    
    return sorted(list(years), reverse=True)

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
    # August 26 = Fall start, January 25 = Spring start, etc.
    
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
        
        # Look for holidays
        if re.search(r'holiday|break', line, re.IGNORECASE):
            # Extract all dates from the line
            all_dates = re.findall(r'([A-Za-z]+ \d{1,2})', line)
            date_ranges = re.findall(r'([A-Za-z]+ \d{1,2})-(\d{1,2})', line)
            
            for date_str in all_dates:
                try:
                    month_name = date_str.split()[0]
                    months = ['January', 'February', 'March', 'April', 'May',
                            'June', 'July', 'August', 'September', 'October', 'November', 'December']
                    month_num = months.index(month_name) + 1
                    
                    # Assign to correct semester based on month
                    if semester == 'fall' and month_num >= 8:
                        date_year = start_year
                        no_classes.append(arrow.get(f"{date_str}, {date_year}", 'MMMM D, YYYY'))
                    elif semester == 'spring' and month_num <= 6:
                        date_year = end_year
                        no_classes.append(arrow.get(f"{date_str}, {date_year}", 'MMMM D, YYYY'))
                except:
                    pass
            
            # Handle date ranges
            for start_date, end_day in date_ranges:
                try:
                    month_name = start_date.split()[0]
                    start_day = int(start_date.split()[1])
                    end_day = int(end_day)
                    
                    months = ['January', 'February', 'March', 'April', 'May',
                            'June', 'July', 'August', 'September', 'October', 'November', 'December']
                    month_num = months.index(month_name) + 1
                    
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
        
        # Look for last day of classes
        if re.search(r'last day of classes', line, re.IGNORECASE):
            date_match = re.search(r'([A-Za-z]+ \d{1,2})', line)
            if date_match:
                try:
                    month_day = date_match.group(1)
                    month_name = month_day.split()[0]
                    months = ['January', 'February', 'March', 'April', 'May',
                            'June', 'July', 'August', 'September', 'October', 'November', 'December']
                    month_num = months.index(month_name) + 1
                    
                    if semester == 'fall' and month_num >= 10:  # Oct-Dec
                        date_year = start_year
                    elif semester == 'spring' and month_num <= 6:  # Jan-Jun
                        date_year = end_year
                    else:
                        continue
                        
                    date_str = f"{month_day}, {date_year}"
                    last_day = arrow.get(date_str, 'MMMM D, YYYY')
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

def parse_pdf_to_json(pdf_path):
    ''' Convert PDF calendar to JSON format with TBD for missing data '''
    # Use the enhanced version with events
    return parse_pdf_to_json_with_events(pdf_path)

def generate_calendar_json(niagara_dir=None, output_dir=None):
    ''' Generate separate JSON files for each semester from all PDFs in niagara directory '''
    import json
    import os
    
    if not niagara_dir:
        niagara_dir = os.path.join(os.path.dirname(__file__), 'niagara')
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(__file__), 'calendars')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(niagara_dir):
        print(f"Niagara directory not found: {niagara_dir}")
        return
    
    pdf_files = [f for f in os.listdir(niagara_dir) if f.endswith('.pdf')]
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(niagara_dir, pdf_file)
        print(f"Processing {pdf_file}...")
        
        try:
            # Parse the full academic year data first
            json_data = parse_pdf_to_json_with_events(pdf_path)
            
            # Split into separate semester files
            for semester_key, semester_data in json_data.get('semesters', {}).items():
                semester_filename = f"{semester_key}.json"
                semester_path = os.path.join(output_dir, semester_filename)
                
                # Create individual semester JSON
                semester_json = {
                    "semester": semester_key,
                    "academic_year": json_data.get('academic_year'),
                    "source_file": json_data.get('source_file'),
                    "generated_at": json_data.get('generated_at'),
                    "first_day": semester_data.get('first_day'),
                    "last_day": semester_data.get('last_day'),
                    "no_class_dates": semester_data.get('no_class_dates', []),
                    "events": semester_data.get('events', [])
                }
                
                # Check for existing semester JSON to preserve manual edits
                preservation_notes = []
                
                if os.path.exists(semester_path):
                    try:
                        with open(semester_path, 'r') as f:
                            existing_data = json.load(f)
                        
                        # Compare key fields that might have been manually edited
                        preserved_fields = []
                        
                        # Check academic year
                        if (existing_data.get('academic_year') != 'TBD' and 
                            semester_json.get('academic_year') == 'TBD'):
                            semester_json['academic_year'] = existing_data['academic_year']
                            preserved_fields.append('academic_year')
                        
                        # Preserve manually set first_day
                        if (existing_data.get('first_day') != 'TBD' and 
                            semester_json.get('first_day') == 'TBD'):
                            semester_json['first_day'] = existing_data['first_day']
                            preserved_fields.append('first_day')
                        
                        # Preserve manually set last_day
                        if (existing_data.get('last_day') != 'TBD' and 
                            semester_json.get('last_day') == 'TBD'):
                            semester_json['last_day'] = existing_data['last_day']
                            preserved_fields.append('last_day')
                        
                        # Preserve manually edited events
                        if 'events' in existing_data and 'events' in semester_json:
                            for i, existing_event in enumerate(existing_data['events']):
                                if i < len(semester_json['events']):
                                    new_event = semester_json['events'][i]
                                    
                                    # Preserve manually set event dates
                                    if (existing_event.get('date') != 'TBD' and 
                                        new_event.get('date') == 'TBD'):
                                        new_event['date'] = existing_event['date']
                                        preserved_fields.append(f'events[{i}].date')
                                    
                                    # Preserve manually set event date ranges
                                    if (existing_event.get('date_range') and 
                                        'TBD' not in str(existing_event.get('date_range')) and
                                        new_event.get('date_range') and 
                                        'TBD' in str(new_event.get('date_range'))):
                                        new_event['date_range'] = existing_event['date_range']
                                        preserved_fields.append(f'events[{i}].date_range')
                        
                        if preserved_fields:
                            preservation_notes.append({
                                'file': semester_filename,
                                'preserved_fields': preserved_fields,
                                'message': 'Preserved manual edits from existing JSON file'
                            })
                            
                            # Add preservation note to JSON
                            semester_json['_preservation_note'] = f"Preserved manual edits: {', '.join(preserved_fields)}"
                    
                    except Exception as e:
                        preservation_notes.append({
                            'file': semester_filename,
                            'preserved_fields': [],
                            'message': f'Error reading existing file: {e}'
                        })
                
                # Write semester JSON file
                with open(semester_path, 'w') as f:
                    json.dump(semester_json, f, indent=2)
                
                print(f"Generated {semester_filename}")
                
                # Store preservation notes for TBD reporting
                if preservation_notes:
                    if not hasattr(generate_calendar_json, '_preservation_notes'):
                        generate_calendar_json._preservation_notes = []
                    generate_calendar_json._preservation_notes.extend(preservation_notes)
            
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
    
    # Generate active_semester.json configuration file
    generate_active_semester_config(output_dir)

def generate_active_semester_config(output_dir):
    ''' Generate active_semester.json configuration file '''
    import json
    import os
    from datetime import datetime
    
    config_path = os.path.join(output_dir, 'active_semester.json')
    
    # Get list of semester-specific JSON files only (e.g., fall_2024.json, spring_2025.json)
    semester_files = [f for f in os.listdir(output_dir) 
                     if f.endswith('.json') and f != 'active_semester.json' and '_' in f.replace('.json', '')]
    
    # Extract semester info from filenames
    available_semesters = []
    for filename in semester_files:
        semester_name = filename.replace('.json', '')
        # Only include files that match semester_year pattern
        if '_' in semester_name and len(semester_name.split('_')) == 2:
            available_semesters.append(semester_name)
    
    # Use first available semester alphabetically as default
    if available_semesters:
        default_semester = sorted(available_semesters)[0]
    else:
        default_semester = "TBD"
    
    config = {
        "available_semesters": sorted(available_semesters, key=lambda x: (x.split('_')[1], x.split('_')[0])),
        "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "_note": "Contains list of available semesters for the interface"
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Generated active_semester.json with {len(available_semesters)} available semesters")

def discover_available_semesters():
    ''' Discover available semesters from JSON files in calendars directory '''
    import os
    import json
    
    calendars_dir = os.path.join(os.path.dirname(__file__), 'calendars')
    
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

def load_semester_calendar_from_json(json_path):
    ''' Load calendar data from semester-specific JSON file '''
    import json
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Convert dates back to Arrow objects
        first_days = []
        last_days = []
        no_class_dates = []
        
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
        
        return first_days, last_days, no_class_dates
        
    except Exception as e:
        print(f"Error loading calendar from JSON: {e}")
        return [], [], []

def load_calendar_from_json(json_path, semester, year):
    ''' Load calendar data from JSON file for specific semester '''
    import json
    
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
        import re
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

def parse_pdf_to_json_with_events(pdf_path):
    ''' Convert PDF calendar to JSON format including events '''
    import json
    import re
    
    try:
        text = extract_text_from_pdf(pdf_path)
        
        # Extract academic year from filename or content
        filename = pdf_path.split('/')[-1]
        year_match = re.search(r'(\d{4})-(\d{4})', filename)
        if year_match:
            academic_year = f"{year_match.group(1)}-{year_match.group(2)}"
            start_year = int(year_match.group(1))
            end_year = int(year_match.group(2))
        else:
            academic_year = "TBD"
            start_year = 2024
            end_year = 2025
        
        # Parse both semesters for basic dates
        fall_data = extract_semester_dates_from_pdf_text(text, 'fall', str(start_year))
        spring_data = extract_semester_dates_from_pdf_text(text, 'spring', str(end_year))
        
        # Parse events for both semesters
        fall_events = extract_semester_events_from_pdf_text(text, 'fall', str(start_year))
        spring_events = extract_semester_events_from_pdf_text(text, 'spring', str(end_year))
        
        def format_date(arrow_date):
            return arrow_date.format('YYYY-MM-DD') if arrow_date else "TBD"
        
        def format_date_list(arrow_list):
            return [date.format('YYYY-MM-DD') for date in arrow_list] if arrow_list else []
        
        json_data = {
            "academic_year": academic_year,
            "source_file": filename,
            "generated_at": arrow.now().format('YYYY-MM-DD HH:mm:ss'),
            "semesters": {
                f"fall_{start_year}": {
                    "first_day": format_date(fall_data[0][0]) if fall_data[0] else "TBD",
                    "last_day": format_date(fall_data[1][0]) if fall_data[1] else "TBD", 
                    "no_class_dates": format_date_list(fall_data[2]),
                    "events": fall_events
                },
                f"spring_{end_year}": {
                    "first_day": format_date(spring_data[0][0]) if spring_data[0] else "TBD",
                    "last_day": format_date(spring_data[1][0]) if spring_data[1] else "TBD",
                    "no_class_dates": format_date_list(spring_data[2]),
                    "events": spring_events
                }
            }
        }
        
        return json_data
        
    except Exception as e:
        # Return TBD structure for any parsing errors
        return {
            "academic_year": "TBD",
            "source_file": pdf_path.split('/')[-1],
            "generated_at": arrow.now().format('YYYY-MM-DD HH:mm:ss'),
            "error": str(e),
            "semesters": {
                "fall_TBD": {
                    "first_day": "TBD",
                    "last_day": "TBD",
                    "no_class_dates": [],
                    "events": []
                },
                "spring_TBD": {
                    "first_day": "TBD", 
                    "last_day": "TBD",
                    "no_class_dates": [],
                    "events": []
                }
            }
        }

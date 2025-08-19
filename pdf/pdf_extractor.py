#!/usr/bin/env python

import re
import arrow
import pdfplumber

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

def extract_no_class_dates_from_pdf_text(text):
    ''' Extract all no class dates from PDF text '''
    from pdf.date_parser import extract_date_range_from_text
    
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
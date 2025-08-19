#!/usr/bin/env python

import re
import arrow
from pdf.pdf_extractor import extract_text_from_pdf
from pdf.semester_parser import extract_semester_dates_from_pdf_text
from pdf.event_parser import extract_semester_events_from_pdf_text

def parse_pdf_to_json(pdf_path):
    ''' Convert PDF calendar to JSON format with TBD for missing data '''
    # Use the enhanced version with events
    return parse_pdf_to_json_with_events(pdf_path)

def parse_pdf_to_json_with_events(pdf_path):
    ''' Convert PDF calendar to JSON format including events '''
    try:
        text = extract_text_from_pdf(pdf_path)
        
        # Extract year from filename or content
        filename = pdf_path.split('/')[-1]
        year_match = re.search(r'(\d{4})-(\d{4})', filename)
        if year_match:
            start_year = int(year_match.group(1))
            end_year = int(year_match.group(2))
        else:
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
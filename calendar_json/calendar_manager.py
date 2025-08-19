#!/usr/bin/env python

import os
import json
import re
from datetime import datetime
from calendar_json.json_converter import parse_pdf_to_json_with_events

def discover_available_years():
    ''' Discover available years from PDF files in niagara directory '''
    niagara_dir = os.path.join(os.path.dirname(__file__), '..', 'niagara')
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

def generate_active_semester_config(output_dir):
    ''' Generate active_semester.json configuration file '''
    config_path = os.path.join(output_dir, 'active_semester.json')
    
    # Get list of semester-specific JSON files only
    semester_files = [f for f in os.listdir(output_dir) 
                     if f.endswith('.json') and f != 'active_semester.json' and '_' in f.replace('.json', '')]
    
    # Extract semester info from filenames
    available_semesters = []
    for filename in semester_files:
        semester_name = filename.replace('.json', '')
        # Only include files that match semester_year pattern
        if '_' in semester_name and len(semester_name.split('_')) == 2:
            available_semesters.append(semester_name)
    
    config = {
        "available_semesters": sorted(available_semesters, key=lambda x: (x.split('_')[1], x.split('_')[0])),
        "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "_note": "Contains list of available semesters for the interface"
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Generated active_semester.json with {len(available_semesters)} available semesters")

def generate_calendar_json(niagara_dir=None, output_dir=None):
    ''' Generate separate JSON files for each semester from all PDFs in niagara directory '''
    if not niagara_dir:
        niagara_dir = os.path.join(os.path.dirname(__file__), '..', 'niagara')
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'calendars')
    
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
                    "source_file": json_data.get('source_file'),
                    "generated_at": json_data.get('generated_at'),
                    "first_day": semester_data.get('first_day'),
                    "last_day": semester_data.get('last_day'),
                    "no_class_dates": semester_data.get('no_class_dates', []),
                    "events": semester_data.get('events', [])
                }
                
                # Write semester JSON file
                with open(semester_path, 'w') as f:
                    json.dump(semester_json, f, indent=2)
                
                print(f"Generated {semester_filename}")
            
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
    
    # Generate active_semester.json configuration file
    generate_active_semester_config(output_dir)
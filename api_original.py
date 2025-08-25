#!/usr/bin/env python
"""
Flask API for Niagara University Syllabus Generator
Provides JSON endpoints for Vue frontend
"""

import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from tempfile import NamedTemporaryFile
from utilities.scheduler import (
    make_url, sorted_classes, schedule, date_formats, 
    parse_registrar_table, fetch_registrar_table, 
    discover_available_semesters
)
from core.markdown_processor import generate_syllabus_markdown, generate_syllabus
from core.data_loader import DepartmentDataLoader

app = Flask(__name__)
CORS(app)  # Enable CORS for Vue frontend

# Initialize data loader
data_dir = os.path.join(os.path.dirname(__file__), 'data')
data_loader = DepartmentDataLoader(data_dir)

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get application configuration data"""
    # Get available semesters from data/semesters directory
    semesters_dir = os.path.join(data_dir, 'semesters')
    available_semesters = []
    
    if os.path.exists(semesters_dir):
        for semester_folder in os.listdir(semesters_dir):
            if os.path.isdir(os.path.join(semesters_dir, semester_folder)):
                # Convert folder name like "25_FA" to readable format
                if '_' in semester_folder:
                    year_part, season_part = semester_folder.split('_', 1)
                    # Convert season abbreviations to full names
                    season_map = {
                        'FA': 'Fall',
                        'SP': 'Spring', 
                        'SU': 'Summer',
                        'WI': 'Winter'
                    }
                    full_season = season_map.get(season_part, season_part)
                    full_year = f"20{year_part}" if len(year_part) == 2 else year_part
                    
                    available_semesters.append({
                        'key': semester_folder,
                        'semester': full_season,
                        'year': full_year,
                        'display': f"{full_season} {full_year}"
                    })
    
    # Sort semesters by year and season
    available_semesters.sort(key=lambda x: (x['year'], x['semester']))
    
    months = ['January', 'February', 'March', 'April', 'May',
              'June', 'July', 'August', 'September', 'October', 'November', 'December']
    days = [str(d) for d in range(1, 32)]
    formats = [{'key': t[0], 'value': t[1]} for t in date_formats()]
    
    return jsonify({
        'semesters': available_semesters,
        'months': months,
        'days': days,
        'date_formats': formats
    })

@app.route('/api/departments', methods=['GET'])
def get_departments():
    """Get list of all departments"""
    departments = data_loader.get_all_departments()
    dept_list = []
    
    for dept_code in departments:
        dept = data_loader.load_department(dept_code)
        if dept:
            dept_list.append({
                'code': dept_code,
                'name': dept.name,
                'mission_statement': dept.mission_statement
            })
    
    return jsonify({'departments': dept_list})

@app.route('/api/departments/<dept_code>', methods=['GET'])
def get_department(dept_code):
    """Get specific department information"""
    dept = data_loader.load_department(dept_code)
    if not dept:
        return jsonify({'error': 'Department not found'}), 404
    
    return jsonify({
        'code': dept_code,
        'name': dept.name,
        'mission_statement': dept.mission_statement,
        'courses': [
            {
                'number': course.number,
                'title': course.title,
                'description': course.description
            } for course in dept.courses
        ]
    })

@app.route('/api/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    """Get specific course information"""
    course = data_loader.find_course(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    return jsonify({
        'number': course.number,
        'title': course.title,
        'description': course.description,
        'instructors': course.instructors,
        'textbooks': course.textbooks,
        'meeting_days': course.meeting_days
    })

@app.route('/api/offerings/<semester>/<dept_code>/<course_number>', methods=['GET'])
def get_course_offerings(semester, dept_code, course_number):
    """Get course offerings for a specific semester, department, and course"""
    offerings_file = os.path.join(data_dir, 'semesters', semester, f'{dept_code}.json')
    
    if not os.path.exists(offerings_file):
        return jsonify({'offerings': []})
    
    try:
        with open(offerings_file, 'r') as f:
            import json
            offerings_data = json.load(f)
        
        # Filter offerings by course number (handle both exact match and prefix match)
        matching_offerings = []
        for offering in offerings_data:
            offering_number = offering.get('number', '')
            # Remove department prefix if present (e.g., "THR101A" -> "101A")
            if offering_number.startswith(dept_code):
                clean_number = offering_number[len(dept_code):]
            else:
                clean_number = offering_number
            
            # Match course number (e.g., "101" matches "101A", "101B", etc.)
            if clean_number.startswith(course_number):
                section_letter = clean_number[len(course_number):] if len(clean_number) > len(course_number) else 'A'
                
                offering_data = {
                    'number': offering_number,
                    'name': offering.get('name', ''),
                    'credits': offering.get('credits', ''),
                    'section': section_letter
                }
                
                # Add schedule information if available
                if 'days' in offering:
                    offering_data['days'] = offering.get('days', '')
                    offering_data['start_time'] = offering.get('start_time', '')
                    offering_data['end_time'] = offering.get('end_time', '')
                    offering_data['delivery_type'] = offering.get('delivery_type', '')
                    offering_data['availability'] = offering.get('availability', '')
                
                matching_offerings.append(offering_data)
        
        return jsonify({'offerings': matching_offerings})
        
    except Exception as e:
        return jsonify({'error': f'Error loading offerings: {str(e)}'}), 500

@app.route('/api/generate-schedule', methods=['POST'])
def generate_schedule():
    """Generate schedule data from calendar"""
    data = request.get_json()
    
    # Extract parameters
    semester_year = data.get('semester_year')
    if not semester_year:
        return jsonify({'error': 'semester_year is required'}), 400
        
    semester, year = semester_year.split('_')
    weekdays = data.get('weekdays', [])
    date_format = data.get('date_format', '')
    
    # Get available formats
    available_formats = date_formats()
    matching_formats = [b for (a, b) in available_formats if a == date_format]
    if not matching_formats:
        date_fmt = available_formats[0][1] if available_formats else 'M/D'
    else:
        date_fmt = matching_formats[0]
    
    # Get filtering preferences
    show_holidays = data.get('show_holidays', True)
    show_breaks = data.get('show_breaks', True)
    show_events = data.get('show_events', True)
    
    try:
        url = make_url(semester, year)
        calendar_data = fetch_registrar_table(url, semester, year)
        first_day, last_day, no_classes, events = parse_registrar_table(calendar_data)
        possible_classes, no_classes = sorted_classes(weekdays, first_day, last_day, no_classes)
        
        course_schedule = schedule(
            possible_classes, no_classes, show_no=True, fmt=date_fmt, events=events,
            show_holidays=show_holidays, show_breaks=show_breaks, show_events=show_events
        )
        
        return jsonify({
            'schedule': course_schedule,
            'semester': semester,
            'year': year,
            'first_day': first_day.isoformat(),
            'last_day': last_day.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing calendar: {str(e)}'}), 500

@app.route('/api/generate-syllabus', methods=['POST'])
def generate_syllabus_api():
    """Generate syllabus markdown content"""
    data = request.get_json()
    
    # Extract parameters
    schedule_data = data.get('schedule', [])
    semester = data.get('semester')
    year = data.get('year')
    course_id = data.get('course_id', '')
    include_description = data.get('include_description', False)
    
    # Additional syllabus data
    instructor_name = data.get('instructor_name', 'TBD')
    textbooks = data.get('textbooks', '')
    assignments = data.get('assignments', '')
    attendance_policy = data.get('attendance_policy', '')
    grading_policy = data.get('grading_policy', '')
    ai_policy = data.get('ai_policy', '')
    bibliography = data.get('bibliography', '')
    
    try:
        markdown_content = generate_syllabus_markdown(
            schedule_data=schedule_data,
            semester=semester,
            year=year,
            course_id=course_id,
            include_description=include_description,
            instructor_name=instructor_name,
            textbooks=textbooks,
            assignments=assignments,
            attendance_policy=attendance_policy,
            grading_policy=grading_policy,
            ai_policy=ai_policy,
            bibliography=bibliography
        )
        
        return jsonify({
            'markdown': markdown_content,
            'course_id': course_id,
            'semester': semester,
            'year': year
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating syllabus: {str(e)}'}), 500

@app.route('/api/export-syllabus', methods=['POST'])
def export_syllabus_api():
    """Export syllabus in specified format"""
    data = request.get_json()
    
    # Extract parameters
    schedule_data = data.get('schedule', [])
    semester = data.get('semester')
    year = data.get('year')
    course_id = data.get('course_id', '')
    include_description = data.get('include_description', False)
    export_format = data.get('format', 'docx')
    
    # Additional syllabus data
    instructor_name = data.get('instructor_name', 'TBD')
    textbooks = data.get('textbooks', '')
    assignments = data.get('assignments', '')
    attendance_policy = data.get('attendance_policy', '')
    grading_policy = data.get('grading_policy', '')
    ai_policy = data.get('ai_policy', '')
    bibliography = data.get('bibliography', '')
    
    try:
        suffix = '.' + export_format
        templatedir = os.path.dirname(os.path.abspath(__file__)) + '/templates'
        tf = NamedTemporaryFile(suffix=suffix, delete=False)
        
        generate_syllabus(
            schedule_data=schedule_data,
            semester=semester,
            year=year,
            output_format=export_format,
            template_dir=templatedir,
            output_file=tf.name,
            course_id=course_id,
            include_description=include_description,
            instructor_name=instructor_name,
            textbooks=textbooks,
            assignments=assignments,
            attendance_policy=attendance_policy,
            grading_policy=grading_policy,
            ai_policy=ai_policy,
            bibliography=bibliography
        )
        
        filename = f"{semester}{year}Syllabus{suffix}"
        return send_file(tf.name, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': f'Error generating export: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Niagara University Scheduler API')
    parser.add_argument('--port', '-p',
                       type=int,
                       default=int(os.environ.get('PORT', 5000)),
                       help='Port to run the API server on (default: 5000)')
    
    args = parser.parse_args()
    
    print(f"Starting API server on port {args.port}...")
    app.run(host='0.0.0.0', port=args.port, debug=True)
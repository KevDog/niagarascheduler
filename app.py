#!/usr/bin/env python

import os
from arrow import get
from flask import Flask, render_template, request, url_for, send_file
from tempfile import NamedTemporaryFile
from scheduler import make_url, sorted_classes, schedule, output, date_formats, parse_registrar_table, fetch_registrar_table, locale, discover_available_semesters

app = Flask(__name__, static_url_path = "")

@app.route('/')
def form():
    semesters = discover_available_semesters()
    if not semesters:
        semesters = [('fall', '2024'), ('spring', '2025')]
    
    months = ['January', 'February', 'March', 'April', 'May',
            'June', 'July', 'August', 'September', 'October', 'November', 'December']
    ddays = [str(d) for d in range(1,32)]
    formats = [t[0] for t in date_formats()]
    return render_template('form_submit.html', semesters=semesters, months=months, ddays=ddays, formats=formats)


@app.route('/results/', methods=['POST'])
def results():

    semester_year = request.form['semester_year']
    semester, year = semester_year.split('_')
    weekdays = request.form.getlist('days')
    format_selection = request.form.get('format', '')
    available_formats = date_formats()
    matching_formats = [b for (a, b) in available_formats if a == format_selection]
    if not matching_formats:
        # Default to first available format if none matches
        date_fmt = available_formats[0][1] if available_formats else 'M/D'
    else:
        date_fmt = matching_formats[0]
# No longer need output_fmt since we're showing preview first
    
    # Get user preferences for showing events
    show_holidays = 'show_holidays' in request.form
    show_breaks = 'show_breaks' in request.form
    show_events = 'show_events' in request.form
    
    # Get course information preferences
    course_id = request.form.get('course_id', '').strip()
    include_description = 'include_description' in request.form
    

    try:
        url = make_url(semester, year)
        calendar_data = fetch_registrar_table(url, semester, year)
        first_day, last_day, no_classes, events = parse_registrar_table(calendar_data)
        possible_classes, no_classes = sorted_classes(weekdays, first_day, last_day, no_classes)
    except Exception as e:
        return f"Error processing calendar: {str(e)}"
    course = schedule(possible_classes, no_classes, show_no=True, fmt=date_fmt, events=events,
                     show_holidays=show_holidays, show_breaks=show_breaks, show_events=show_events) 

    # Generate markdown content for preview
    from core.markdown_processor import generate_syllabus_markdown
    
    markdown_content = generate_syllabus_markdown(
        schedule_data=course,
        semester=semester,
        year=year,
        course_id=course_id,
        include_description=include_description
    )
    
    # Store form data in session for export functionality
    form_data = {
        'schedule_data': course,
        'semester': semester,
        'year': year,
        'course_id': course_id,
        'include_description': include_description,
        'date_fmt': date_fmt
    }
    
    return render_template('results.html', 
                         markdown_content=markdown_content,
                         form_data=form_data)


@app.route('/export/', methods=['POST'])
def export_syllabus():
    """Handle syllabus export in various formats"""
    
    # Reconstruct form data
    schedule_data = request.form['schedule_data'].split(',') if request.form.get('schedule_data') else []
    semester = request.form['semester']
    year = request.form['year']
    course_id = request.form.get('course_id', '')
    include_description = request.form.get('include_description') == 'True'
    export_format = request.form['export_format']
    
    try:
        from tempfile import NamedTemporaryFile
        
        suffix = '.' + export_format
        templatedir = os.path.dirname(os.path.abspath(__file__)) + '/templates'
        tf = NamedTemporaryFile(suffix=suffix, delete=False)
        
        # Use markdown processor to generate file
        from core.markdown_processor import generate_syllabus
        
        generate_syllabus(
            schedule_data=schedule_data,
            semester=semester,
            year=year,
            output_format=export_format,
            template_dir=templatedir,
            output_file=tf.name,
            course_id=course_id,
            include_description=include_description
        )
        
        filename = f"{semester}{year}Syllabus{suffix}"
        return send_file(tf.name, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return f"Error generating export: {str(e)}", 500


if __name__ == '__main__':
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Run Niagara University Scheduler web application')
    parser.add_argument('--generate', 
                       action='store_true',
                       help='Generate calendar JSON files from PDFs before starting server')
    parser.add_argument('--port', '-p',
                       type=int,
                       default=int(os.environ.get('PORT', 5001)),
                       help='Port to run the server on (default: 5001)')
    
    args = parser.parse_args()
    
    if args.generate:
        print("Generating calendar JSON files...")
        from scheduler import generate_calendar_json
        generate_calendar_json()
        print("Calendar generation complete!")
    
    print(f"Starting server on port {args.port}...")
    app.run(host='0.0.0.0', port=args.port, debug=True)

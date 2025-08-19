#!/usr/bin/env python

import os
from arrow import get
from flask import Flask, render_template, request, url_for, send_file
from tempfile import NamedTemporaryFile
from niagarascheduler import make_url, sorted_classes, schedule, output, date_formats, parse_registrar_table, fetch_registrar_table, locale, discover_available_semesters

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

@app.route('/generic/', methods=['GET'])
def generic():
    semesters = discover_available_semesters()
    if not semesters:
        semesters = [('fall', '2024'), ('spring', '2025')]
    months = ['January', 'February', 'March', 'April', 'May',
            'June', 'July', 'August', 'September', 'October', 'November', 'December']
    ddays = [str(d) for d in range(1,32)]
    formats = [t[0] for t in date_formats()]
    return render_template('form_submit_generic.html', semesters=semesters, months=months, ddays=ddays, formats=formats)

@app.route('/results/', methods=['POST'])
def results():

    semester = request.form['semester']
    year = request.form['year']
    weekdays = request.form.getlist('days')
    date_fmt = [b for (a, b) in date_formats() if a == request.form['format']][0]
    output_fmt = request.form['output']

    try:
        url = make_url(semester, year)
        calendar_data = fetch_registrar_table(url, semester, year)
        first_day, last_day, no_classes = parse_registrar_table(calendar_data)
        possible_classes, no_classes = sorted_classes(weekdays, first_day, last_day, no_classes)
    except Exception as e:
        return f"Error processing calendar: {str(e)}"
    course = schedule(possible_classes, no_classes, show_no=True, fmt=date_fmt) 

    if output_fmt == 'plain':
        return '<br/>'.join(course)
    else:
        suffix = '.' + output_fmt
        templatedir = os.path.dirname(os.path.abspath(__file__)) + '/templates'
        tf = NamedTemporaryFile(suffix=suffix)
        output(course, semester, year, output_fmt, templatedir=templatedir, outfile=tf.name)
        filename = semester + year + 'Syllabus' + suffix
        return send_file(tf.name, attachment_filename=filename, as_attachment=True)

@app.route('/classes/', methods=['POST'])
def classes():

    year = int(request.form['year'])
    start_month = locale().month_number(request.form['start-month'])
    start_day = int(request.form['start-day'])
    last_month = locale().month_number(request.form['last-month'])
    last_day = int(request.form['last-day'])
    weekdays = request.form.getlist('days')
    date_fmt = [b for (a, b) in date_formats() if a == request.form['format']][0]

    try:
        start_date = [get(year, start_month, start_day)]
    except:
        return "The starting date you specified does not exist." 

    try:
        last_date = [get(year, last_month, last_day)]
    except:
        return "The ending date you specified does not exist." 

    possible_classes, no_classes = sorted_classes(weekdays, start_date, last_date, no_classes=[])
    course = schedule(possible_classes, no_classes, show_no=True, fmt=date_fmt) 
    return '<br/>'.join(course)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

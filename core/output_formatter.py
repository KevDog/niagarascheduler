#!/usr/bin/env python

import pypandoc
import os
from core.docx_editor import enhance_syllabus_docx, install_docx_support
from core.course_descriptions import CourseDescriptionManager

def markdown(schedule, semester, year, templatedir):
    course = ['## ' + d + '\n' for d in schedule]
    course = [d + '[Fill in class plan]\n\n' if 'NO CLASS' not in d else d for d in course]
    md_args = ['--template=' + templatedir + '/syllabus.md', '--to=markdown',
            '--variable=semester:' + semester.capitalize(), '--variable=year:' + year]
    return pypandoc.convert('\n'.join(course), 'md', 'md', md_args)

def output(schedule, semester, year, fmt, templatedir, outfile):
    if fmt == 'docx':
        # Try enhanced DOCX generation first
        template_path = os.path.join(templatedir, 'NU 2025 Syllabus Template.docx')
        if os.path.exists(template_path):
            success = enhance_syllabus_docx(template_path, schedule, outfile, semester, year)
            if success:
                return
        
        # Fallback to PyPandoc method
        template_path = os.path.join(templatedir, 'syllabus.docx')
        if os.path.exists(template_path):
            md = markdown(schedule, semester, year, templatedir)
            template_arg = '--reference-docx=' + template_path
            pandoc_args = ['--standalone', template_arg]
            pypandoc.convert(md, fmt, 'md', pandoc_args, outputfile=outfile)
            return
    
    # Original method for other formats
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

def format_text_with_description(schedule, course_id=None, include_description=False):
    """Format text output with optional course description"""
    if not include_description or not course_id:
        return '\n'.join(schedule)
    
    # Data file path relative to project root
    project_root = os.path.dirname(os.path.dirname(__file__))
    data_file = os.path.join(project_root, 'data', 'courses.json')
    manager = CourseDescriptionManager(data_file)
    description = manager.get_course_description(course_id)
    
    result = f"Course Description: {description}\n\n"
    result += '\n'.join(schedule)
    return result
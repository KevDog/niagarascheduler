#!/usr/bin/env python

"""
Simplified output formatter using markdown-first approach
"""

from core.markdown_processor import generate_syllabus


def output(schedule, semester, year, fmt, templatedir, outfile, course_id=None, include_description=False, **kwargs):
    """Generate syllabus in specified format using markdown-first approach"""
    
    generate_syllabus(
        schedule_data=schedule,
        semester=semester,
        year=year,
        output_format=fmt,
        template_dir=templatedir,
        output_file=outfile,
        course_id=course_id,
        include_description=include_description,
        **kwargs
    )


def format_text_with_description(schedule, course_id=None, include_description=False):
    """Format text output with optional course description (legacy compatibility)"""
    from core.markdown_processor import generate_syllabus_markdown
    
    # Generate markdown first, then convert to plain text
    markdown_content = generate_syllabus_markdown(
        schedule_data=schedule,
        semester='',
        year='',
        course_id=course_id,
        include_description=include_description
    )
    
    # Simple markdown to text conversion (remove markdown formatting)
    text_content = markdown_content
    text_content = text_content.replace('# ', '').replace('## ', '').replace('### ', '')
    text_content = text_content.replace('**', '').replace('*', '')
    text_content = text_content.replace('|', ' ').replace('---', '')
    
    return text_content
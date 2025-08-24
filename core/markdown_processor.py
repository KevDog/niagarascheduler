#!/usr/bin/env python

"""
Markdown-first syllabus generation for Niagara University Scheduler

Processes markdown templates with placeholder replacement and converts to various formats via pandoc.
"""

import os
import pypandoc
from core.data_loader import DepartmentDataLoader


def load_template(template_path):
    """Load markdown template from file"""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def format_schedule_as_markdown(schedule_data):
    """Convert schedule data to markdown table format"""
    if not schedule_data:
        return "No schedule data available."
    
    # Create markdown table
    markdown_table = "| Date | Event |\n|------|-------|\n"
    
    for item in schedule_data:
        # Clean up the schedule item for markdown
        clean_item = str(item).replace('**', '').replace('*', '')
        if ':' in clean_item:
            date_part, event_part = clean_item.split(':', 1)
            markdown_table += f"| {date_part.strip()} | {event_part.strip()} |\n"
        else:
            markdown_table += f"| {clean_item.strip()} | |\n"
    
    return markdown_table


def replace_placeholders(template_content, replacements):
    """Replace all placeholders in template with provided values"""
    content = template_content
    
    for placeholder, value in replacements.items():
        if value is not None:
            content = content.replace(f"{{{{{placeholder}}}}}", str(value))
    
    return content


def generate_syllabus_markdown(schedule_data, semester, year, course_id=None, include_description=False, **kwargs):
    """Generate complete syllabus markdown with all replacements"""
    
    # Load template
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'syllabus_master.md')
    template_content = load_template(template_path)
    
    # Prepare course information
    course_title = kwargs.get('course_title', f'Course {course_id}' if course_id else 'Course Title')
    instructor_name = kwargs.get('instructor_name', 'TBD')
    
    # Get course information using new data loader
    course_description = "Please paste your course description here which can be found in the online catalogue under Primary Resources."
    department_mission_statement = "Please paste your departmental mission statement here which can be found in the online catalogue under Primary Resources."
    course_instructors = []
    course_textbooks = []
    zoom_link = None
    
    if course_id:
        project_root = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(project_root, 'data')
        loader = DepartmentDataLoader(data_dir)
        course = loader.find_course(course_id)
        
        if course:
            if include_description and course.description:
                course_description = course.description
            if course.title:
                course_title = course.title
            if course.instructors:
                course_instructors = course.instructors
                instructor_name = ", ".join(course.instructors)
            if course.textbooks:
                course_textbooks = course.textbooks
            if course.zoom_link:
                zoom_link = course.zoom_link
        
        # Get department mission statement
        if course_id and ' ' in course_id:
            dept_code = course_id.split()[0]
            department = loader.load_department(dept_code)
            if department and department.mission_statement:
                department_mission_statement = department.mission_statement
    
    # Format schedule as markdown table
    schedule_table = format_schedule_as_markdown(schedule_data)
    
    # Prepare all replacements
    replacements = {
        'COURSE_ID': course_id or 'COURSE XXX',
        'COURSE_TITLE': course_title,
        'SEMESTER': semester.title(),
        'YEAR': str(year),
        'INSTRUCTOR_NAME': instructor_name,
        'COURSE_DESCRIPTION': course_description,
        'DEPARTMENT_MISSION_STATEMENT': department_mission_statement,
        'SCHEDULE_TABLE': schedule_table,
        'TEXTBOOKS': kwargs.get('textbooks', '; '.join(course_textbooks) if course_textbooks else 'Please list textbook information here.'),
        'ASSIGNMENTS': kwargs.get('assignments', 'Please list assignments here providing clear explanations regarding the nature, length, grade percentage, and due dates for each major assignment.'),
        'ATTENDANCE_POLICY': kwargs.get('attendance_policy', 'Please explain the course attendance policy here.'),
        'GRADING_POLICY': kwargs.get('grading_policy', 'Please explain course grading policies and procedures here.'),
        'AI_POLICY': kwargs.get('ai_policy', 'Please select appropriate AI policy for your course.'),
        'BIBLIOGRAPHY': kwargs.get('bibliography', 'If appropriate, include required readings and other supplementary materials.')
    }
    
    # Replace all placeholders
    final_content = replace_placeholders(template_content, replacements)
    
    return final_content


def convert_markdown_to_format(markdown_content, output_format, template_dir=None, output_file=None):
    """Convert markdown to specified format using pandoc"""
    
    pandoc_args = ['--standalone']
    
    # Format-specific arguments (using pandoc defaults since custom templates deleted)
    if output_format == 'pdf':
        pandoc_args.extend(['--pdf-engine=pdflatex'])
    
    # Convert using pandoc
    if output_file:
        pypandoc.convert_text(
            markdown_content, 
            output_format, 
            format='md', 
            extra_args=pandoc_args,
            outputfile=output_file
        )
        return ""
    else:
        return pypandoc.convert_text(
            markdown_content, 
            output_format, 
            format='md', 
            extra_args=pandoc_args
        )


def generate_syllabus(schedule_data, semester, year, output_format, template_dir=None, output_file=None, **kwargs):
    """Main function to generate syllabus in any format from markdown"""
    
    # Generate markdown content
    markdown_content = generate_syllabus_markdown(
        schedule_data, semester, year, **kwargs
    )
    
    # Convert to requested format
    if output_format == 'md' or output_format == 'markdown':
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            return ""
        return markdown_content
    else:
        return convert_markdown_to_format(
            markdown_content, output_format, template_dir, output_file
        )
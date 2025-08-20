#!/usr/bin/env python

"""
Enhanced DOCX editing capabilities for Niagara University Scheduler

Features:
- Direct DOCX template manipulation
- Dynamic content replacement
- Table editing for schedules
- Header/footer customization
- Styling and formatting control
"""

import os
from core.course_descriptions import CourseDescriptionManager

def create_enhanced_docx_editor():
    """Check if python-docx is available and provide enhanced editing"""
    try:
        from docx import Document
        from docx.shared import Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
        return True, Document, Inches, WD_ALIGN_PARAGRAPH, WD_TABLE_ALIGNMENT
    except ImportError:
        return False, None, None, None, None

def enhance_syllabus_docx(template_path, schedule_data, output_path, semester, year):
    """Create enhanced DOCX syllabus with direct document manipulation"""
    
    available, Document, Inches, WD_ALIGN_PARAGRAPH, WD_TABLE_ALIGNMENT = create_enhanced_docx_editor()
    
    if not available:
        print("python-docx not available. Using fallback PyPandoc method.")
        return False
    
    try:
        # Load template document
        doc = Document(template_path)
        
        # Replace template variables
        replace_text_in_document(doc, '{{SEMESTER}}', semester.title())
        replace_text_in_document(doc, '{{YEAR}}', str(year))
        replace_text_in_document(doc, '{{SEMESTER_YEAR}}', f"{semester.title()} {year}")
        
        # Add schedule table
        add_schedule_table(doc, schedule_data)
        
        # Save enhanced document
        doc.save(output_path)
        return True
        
    except Exception as e:
        print(f"Error creating enhanced DOCX: {e}")
        return False

def replace_text_in_document(doc, old_text, new_text):
    """Replace text throughout the document including headers and footers"""
    
    # Replace in main document
    for paragraph in doc.paragraphs:
        if old_text in paragraph.text:
            paragraph.text = paragraph.text.replace(old_text, new_text)
    
    # Replace in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if old_text in paragraph.text:
                        paragraph.text = paragraph.text.replace(old_text, new_text)
    
    # Replace in headers and footers
    for section in doc.sections:
        # Header
        if section.header:
            for paragraph in section.header.paragraphs:
                if old_text in paragraph.text:
                    paragraph.text = paragraph.text.replace(old_text, new_text)
        
        # Footer
        if section.footer:
            for paragraph in section.footer.paragraphs:
                if old_text in paragraph.text:
                    paragraph.text = paragraph.text.replace(old_text, new_text)

def add_schedule_table(doc, schedule_data):
    """Add a formatted schedule table to the document"""
    
    available, Document, Inches, WD_ALIGN_PARAGRAPH, WD_TABLE_ALIGNMENT = create_enhanced_docx_editor()
    
    if not available or not schedule_data:
        return
    
    # Find placeholder for schedule or add at end
    schedule_placeholder = None
    for paragraph in doc.paragraphs:
        if '{{SCHEDULE}}' in paragraph.text or '[CLASS SCHEDULE]' in paragraph.text.upper():
            schedule_placeholder = paragraph
            break
    
    if schedule_placeholder:
        # Clear placeholder text
        schedule_placeholder.clear()
        schedule_placeholder.text = "Class Schedule:"
    else:
        # Add new heading
        doc.add_heading('Class Schedule', level=2)
    
    # Create table
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Use a more universal table style or none at all
    try:
        table.style = 'Table Grid'
    except:
        # Fallback if style doesn't exist
        pass
    
    # Header row
    header_cells = table.rows[0].cells
    header_cells[0].text = 'Date'
    header_cells[1].text = 'Class/Event'
    
    # Add schedule data
    for entry in schedule_data:
        row_cells = table.add_row().cells
        
        # Parse date and event from schedule entry
        if ' - ' in entry:
            date_part, event_part = entry.split(' - ', 1)
            row_cells[0].text = date_part
            row_cells[1].text = event_part
        else:
            row_cells[0].text = entry
            row_cells[1].text = 'Regular Class'
    
    # Format table
    for row in table.rows:
        for cell in row.cells:
            # Center align dates, left align events
            if cell == row.cells[0]:  # Date column
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:  # Event column
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

def create_custom_syllabus_template():
    """Create a custom DOCX template with placeholders"""
    
    available, Document, Inches, WD_ALIGN_PARAGRAPH, WD_TABLE_ALIGNMENT = create_enhanced_docx_editor()
    
    if not available:
        return False, "python-docx not available"
    
    try:
        doc = Document()
        
        # Header
        header = doc.sections[0].header
        header_para = header.paragraphs[0]
        header_para.text = "Niagara University - {{SEMESTER}} {{YEAR}}"
        header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Title
        title = doc.add_heading('Course Syllabus', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Course info section
        doc.add_heading('Course Information', level=1)
        
        info_table = doc.add_table(rows=4, cols=2)
        try:
            info_table.style = 'Table Grid'
        except:
            # Fallback if style doesn't exist
            pass
        
        # Course details
        course_info = [
            ('Course Title:', '{{COURSE_TITLE}}'),
            ('Instructor:', '{{INSTRUCTOR_NAME}}'),
            ('Email:', '{{INSTRUCTOR_EMAIL}}'),
            ('Office Hours:', '{{OFFICE_HOURS}}')
        ]
        
        for i, (label, placeholder) in enumerate(course_info):
            info_table.rows[i].cells[0].text = label
            info_table.rows[i].cells[1].text = placeholder
        
        # Schedule section
        doc.add_heading('Class Schedule', level=1)
        doc.add_paragraph('{{SCHEDULE}}')
        
        # Additional sections
        doc.add_heading('Course Objectives', level=1)
        doc.add_paragraph('{{OBJECTIVES}}')
        
        doc.add_heading('Required Materials', level=1)
        doc.add_paragraph('{{MATERIALS}}')
        
        doc.add_heading('Grading Policy', level=1)
        doc.add_paragraph('{{GRADING_POLICY}}')
        
        doc.add_heading('Attendance Policy', level=1)
        doc.add_paragraph('{{ATTENDANCE_POLICY}}')
        
        # Footer
        footer = doc.sections[0].footer
        footer_para = footer.paragraphs[0]
        footer_para.text = "Generated by Niagara University Scheduler"
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        return True, doc
        
    except Exception as e:
        return False, str(e)

def install_docx_support():
    """Check if python-docx is installed, offer to install if not"""
    try:
        import docx
        return True, "python-docx is already installed"
    except ImportError:
        return False, "python-docx is not installed. Install with: pip install python-docx"

def enhance_docx_with_description(doc, course_id=None, include_description=False):
    """Enhance DOCX document with course description"""
    if not include_description or not course_id:
        return
    
    # Data file path relative to project root
    project_root = os.path.dirname(os.path.dirname(__file__))
    data_file = os.path.join(project_root, 'data', 'courses.json')
    manager = CourseDescriptionManager(data_file)
    description = manager.get_course_description(course_id)
    
    replace_text_in_document(doc, '{{COURSE_DESCRIPTION}}', description)
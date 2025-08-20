#!/usr/bin/env python

"""
DOCX Tools for Niagara University Scheduler

Command-line utilities for enhanced DOCX operations:
- Create custom syllabus templates
- Check DOCX editing capabilities
- Generate enhanced syllabi
"""

import argparse
import sys
import os
from core.docx_editor import create_custom_syllabus_template, install_docx_support, enhance_syllabus_docx

def check_capabilities():
    """Check if enhanced DOCX editing is available"""
    available, message = install_docx_support()
    
    if available:
        print("✅ Enhanced DOCX editing is available")
        print("   - Direct document manipulation")
        print("   - Template variable replacement") 
        print("   - Dynamic table generation")
        print("   - Header/footer customization")
    else:
        print("❌ Enhanced DOCX editing is not available")
        print(f"   {message}")
        print("\nTo enable enhanced DOCX features:")
        print("   pip install python-docx")
    
    return available

def create_template(output_path):
    """Create a custom syllabus template"""
    success, result = create_custom_syllabus_template()
    
    if success:
        try:
            result.save(output_path)
            print(f"✅ Custom syllabus template created: {output_path}")
            print("\nTemplate includes placeholders for:")
            print("   - {{SEMESTER}} {{YEAR}}")
            print("   - {{COURSE_TITLE}}")
            print("   - {{INSTRUCTOR_NAME}}")
            print("   - {{INSTRUCTOR_EMAIL}}")
            print("   - {{OFFICE_HOURS}}")
            print("   - {{SCHEDULE}}")
            print("   - {{OBJECTIVES}}")
            print("   - {{MATERIALS}}")
            print("   - {{GRADING_POLICY}}")
            print("   - {{ATTENDANCE_POLICY}}")
            return True
        except Exception as e:
            print(f"❌ Error saving template: {e}")
            return False
    else:
        print(f"❌ Error creating template: {result}")
        return False

def enhance_existing_template(template_path, output_path, semester="Fall", year="2025"):
    """Enhance an existing template with sample data"""
    
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False
    
    # Sample schedule data
    sample_schedule = [
        "Monday, August 25, 2025",
        "Wednesday, August 27, 2025", 
        "Friday, August 29, 2025",
        "Monday, September 1, 2025 - NO CLASS (Labor Day)",
        "Wednesday, September 3, 2025",
        "Friday, September 5, 2025 - Graduate Start End"
    ]
    
    success = enhance_syllabus_docx(template_path, sample_schedule, output_path, semester, year)
    
    if success:
        print(f"✅ Enhanced syllabus created: {output_path}")
        print(f"   Semester: {semester} {year}")
        print(f"   Schedule entries: {len(sample_schedule)}")
        return True
    else:
        print(f"❌ Error enhancing template")
        return False

def main():
    parser = argparse.ArgumentParser(description='DOCX Tools for Niagara University Scheduler')
    parser.add_argument('command', choices=['check', 'create-template', 'enhance'],
                       help='Command to execute')
    parser.add_argument('--output', '-o', 
                       help='Output file path')
    parser.add_argument('--template', '-t',
                       help='Template file path (for enhance command)')
    parser.add_argument('--semester', 
                       default='Fall',
                       help='Semester name (default: Fall)')
    parser.add_argument('--year',
                       default='2025', 
                       help='Year (default: 2025)')
    
    args = parser.parse_args()
    
    if args.command == 'check':
        check_capabilities()
    
    elif args.command == 'create-template':
        if not args.output:
            print("❌ Output path required for create-template command")
            print("Usage: python docx_tools.py create-template --output template.docx")
            sys.exit(1)
        create_template(args.output)
    
    elif args.command == 'enhance':
        if not args.template:
            print("❌ Template path required for enhance command")
            print("Usage: python docx_tools.py enhance --template template.docx --output output.docx")
            sys.exit(1)
        if not args.output:
            print("❌ Output path required for enhance command")
            sys.exit(1)
        enhance_existing_template(args.template, args.output, args.semester, args.year)

if __name__ == '__main__':
    main()
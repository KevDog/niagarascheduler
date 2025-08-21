#!/usr/bin/env python

import json
import os
from core.department import Department
from core.course import Course


def migrate_courses_to_departments(courses_file, output_dir):
    """Migrate existing courses.json to department-specific JSON files"""
    
    # Load existing courses data
    with open(courses_file, 'r') as f:
        courses_data = json.load(f)
    
    # Group courses by department
    departments = {}
    
    for course_id, course_info in courses_data.items():
        dept_name = course_info.get("department", "Unknown")
        
        if dept_name not in departments:
            departments[dept_name] = {
                "name": dept_name,
                "courses": []
            }
        
        # Extract course number from course_id (e.g., "THR 101" -> "101")
        course_number = course_id.split()[-1] if " " in course_id else course_id
        
        # Create course with new object model structure
        course = Course(
            number=course_number,
            title=course_info.get("title"),
            description=course_info.get("description")
        )
        
        departments[dept_name]["courses"].append(course)
    
    # Write department-specific JSON files
    for dept_name, dept_data in departments.items():
        # Create department abbreviation from name
        dept_abbrev = get_department_abbreviation(dept_name)
        
        # Create Department object
        department = Department(
            name=dept_name,
            courses=dept_data["courses"]
        )
        
        # Write to department-specific file
        output_file = os.path.join(output_dir, f"{dept_abbrev}.json")
        with open(output_file, 'w') as f:
            f.write(department.to_json())


def get_department_abbreviation(dept_name):
    """Get department abbreviation from name"""
    abbreviations = {
        "Theater Arts": "THR",
        "Mathematics": "MATH"
    }
    return abbreviations.get(dept_name, dept_name[:4].upper())
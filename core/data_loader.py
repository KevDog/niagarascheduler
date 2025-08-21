#!/usr/bin/env python

import json
import os
from core.department import Department
from core.course import Course


class DepartmentDataLoader:
    def __init__(self, data_directory):
        """Initialize loader with directory containing department JSON files"""
        self.data_directory = data_directory
    
    def load_department(self, department_abbreviation):
        """Load Department object from JSON file"""
        file_path = os.path.join(self.data_directory, f"{department_abbreviation}.json")
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r') as f:
            dept_data = json.load(f)
        
        # Convert course dictionaries to Course objects
        courses = []
        for course_data in dept_data.get("courses", []):
            courses.append(Course.from_dict(course_data))
        
        # Create Department object
        return Department(
            name=dept_data.get("name"),
            mission_statement=dept_data.get("mission_statement"),
            office=dept_data.get("office"),
            course_listing_url=dept_data.get("course_listing_url"),
            courses=courses
        )
    
    def find_course(self, course_id):
        """Find specific course by course ID (e.g., 'THR 201')"""
        # Parse course ID to get department and number
        parts = course_id.split()
        if len(parts) != 2:
            return None
        
        dept_abbrev, course_number = parts
        
        # Load department
        department = self.load_department(dept_abbrev)
        if not department:
            return None
        
        # Find course by number
        for course in department.courses:
            if course.number == course_number:
                return course
        
        return None
    
    def get_all_departments(self):
        """Get list of all available department abbreviations"""
        departments = []
        for filename in os.listdir(self.data_directory):
            if filename.endswith('.json'):
                dept_abbrev = filename[:-5]  # Remove .json extension
                departments.append(dept_abbrev)
        return departments
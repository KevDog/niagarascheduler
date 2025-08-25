#!/usr/bin/env python

import unittest
import json
import os
import tempfile
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.data_loader import DepartmentDataLoader
from core.department import Department
from core.course import Course


class TestDataLoader(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.test_department_data = {
            "name": "Theater Arts",
            "mission_statement": "Excellence in theater education",
            "office": "CAM 201",
            "course_listing_url": "https://catalog.niagara.edu/theater",
            "courses": [
                {
                    "number": "101",
                    "title": "Introduction to Theater",
                    "description": "Basic theater course",
                    "instructors": ["Dr. Smith"],
                    "textbooks": ["Theater Basics"],
                    "zoom_link": None,
                    "meeting_days": ["Monday", "Wednesday"]
                },
                {
                    "number": "201", 
                    "title": "Advanced Acting",
                    "description": "Advanced acting techniques",
                    "instructors": ["Prof. Johnson"],
                    "textbooks": ["Method Acting"],
                    "zoom_link": "https://zoom.us/j/123",
                    "meeting_days": ["Tuesday", "Thursday"]
                }
            ]
        }
    
    def test_load_department_from_json_file(self):
        """Load Department object from JSON file"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            dept_file = os.path.join(temp_dir, "THR.json")
            with open(dept_file, 'w') as f:
                json.dump(self.test_department_data, f)
            
            loader = DepartmentDataLoader(temp_dir)
            
            # Act
            department = loader.load_department("THR")
            
            # Assert
            self.assertIsInstance(department, Department)
            self.assertEqual(department.name, "Theater Arts")
            self.assertEqual(department.mission_statement, "Excellence in theater education")
            self.assertEqual(len(department.courses), 2)
            
            # Check first course
            course1 = department.courses[0]
            self.assertIsInstance(course1, Course)
            self.assertEqual(course1.number, "101")
            self.assertEqual(course1.title, "Introduction to Theater")
            self.assertEqual(course1.instructors, ["Dr. Smith"])
    
    def test_find_course_by_id(self):
        """Find specific course by course ID across departments"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            dept_file = os.path.join(temp_dir, "THR.json")
            with open(dept_file, 'w') as f:
                json.dump(self.test_department_data, f)
            
            loader = DepartmentDataLoader(temp_dir)
            
            # Act
            course = loader.find_course("THR 201")
            
            # Assert
            self.assertIsInstance(course, Course)
            self.assertEqual(course.number, "201")
            self.assertEqual(course.title, "Advanced Acting")
            self.assertEqual(course.zoom_link, "https://zoom.us/j/123")


if __name__ == '__main__':
    unittest.main()
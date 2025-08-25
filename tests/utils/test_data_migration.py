#!/usr/bin/env python

import unittest
import json
import os
import tempfile
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.data_migration import migrate_courses_to_departments


class TestDataMigration(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.test_courses_data = {
            "THR 101": {
                "title": "Introduction to Theater",
                "description": "Basic theater course",
                "credits": 3,
                "department": "Theater Arts"
            },
            "THR 201": {
                "title": "Advanced Acting",
                "description": "Advanced acting techniques",
                "credits": 3,
                "department": "Theater Arts"
            },
            "MATH 101": {
                "title": "College Algebra",
                "description": "Fundamental algebra",
                "credits": 4,
                "department": "Mathematics"
            }
        }
    
    def test_migrate_courses_to_department_files(self):
        """Migrate existing courses.json to department-specific files"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test courses.json
            courses_file = os.path.join(temp_dir, "courses.json")
            with open(courses_file, 'w') as f:
                json.dump(self.test_courses_data, f)
            
            # Act
            migrate_courses_to_departments(courses_file, temp_dir)
            
            # Assert
            thr_file = os.path.join(temp_dir, "THR.json")
            math_file = os.path.join(temp_dir, "MATH.json")
            
            self.assertTrue(os.path.exists(thr_file))
            self.assertTrue(os.path.exists(math_file))
            
            # Check THR.json content
            with open(thr_file, 'r') as f:
                thr_data = json.load(f)
            
            self.assertEqual(thr_data["name"], "Theater Arts")
            self.assertEqual(len(thr_data["courses"]), 2)
            self.assertEqual(thr_data["courses"][0]["number"], "101")
            self.assertEqual(thr_data["courses"][1]["number"], "201")


if __name__ == '__main__':
    unittest.main()
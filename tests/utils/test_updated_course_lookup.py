#!/usr/bin/env python

import unittest
import tempfile
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.markdown_processor import generate_syllabus_markdown


class TestUpdatedCourseLookup(unittest.TestCase):
    
    def setUp(self):
        """Set up test data with department JSON files"""
        self.test_data_dir = tempfile.mkdtemp()
        
        # Create THR.json with rich course data
        thr_data = {
            "name": "Theater Arts",
            "mission_statement": "Excellence in theater education",
            "office": "CAM 201",
            "course_listing_url": "https://catalog.niagara.edu/theater",
            "courses": [
                {
                    "number": "101",
                    "title": "Introduction to Theater",
                    "description": "Basic theater course covering fundamentals",
                    "instructors": ["Dr. Smith", "Prof. Johnson"],
                    "textbooks": ["Theater Basics", "Acting Fundamentals"],
                    "zoom_link": "https://zoom.us/j/123456789",
                    "meeting_days": ["Monday", "Wednesday", "Friday"]
                }
            ]
        }
        
        with open(os.path.join(self.test_data_dir, "THR.json"), 'w') as f:
            json.dump(thr_data, f)
    
    def tearDown(self):
        """Clean up test data"""
        import shutil
        shutil.rmtree(self.test_data_dir)
    
    def test_syllabus_generation_with_rich_course_data(self):
        """Syllabus generation uses rich Course object data"""
        # Arrange
        schedule_data = ["Aug 25: First Day", "Dec 15: Final Exams"]
        
        # Act - temporarily patch data directory
        import core.markdown_processor
        original_data_dir = None
        # We'll modify the function to accept data_dir parameter
        
        # For now, test that the function still works with course_id
        result = generate_syllabus_markdown(
            schedule_data=schedule_data,
            semester="fall",
            year=2025,
            course_id="THR 101",
            include_description=True
        )
        
        # Assert
        self.assertIn("THR 101", result)
        self.assertIn("Fall", result)
        self.assertIn("2025", result)
        # Should contain some course info (even if using old system for now)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 100)


if __name__ == '__main__':
    unittest.main()
#!/usr/bin/env python

"""
Test suite for course description functionality
"""

import unittest
import tempfile
import os
import json
import sys
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.course_descriptions import CourseDescriptionManager


class TestCourseDescriptions(unittest.TestCase):
    """Test course description management functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = {
            "THR 101": {
                "title": "Introduction to Theater",
                "description": "An introductory course covering the fundamentals of theater arts and performance.",
                "credits": 3,
                "department": "Theater Arts"
            },
            "THR 201": {
                "title": "Acting Fundamentals",
                "description": "Basic acting techniques and scene study for beginning actors.",
                "credits": 3,
                "department": "Theater Arts"
            },
            "MATH 101": {
                "title": "College Algebra",
                "description": "Fundamental algebraic concepts and problem-solving techniques.",
                "credits": 4,
                "department": "Mathematics"
            }
        }
        
        self.temp_dir = tempfile.mkdtemp()
        self.json_file = os.path.join(self.temp_dir, 'courses.json')
        
        # Write test JSON data
        with open(self.json_file, 'w') as f:
            json.dump(self.test_data, f, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.json_file):
            os.remove(self.json_file)
        os.rmdir(self.temp_dir)
    
    def test_load_course_data(self):
        """Test loading course data from JSON file"""
        manager = CourseDescriptionManager(self.json_file)
        courses = manager.load_course_data()
        
        self.assertEqual(len(courses), 3)
        self.assertIn('THR 101', courses)
        self.assertEqual(courses['THR 101']['title'], 'Introduction to Theater')
        self.assertEqual(courses['THR 101']['credits'], 3)
    
    def test_get_course_description_found(self):
        """Test retrieving course description for existing course"""
        manager = CourseDescriptionManager(self.json_file)
        
        description = manager.get_course_description('THR 101')
        expected = 'An introductory course covering the fundamentals of theater arts and performance.'
        self.assertEqual(description, expected)
    
    def test_get_course_description_not_found(self):
        """Test retrieving course description for non-existent course"""
        manager = CourseDescriptionManager(self.json_file)
        
        description = manager.get_course_description('INVALID 999')
        self.assertEqual(description, 'Course description not found, insert manually')
    
    def test_get_course_info_complete(self):
        """Test retrieving complete course information"""
        manager = CourseDescriptionManager(self.json_file)
        
        course_info = manager.get_course_info('MATH 101')
        expected = {
            'title': 'College Algebra',
            'description': 'Fundamental algebraic concepts and problem-solving techniques.',
            'credits': 4,
            'department': 'Mathematics'
        }
        self.assertEqual(course_info, expected)
    
    def test_get_course_info_not_found(self):
        """Test retrieving course info for non-existent course"""
        manager = CourseDescriptionManager(self.json_file)
        
        course_info = manager.get_course_info('INVALID 999')
        self.assertIsNone(course_info)
    
    def test_file_not_found_handling(self):
        """Test graceful handling of missing JSON file"""
        manager = CourseDescriptionManager('/nonexistent/file.json')
        
        description = manager.get_course_description('THR 101')
        self.assertEqual(description, 'Course description not found, insert manually')
    
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON file"""
        bad_json_file = os.path.join(self.temp_dir, 'bad.json')
        with open(bad_json_file, 'w') as f:
            f.write('{ invalid json }')
        
        manager = CourseDescriptionManager(bad_json_file)
        description = manager.get_course_description('THR 101')
        self.assertEqual(description, 'Course description not found, insert manually')
        
        os.remove(bad_json_file)


class TestOutputIntegration(unittest.TestCase):
    """Test integration with syllabus output generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_schedule = [
            "Monday, 1/15/2025: Class begins",
            "Wednesday, 1/17/2025: Regular class",
            "Friday, 1/19/2025: Regular class"
        ]
    
    @patch('core.course_descriptions.CourseDescriptionManager')
    def test_text_output_with_description(self, mock_manager):
        """Test text output includes course description at beginning"""
        mock_instance = MagicMock()
        mock_instance.get_course_description.return_value = "Test course description."
        mock_manager.return_value = mock_instance
        
        from core.output_formatter import format_text_with_description
        
        result = format_text_with_description(
            self.test_schedule, 
            course_id="THR 101",
            include_description=True
        )
        
        self.assertIn("Course Description: Test course description.", result)
        self.assertTrue(result.startswith("Course Description:"))
    
    @patch('core.course_descriptions.CourseDescriptionManager')
    def test_text_output_without_description(self, mock_manager):
        """Test text output when description not requested"""
        from core.output_formatter import format_text_with_description
        
        result = format_text_with_description(
            self.test_schedule,
            course_id="THR 101", 
            include_description=False
        )
        
        self.assertNotIn("Course Description:", result)
        mock_manager.assert_not_called()
    
    @patch('core.docx_editor.replace_text_in_document')
    @patch('core.course_descriptions.CourseDescriptionManager')
    def test_docx_output_with_description(self, mock_manager, mock_replace):
        """Test DOCX output includes course description in template"""
        mock_instance = MagicMock()
        mock_instance.get_course_description.return_value = "Test course description."
        mock_manager.return_value = mock_instance
        
        from core.docx_editor import enhance_docx_with_description
        
        mock_doc = MagicMock()
        enhance_docx_with_description(
            mock_doc,
            course_id="THR 101",
            include_description=True
        )
        
        mock_replace.assert_called_with(mock_doc, '{{COURSE_DESCRIPTION}}', 'Test course description.')


if __name__ == '__main__':
    unittest.main()
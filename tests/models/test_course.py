#!/usr/bin/env python

import unittest
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.course import Course


class TestCourse(unittest.TestCase):
    
    def test_course_has_number(self):
        """A course has a number"""
        # Arrange
        course_number = "101"
        
        # Act
        course = Course(course_number)
        
        # Assert
        self.assertEqual(course.number, course_number)
    
    def test_course_has_title(self):
        """A course has a title"""
        # Arrange
        course_number = "101"
        course_title = "Introduction to Theater"
        
        # Act
        course = Course(course_number, title=course_title)
        
        # Assert
        self.assertEqual(course.title, course_title)
    
    def test_course_has_description(self):
        """A course has a description"""
        # Arrange
        course_number = "101"
        course_description = "An introductory course covering the fundamentals of theatrical performance and production."
        
        # Act
        course = Course(course_number, description=course_description)
        
        # Assert
        self.assertEqual(course.description, course_description)
    
    def test_course_has_instructors(self):
        """A course has one or more instructors"""
        # Arrange
        course_number = "101"
        instructors = ["Dr. Smith", "Prof. Johnson"]
        
        # Act
        course = Course(course_number, instructors=instructors)
        
        # Assert
        self.assertEqual(course.instructors, instructors)
    
    def test_course_has_textbooks(self):
        """A course has zero to many textbooks"""
        # Arrange
        course_number = "101"
        textbooks = ["Theater: The Lively Art", "Acting for the Camera"]
        
        # Act
        course = Course(course_number, textbooks=textbooks)
        
        # Assert
        self.assertEqual(course.textbooks, textbooks)
    
    def test_course_may_have_zoom_link(self):
        """A course may have a zoom link"""
        # Arrange
        course_number = "101"
        zoom_link = "https://zoom.us/j/123456789"
        
        # Act
        course = Course(course_number, zoom_link=zoom_link)
        
        # Assert
        self.assertEqual(course.zoom_link, zoom_link)
    
    def test_course_defaults_empty_lists(self):
        """A course has empty lists for instructors and textbooks by default"""
        # Arrange
        course_number = "101"
        
        # Act
        course = Course(course_number)
        
        # Assert
        self.assertEqual(course.instructors, [])
        self.assertEqual(course.textbooks, [])
    
    def test_course_to_dict(self):
        """Course has to_dict method that serializes all properties"""
        # Arrange
        course = Course(
            number="101",
            title="Introduction to Theater",
            description="Basic theater course",
            instructors=["Dr. Smith"],
            textbooks=["Theater Basics"],
            zoom_link="https://zoom.us/j/123"
        )
        
        # Act
        result = course.to_dict()
        
        # Assert
        expected = {
            "number": "101",
            "title": "Introduction to Theater", 
            "description": "Basic theater course",
            "instructors": ["Dr. Smith"],
            "textbooks": ["Theater Basics"],
            "zoom_link": "https://zoom.us/j/123"
        }
        self.assertEqual(result, expected)
    
    def test_course_from_dict(self):
        """Course has from_dict class method that creates object from dictionary"""
        # Arrange
        course_data = {
            "number": "202",
            "title": "Advanced Acting",
            "description": "Advanced techniques",
            "instructors": ["Prof. Johnson", "Dr. Lee"],
            "textbooks": ["Method Acting", "Scene Study"],
            "zoom_link": "https://zoom.us/j/456"
        }
        
        # Act
        course = Course.from_dict(course_data)
        
        # Assert
        self.assertEqual(course.number, "202")
        self.assertEqual(course.title, "Advanced Acting")
        self.assertEqual(course.description, "Advanced techniques")
        self.assertEqual(course.instructors, ["Prof. Johnson", "Dr. Lee"])
        self.assertEqual(course.textbooks, ["Method Acting", "Scene Study"])
        self.assertEqual(course.zoom_link, "https://zoom.us/j/456")


if __name__ == '__main__':
    unittest.main()
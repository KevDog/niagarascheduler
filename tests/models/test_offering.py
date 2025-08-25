#!/usr/bin/env python

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.offering import Offering


class TestOffering(unittest.TestCase):
    
    def test_offering_has_code(self):
        """An offering has a code"""
        # Arrange
        offering_code = "THR101A"
        
        # Act
        offering = Offering(offering_code)
        
        # Assert
        self.assertEqual(offering.code, offering_code)
    
    def test_offering_parses_department_from_code(self):
        """An offering parses department from code"""
        # Arrange
        offering_code = "THR101A"
        
        # Act
        offering = Offering(offering_code)
        
        # Assert
        self.assertEqual(offering.department, "THR")
    
    def test_offering_parses_number_from_code(self):
        """An offering parses number from code"""
        # Arrange
        offering_code = "THR101A"
        
        # Act
        offering = Offering(offering_code)
        
        # Assert
        self.assertEqual(offering.number, "101")
    
    def test_offering_parses_type_from_code(self):
        """An offering parses type from code"""
        # Arrange - Test both regular and lab offerings
        regular_offering = Offering("THR101A")
        lab_offering = Offering("ACC425LA")
        
        # Act & Assert
        self.assertEqual(regular_offering.type, "")
        self.assertEqual(lab_offering.type, "L")
    
    def test_offering_parses_section_from_code(self):
        """An offering parses section from code"""
        # Arrange
        offering_a = Offering("THR101A")
        offering_b = Offering("ACC425LB")
        
        # Act & Assert
        self.assertEqual(offering_a.section, "A")
        self.assertEqual(offering_b.section, "B")
    
    def test_offering_has_delivery_type(self):
        """An offering has delivery type"""
        # Arrange
        delivery_type = "In-Person"
        
        # Act
        offering = Offering("THR101A", delivery_type=delivery_type)
        
        # Assert
        self.assertEqual(offering.delivery_type, delivery_type)
    
    def test_offering_has_designation(self):
        """An offering has designation"""
        # Arrange
        designation = "Core Requirement"
        
        # Act
        offering = Offering("THR101A", designation=designation)
        
        # Assert
        self.assertEqual(offering.designation, designation)
    
    def test_offering_has_credits_with_decimal_precision(self):
        """An offering has credits with decimal precision"""
        # Arrange
        credits = 3.50
        
        # Act
        offering = Offering("THR101A", credits=credits)
        
        # Assert
        self.assertEqual(offering.credits, credits)
        self.assertIsInstance(offering.credits, float)
    
    def test_offering_has_instructors(self):
        """An offering has instructors"""
        # Arrange
        instructors = ["Dr. Smith", "Prof. Johnson"]
        
        # Act
        offering = Offering("THR101A", instructors=instructors)
        
        # Assert
        self.assertEqual(offering.instructors, instructors)
    
    def test_offering_has_textbooks(self):
        """An offering has textbooks"""
        # Arrange
        textbooks = ["Theater Basics", "Acting Fundamentals"]
        
        # Act
        offering = Offering("THR101A", textbooks=textbooks)
        
        # Assert
        self.assertEqual(offering.textbooks, textbooks)
    
    def test_offering_has_zoom_link(self):
        """An offering has zoom link"""
        # Arrange
        zoom_link = "https://zoom.us/j/123456789"
        
        # Act
        offering = Offering("THR101A", zoom_link=zoom_link)
        
        # Assert
        self.assertEqual(offering.zoom_link, zoom_link)
    
    def test_offering_has_meeting_days(self):
        """An offering has meeting days"""
        # Arrange
        meeting_days = ["Monday", "Wednesday", "Friday"]
        
        # Act
        offering = Offering("THR101A", meeting_days=meeting_days)
        
        # Assert
        self.assertEqual(offering.meeting_days, meeting_days)


if __name__ == '__main__':
    unittest.main()
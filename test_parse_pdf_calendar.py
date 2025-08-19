#!/usr/bin/env python

import unittest
import arrow
from unittest.mock import patch, mock_open
from niagarascheduler import parse_pdf_calendar

class TestParsePDFCalendar(unittest.TestCase):
    
    def setUp(self):
        self.sample_pdf_text = """
        Academic Calendar 2024-2025
        
        August 26, 2024 - First Day of Classes
        September 2, 2024 - Labor Day - No Classes
        October 14, 2024 - Columbus Day - No Classes
        November 28-29, 2024 - Thanksgiving Break - No Classes
        December 13, 2024 - Last Day of Classes
        December 16-20, 2024 - Final Examinations
        """
    
    @patch('niagarascheduler.extract_text_from_pdf')
    def test_parse_pdf_calendar_complete(self, mock_extract):
        """Test parsing complete PDF calendar with all components"""
        mock_extract.return_value = self.sample_pdf_text
        
        first_day, last_day, no_classes = parse_pdf_calendar("dummy_path.pdf")
        
        self.assertEqual(len(first_day), 1)
        self.assertEqual(first_day[0], arrow.get(2024, 8, 26))
        
        self.assertEqual(len(last_day), 1)
        self.assertEqual(last_day[0], arrow.get(2024, 12, 13))
        
        self.assertEqual(len(no_classes), 4)
        expected_no_classes = [
            arrow.get(2024, 9, 2),
            arrow.get(2024, 10, 14),
            arrow.get(2024, 11, 28),
            arrow.get(2024, 11, 29)
        ]
        for date in expected_no_classes:
            self.assertIn(date, no_classes)
    
    @patch('niagarascheduler.extract_text_from_pdf')
    def test_parse_pdf_calendar_missing_first_day(self, mock_extract):
        """Test parsing PDF calendar missing first day"""
        incomplete_text = """
        Academic Calendar 2024-2025
        
        September 2, 2024 - Labor Day - No Classes
        December 13, 2024 - Last Day of Classes
        """
        mock_extract.return_value = incomplete_text
        
        first_day, last_day, no_classes = parse_pdf_calendar("dummy_path.pdf")
        
        self.assertEqual(len(first_day), 0)
        self.assertEqual(len(last_day), 1)
        self.assertEqual(last_day[0], arrow.get(2024, 12, 13))
    
    @patch('niagarascheduler.extract_text_from_pdf')
    def test_parse_pdf_calendar_missing_last_day(self, mock_extract):
        """Test parsing PDF calendar missing last day"""
        incomplete_text = """
        Academic Calendar 2024-2025
        
        August 26, 2024 - First Day of Classes
        September 2, 2024 - Labor Day - No Classes
        """
        mock_extract.return_value = incomplete_text
        
        first_day, last_day, no_classes = parse_pdf_calendar("dummy_path.pdf")
        
        self.assertEqual(len(first_day), 1)
        self.assertEqual(first_day[0], arrow.get(2024, 8, 26))
        self.assertEqual(len(last_day), 0)
    
    @patch('niagarascheduler.extract_text_from_pdf')
    def test_parse_pdf_calendar_no_holidays(self, mock_extract):
        """Test parsing PDF calendar with no holiday entries"""
        minimal_text = """
        Academic Calendar 2024-2025
        
        August 26, 2024 - First Day of Classes
        December 13, 2024 - Last Day of Classes
        """
        mock_extract.return_value = minimal_text
        
        first_day, last_day, no_classes = parse_pdf_calendar("dummy_path.pdf")
        
        self.assertEqual(len(first_day), 1)
        self.assertEqual(len(last_day), 1)
        self.assertEqual(len(no_classes), 0)
    
    @patch('niagarascheduler.extract_text_from_pdf')
    def test_parse_pdf_calendar_empty_text(self, mock_extract):
        """Test parsing PDF calendar with empty text"""
        mock_extract.return_value = ""
        
        first_day, last_day, no_classes = parse_pdf_calendar("dummy_path.pdf")
        
        self.assertEqual(len(first_day), 0)
        self.assertEqual(len(last_day), 0)
        self.assertEqual(len(no_classes), 0)
    
    @patch('niagarascheduler.extract_text_from_pdf')
    def test_parse_pdf_calendar_malformed_text(self, mock_extract):
        """Test parsing PDF calendar with malformed text"""
        malformed_text = """
        Some random text that doesn't match patterns
        Invalid date format - First Day of Classes
        Another invalid entry
        """
        mock_extract.return_value = malformed_text
        
        first_day, last_day, no_classes = parse_pdf_calendar("dummy_path.pdf")
        
        self.assertEqual(len(first_day), 0)
        self.assertEqual(len(last_day), 0)
        self.assertEqual(len(no_classes), 0)

if __name__ == '__main__':
    unittest.main()
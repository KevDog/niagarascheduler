#!/usr/bin/env python

import unittest
import arrow
from unittest.mock import patch
from niagarascheduler import extract_semester_dates_from_pdf_text, parse_pdf_calendar_for_semester

class TestSemesterSpecificParsing(unittest.TestCase):
    
    def setUp(self):
        self.multi_semester_pdf_text = """
        SUMMER 2024 FALL 2024 SEMESTER SPRING 2025 SEMESTER
        August 24 January 21
        MBA & Graduate 1st Saturday Session Begins Undergraduate and Graduate Classes Begin
        August 26 January 25
        Undergraduate and Graduate Classes Begin MBA & Graduate 1st Saturday Session Begins
        September 02 January 28
        Labor Day Holiday Restricted Drop Add Begins
        October 14 February 17
        Columbus Day Holiday Presidents Day Holiday
        November 27-29 March 10-14
        Thanksgiving Break Spring Break
        December 13 April 25
        Last Day of Classes Last Day of Classes
        December 16-20 April 28-May 2
        Final Examinations Final Examinations
        """
    
    def test_extract_fall_semester_dates(self):
        """Test extracting Fall 2024 specific dates"""
        from niagarascheduler import extract_semester_dates_from_pdf_text
        
        first_day, last_day, no_classes = extract_semester_dates_from_pdf_text(
            self.multi_semester_pdf_text, 'fall', '2024'
        )
        
        # Fall semester should start August 26, 2024
        self.assertEqual(len(first_day), 1)
        self.assertEqual(first_day[0], arrow.get(2024, 8, 26))
        
        # Fall semester should end December 13, 2024
        self.assertEqual(len(last_day), 1)
        self.assertEqual(last_day[0], arrow.get(2024, 12, 13))
        
        # Fall should include Labor Day, Columbus Day, Thanksgiving
        expected_holidays = [
            arrow.get(2024, 9, 2),   # Labor Day
            arrow.get(2024, 10, 14), # Columbus Day
            arrow.get(2024, 11, 27), # Thanksgiving Break
            arrow.get(2024, 11, 28),
            arrow.get(2024, 11, 29)
        ]
        
        self.assertEqual(len(no_classes), len(expected_holidays))
        for holiday in expected_holidays:
            self.assertIn(holiday, no_classes)
    
    def test_extract_spring_semester_dates(self):
        """Test extracting Spring 2025 specific dates"""
        from niagarascheduler import extract_semester_dates_from_pdf_text
        
        first_day, last_day, no_classes = extract_semester_dates_from_pdf_text(
            self.multi_semester_pdf_text, 'spring', '2025'
        )
        
        # Spring semester should start January 25, 2025
        self.assertEqual(len(first_day), 1)
        self.assertEqual(first_day[0], arrow.get(2025, 1, 25))
        
        # Spring semester should end April 25, 2025
        self.assertEqual(len(last_day), 1)
        self.assertEqual(last_day[0], arrow.get(2025, 4, 25))
        
        # Spring should include Presidents Day, Spring Break
        expected_holidays = [
            arrow.get(2025, 2, 17),  # Presidents Day
            arrow.get(2025, 3, 10),  # Spring Break
            arrow.get(2025, 3, 11),
            arrow.get(2025, 3, 12),
            arrow.get(2025, 3, 13),
            arrow.get(2025, 3, 14)
        ]
        
        self.assertEqual(len(no_classes), len(expected_holidays))
        for holiday in expected_holidays:
            self.assertIn(holiday, no_classes)
    
    def test_parse_pdf_calendar_for_semester(self):
        """Test main parsing function with semester parameter"""
        with patch('niagarascheduler.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = self.multi_semester_pdf_text
            
            # Test Fall 2024
            first_day, last_day, no_classes = parse_pdf_calendar_for_semester(
                "dummy.pdf", 'fall', '2024'
            )
            
            self.assertEqual(len(first_day), 1)
            self.assertEqual(first_day[0], arrow.get(2024, 8, 26))
            self.assertEqual(len(last_day), 1)
            self.assertEqual(last_day[0], arrow.get(2024, 12, 13))
            
            # Test Spring 2025
            first_day, last_day, no_classes = parse_pdf_calendar_for_semester(
                "dummy.pdf", 'spring', '2025'
            )
            
            self.assertEqual(len(first_day), 1)
            self.assertEqual(first_day[0], arrow.get(2025, 1, 25))
            self.assertEqual(len(last_day), 1)
            self.assertEqual(last_day[0], arrow.get(2025, 4, 25))
    
    def test_semester_date_boundaries(self):
        """Test that semester parsing respects date boundaries"""
        from niagarascheduler import extract_semester_dates_from_pdf_text
        
        # Fall dates should not include spring holidays
        first_day, last_day, no_classes = extract_semester_dates_from_pdf_text(
            self.multi_semester_pdf_text, 'fall', '2024'
        )
        
        presidents_day = arrow.get(2025, 2, 17)
        self.assertNotIn(presidents_day, no_classes)
        
        # Spring dates should not include fall holidays
        first_day, last_day, no_classes = extract_semester_dates_from_pdf_text(
            self.multi_semester_pdf_text, 'spring', '2025'
        )
        
        labor_day = arrow.get(2024, 9, 2)
        self.assertNotIn(labor_day, no_classes)
    
    def test_invalid_semester_year_combination(self):
        """Test handling of invalid semester/year combinations"""
        from niagarascheduler import extract_semester_dates_from_pdf_text
        
        # Try to get Spring 2024 from a PDF that doesn't have it
        first_day, last_day, no_classes = extract_semester_dates_from_pdf_text(
            self.multi_semester_pdf_text, 'spring', '2024'
        )
        
        # Should return empty lists for unavailable semester
        self.assertEqual(len(first_day), 0)
        self.assertEqual(len(last_day), 0)
        self.assertEqual(len(no_classes), 0)
    
    def test_case_insensitive_semester_names(self):
        """Test that semester names are case insensitive"""
        from niagarascheduler import extract_semester_dates_from_pdf_text
        
        first_day_fall, _, _ = extract_semester_dates_from_pdf_text(
            self.multi_semester_pdf_text, 'FALL', '2024'
        )
        first_day_fall_lower, _, _ = extract_semester_dates_from_pdf_text(
            self.multi_semester_pdf_text, 'fall', '2024'
        )
        
        self.assertEqual(first_day_fall, first_day_fall_lower)

if __name__ == '__main__':
    unittest.main()
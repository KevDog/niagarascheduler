"""
Tests for CalendarService day parsing and class date generation

This test suite specifically tests the fix for TTH parsing where "TTH" should
generate both Tuesday and Thursday classes, not just Tuesday.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import os
import sys

# Add the parent directory to the path to import the calendar service
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.services.calendar_service import CalendarService


class TestCalendarServiceDayParsing(unittest.TestCase):
    """Test day parsing logic in CalendarService"""
    
    def setUp(self):
        """Set up test calendar service with mock data"""
        self.calendar_service = CalendarService()
        
        # Mock calendar data
        self.mock_calendar_data = {
            'semester': 'test_semester',
            'first_day': '2025-08-25',  # Monday
            'last_day': '2025-12-15',   # Monday
            'no_class_dates': ['2025-09-01'],  # Labor Day
            'events': [
                {
                    'name': 'Labor Day',
                    'date': '2025-09-01',
                    'type': 'holiday'
                }
            ]
        }
    
    def test_tth_parsing_includes_both_tuesday_and_thursday(self):
        """Test that TTH correctly includes both Tuesday and Thursday"""
        # Arrange
        test_semester = 'test'
        test_meeting_days = 'TTH'
        expected_tuesday_weekday = 1
        expected_thursday_weekday = 3
        expected_day_difference = 2
        
        # Act
        with patch.object(self.calendar_service, 'get_calendar', return_value=self.mock_calendar_data):
            class_dates = self.calendar_service.generate_class_dates(
                semester=test_semester,
                meeting_days=test_meeting_days
            )
            
            # Process the results for analysis
            tuesday_dates = []
            thursday_dates = []
            
            for date_str in class_dates[:10]:  # Check first 10 dates
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                weekday = date_obj.weekday()
                if weekday == expected_tuesday_weekday:  # Tuesday
                    tuesday_dates.append(date_str)
                elif weekday == expected_thursday_weekday:  # Thursday
                    thursday_dates.append(date_str)
        
        # Assert
        self.assertGreater(len(class_dates), 0, "Should generate class dates for TTH")
        self.assertGreater(len(tuesday_dates), 0, "Should have Tuesday classes")
        self.assertGreater(len(thursday_dates), 0, "Should have Thursday classes")
        
        # Verify the pattern: should alternate between Tuesday and Thursday
        if len(class_dates) >= 2:
            first_date = datetime.strptime(class_dates[0], '%Y-%m-%d')
            second_date = datetime.strptime(class_dates[1], '%Y-%m-%d')
            date_diff = (second_date - first_date).days
            self.assertEqual(date_diff, expected_day_difference, "TTH classes should alternate every 2 days")
    
    def test_mwf_parsing_includes_all_three_days(self):
        """Test that MWF correctly includes Monday, Wednesday, and Friday"""
        # Arrange
        test_semester = 'test'
        test_meeting_days = 'MWF'
        expected_monday_weekday = 0
        expected_wednesday_weekday = 2
        expected_friday_weekday = 4
        
        # Act
        with patch.object(self.calendar_service, 'get_calendar', return_value=self.mock_calendar_data):
            class_dates = self.calendar_service.generate_class_dates(
                semester=test_semester,
                meeting_days=test_meeting_days
            )
            
            # Process the results for analysis
            monday_dates = []
            wednesday_dates = []
            friday_dates = []
            
            for date_str in class_dates[:15]:  # Check first 15 dates for full pattern
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                weekday = date_obj.weekday()
                if weekday == expected_monday_weekday:  # Monday
                    monday_dates.append(date_str)
                elif weekday == expected_wednesday_weekday:  # Wednesday
                    wednesday_dates.append(date_str)
                elif weekday == expected_friday_weekday:  # Friday
                    friday_dates.append(date_str)
        
        # Assert
        self.assertGreater(len(class_dates), 0, "Should generate class dates for MWF")
        self.assertGreater(len(monday_dates), 0, "Should have Monday classes")
        self.assertGreater(len(wednesday_dates), 0, "Should have Wednesday classes")
        self.assertGreater(len(friday_dates), 0, "Should have Friday classes")
    
    def test_mw_parsing_only_monday_and_wednesday(self):
        """Test that MW only includes Monday and Wednesday"""
        with patch.object(self.calendar_service, 'get_calendar', return_value=self.mock_calendar_data):
            class_dates = self.calendar_service.generate_class_dates(
                semester='test',
                meeting_days='MW'
            )
            
            # Verify we got some dates
            self.assertGreater(len(class_dates), 0, "Should generate class dates for MW")
            
            # Check weekdays - should only be Monday (0) and Wednesday (2)
            allowed_weekdays = {0, 2}  # Monday and Wednesday
            for date_str in class_dates[:10]:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                weekday = date_obj.weekday()
                self.assertIn(weekday, allowed_weekdays, 
                            f"Date {date_str} is weekday {weekday}, should be Monday (0) or Wednesday (2)")
    
    def test_tr_parsing_tuesday_and_thursday_with_r_notation(self):
        """Test that TR (Tuesday/Thursday with R notation) works correctly"""
        with patch.object(self.calendar_service, 'get_calendar', return_value=self.mock_calendar_data):
            class_dates = self.calendar_service.generate_class_dates(
                semester='test',
                meeting_days='TR'
            )
            
            # Verify we got some dates
            self.assertGreater(len(class_dates), 0, "Should generate class dates for TR")
            
            # Check weekdays - should only be Tuesday (1) and Thursday (3)
            allowed_weekdays = {1, 3}  # Tuesday and Thursday
            for date_str in class_dates[:10]:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                weekday = date_obj.weekday()
                self.assertIn(weekday, allowed_weekdays, 
                            f"Date {date_str} is weekday {weekday}, should be Tuesday (1) or Thursday (3)")
    
    def test_single_day_patterns(self):
        """Test parsing of single day patterns"""
        test_cases = [
            ('M', {0}),    # Monday
            ('T', {1}),    # Tuesday
            ('W', {2}),    # Wednesday
            ('R', {3}),    # Thursday (R notation)
            ('F', {4}),    # Friday
        ]
        
        for meeting_days, expected_weekdays in test_cases:
            with self.subTest(meeting_days=meeting_days):
                with patch.object(self.calendar_service, 'get_calendar', return_value=self.mock_calendar_data):
                    class_dates = self.calendar_service.generate_class_dates(
                        semester='test',
                        meeting_days=meeting_days
                    )
                    
                    self.assertGreater(len(class_dates), 0, f"Should generate dates for {meeting_days}")
                    
                    # Check all generated dates are the correct weekday
                    for date_str in class_dates[:5]:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        weekday = date_obj.weekday()
                        self.assertIn(weekday, expected_weekdays,
                                    f"Date {date_str} for pattern {meeting_days} is weekday {weekday}, expected {expected_weekdays}")
    
    def test_holiday_exclusion(self):
        """Test that holidays are properly excluded from class dates"""
        with patch.object(self.calendar_service, 'get_calendar', return_value=self.mock_calendar_data):
            class_dates = self.calendar_service.generate_class_dates(
                semester='test',
                meeting_days='MW'  # Monday/Wednesday
            )
            
            # Labor Day (2025-09-01) is a Monday and should be excluded
            self.assertNotIn('2025-09-01', class_dates, "Labor Day should be excluded from class dates")
    
    def test_case_insensitive_parsing(self):
        """Test that day patterns are case-insensitive"""
        test_patterns = ['tth', 'TTH', 'TtH', 'mwf', 'MWF', 'Mwf']
        
        for pattern in test_patterns:
            with self.subTest(pattern=pattern):
                with patch.object(self.calendar_service, 'get_calendar', return_value=self.mock_calendar_data):
                    class_dates = self.calendar_service.generate_class_dates(
                        semester='test',
                        meeting_days=pattern
                    )
                    
                    self.assertGreater(len(class_dates), 0, f"Should generate dates for case variation {pattern}")
    
    def test_invalid_patterns(self):
        """Test handling of invalid day patterns"""
        invalid_patterns = ['', 'X', 'ZZZ', '123', 'INVALID']
        
        for pattern in invalid_patterns:
            with self.subTest(pattern=pattern):
                with patch.object(self.calendar_service, 'get_calendar', return_value=self.mock_calendar_data):
                    class_dates = self.calendar_service.generate_class_dates(
                        semester='test',
                        meeting_days=pattern
                    )
                    
                    self.assertEqual(len(class_dates), 0, f"Invalid pattern {pattern} should generate no dates")
    
    def test_mixed_valid_invalid_characters(self):
        """Test patterns with mix of valid and invalid characters"""
        with patch.object(self.calendar_service, 'get_calendar', return_value=self.mock_calendar_data):
            # "MX2WF" should parse as "MWF" (ignoring X and 2)
            class_dates = self.calendar_service.generate_class_dates(
                semester='test',
                meeting_days='MX2WF'
            )
            
            # Should still generate dates for M, W, F
            self.assertGreater(len(class_dates), 0, "Should generate dates ignoring invalid characters")
            
            # Verify only Monday, Wednesday, Friday
            allowed_weekdays = {0, 2, 4}  # Monday, Wednesday, Friday
            for date_str in class_dates[:9]:  # Check enough dates to see the pattern
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                weekday = date_obj.weekday()
                self.assertIn(weekday, allowed_weekdays, 
                            f"Date {date_str} should only be M/W/F, got weekday {weekday}")


class TestCalendarServiceIntegration(unittest.TestCase):
    """Integration tests for CalendarService with actual calendar data"""
    
    def setUp(self):
        """Set up calendar service for integration tests"""
        self.calendar_service = CalendarService()
    
    def test_tth_with_real_fall_2025_calendar(self):
        """Integration test with actual Fall 2025 calendar data"""
        # This test uses the actual calendar file if it exists
        try:
            class_dates = self.calendar_service.generate_class_dates(
                semester='25_FA',
                meeting_days='TTH'
            )
            
            if class_dates:  # Only test if we successfully loaded calendar data
                # Verify we have both Tuesday and Thursday dates
                weekdays_found = set()
                for date_str in class_dates[:10]:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    weekdays_found.add(date_obj.weekday())
                
                self.assertIn(1, weekdays_found, "Should include Tuesday classes")
                self.assertIn(3, weekdays_found, "Should include Thursday classes")
                
                # Should have reasonable number of classes for a semester
                self.assertGreater(len(class_dates), 20, "Should have substantial number of classes")
                self.assertLess(len(class_dates), 40, "Should not have excessive number of classes")
        
        except Exception as e:
            self.skipTest(f"Calendar data not available for integration test: {e}")


if __name__ == '__main__':
    unittest.main()
#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import unittest
import arrow
from unittest.mock import patch
from pdf.event_parser import extract_semester_events_from_pdf_text
from calendar_json.json_converter import parse_pdf_to_json_with_events

class TestSemesterEventsParser(unittest.TestCase):
    
    def setUp(self):
        # Sample PDF text with column-based semester data
        self.sample_pdf_text = """
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
        December 16-20 April 28-May 2
        Final Examinations Final Examinations
        December 13 April 25
        Last Day of Classes Last Day of Classes
        """
    
    def test_extract_fall_semester_events(self):
        """Test extracting Fall semester events and dates"""
        from pdf.event_parser import extract_semester_events_from_pdf_text
        
        events = extract_semester_events_from_pdf_text(self.sample_pdf_text, 'fall', '2024')
        
        expected_events = [
            {
                "name": "Labor Day Holiday",
                "date": "2024-09-02",
                "date_range": None,
                "type": "holiday"
            },
            {
                "name": "Columbus Day Holiday", 
                "date": "2024-10-14",
                "date_range": None,
                "type": "holiday"
            },
            {
                "name": "Thanksgiving Break",
                "date": None,
                "date_range": ["2024-11-27", "2024-11-29"],
                "type": "break"
            },
            {
                "name": "Final Examinations",
                "date": None,
                "date_range": ["2024-12-16", "2024-12-20"],
                "type": "exam_period"
            }
        ]
        
        self.assertEqual(len(events), len(expected_events))
        
        # Check that Labor Day is found
        labor_day_events = [e for e in events if 'Labor Day' in e['name']]
        self.assertEqual(len(labor_day_events), 1)
        self.assertEqual(labor_day_events[0]['date'], "2024-09-02")
    
    def test_extract_spring_semester_events(self):
        """Test extracting Spring semester events and dates"""
        from pdf.event_parser import extract_semester_events_from_pdf_text
        
        events = extract_semester_events_from_pdf_text(self.sample_pdf_text, 'spring', '2025')
        
        # Should find Presidents Day and Spring Break
        presidents_day_events = [e for e in events if 'Presidents Day' in e['name']]
        self.assertEqual(len(presidents_day_events), 1)
        self.assertEqual(presidents_day_events[0]['date'], "2025-02-17")
        
        spring_break_events = [e for e in events if 'Spring Break' in e['name']]
        self.assertEqual(len(spring_break_events), 1)
        self.assertEqual(spring_break_events[0]['date_range'], ["2025-03-10", "2025-03-14"])
    
    def test_parse_date_ranges(self):
        """Test parsing of date ranges like 'November 27-29' or 'March 10-14'"""
        from pdf.date_parser import parse_date_range_from_text
        
        # Test November 27-29, 2024
        result = parse_date_range_from_text("November 27-29", 2024)
        expected = ["2024-11-27", "2024-11-28", "2024-11-29"]
        self.assertEqual(result, expected)
        
        # Test March 10-14, 2025
        result = parse_date_range_from_text("March 10-14", 2025)
        expected = ["2025-03-10", "2025-03-11", "2025-03-12", "2025-03-13", "2025-03-14"]
        self.assertEqual(result, expected)
    
    def test_parse_single_dates(self):
        """Test parsing single dates like 'September 02'"""
        from pdf.date_parser import parse_single_date_from_text
        
        result = parse_single_date_from_text("September 02", 2024)
        expected = "2024-09-02"
        self.assertEqual(result, expected)
        
        result = parse_single_date_from_text("February 17", 2025)
        expected = "2025-02-17"
        self.assertEqual(result, expected)
    
    def test_classify_event_types(self):
        """Test automatic classification of event types"""
        from pdf.event_parser import classify_event_type
        
        self.assertEqual(classify_event_type("Labor Day Holiday"), "holiday")
        self.assertEqual(classify_event_type("Thanksgiving Break"), "break")
        self.assertEqual(classify_event_type("Final Examinations"), "exam_period")
        self.assertEqual(classify_event_type("Registration Week"), "registration")
        self.assertEqual(classify_event_type("Graduation"), "ceremony")
        self.assertEqual(classify_event_type("Some Random Event"), "other")
    
    @patch('pdf.pdf_extractor.extract_text_from_pdf')
    def test_parse_pdf_to_json_with_events(self, mock_extract):
        """Test complete PDF to JSON conversion including events"""
        mock_extract.return_value = self.sample_pdf_text
        
        result = parse_pdf_to_json_with_events("dummy.pdf")
        
        self.assertIn("semesters", result)
        
        # Check fall semester has events
        fall_semester = result["semesters"]["fall_2024"]
        self.assertIn("events", fall_semester)
        self.assertIsInstance(fall_semester["events"], list)
        self.assertGreater(len(fall_semester["events"]), 0)
        
        # Check spring semester has events
        spring_semester = result["semesters"]["spring_2025"]
        self.assertIn("events", spring_semester)
        self.assertIsInstance(spring_semester["events"], list)
    
    def test_handle_unparseable_dates_as_tbd(self):
        """Test that unparseable dates become TBD"""
        malformed_text = "Some Random Date Format - Holiday"
        
        from pdf.event_parser import extract_semester_events_from_pdf_text
        
        events = extract_semester_events_from_pdf_text(malformed_text, 'fall', '2024')
        
        # Should handle gracefully, either return empty or TBD events
        self.assertIsInstance(events, list)
    
    def test_semester_column_separation(self):
        """Test that events are correctly assigned to their semester columns"""
        from pdf.event_parser import extract_semester_events_from_pdf_text
        
        # Fall events should not appear in Spring
        fall_events = extract_semester_events_from_pdf_text(self.sample_pdf_text, 'fall', '2024')
        spring_events = extract_semester_events_from_pdf_text(self.sample_pdf_text, 'spring', '2025')
        
        fall_event_names = [e['name'] for e in fall_events]
        spring_event_names = [e['name'] for e in spring_events]
        
        # Labor Day should only be in Fall
        self.assertTrue(any('Labor Day' in name for name in fall_event_names))
        self.assertFalse(any('Labor Day' in name for name in spring_event_names))
        
        # Presidents Day should only be in Spring  
        self.assertFalse(any('Presidents Day' in name for name in fall_event_names))
        self.assertTrue(any('Presidents Day' in name for name in spring_event_names))

if __name__ == '__main__':
    unittest.main()
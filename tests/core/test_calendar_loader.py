#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import unittest
import json
import tempfile
import arrow
from core.calendar_loader import load_semester_calendar_from_json, fetch_registrar_table

class TestCalendarLoader(unittest.TestCase):
    
    def setUp(self):
        # Create sample JSON data
        self.sample_calendar_data = {
            "semester": "fall_2025",
            "source_file": "test.pdf",
            "generated_at": "2025-08-19 12:00:00",
            "first_day": "2025-08-25",
            "last_day": "2025-12-15",
            "no_class_dates": ["2025-11-28", "2025-11-29"],
            "events": [
                {
                    "name": "Columbus Day",
                    "date": "2025-10-13",
                    "date_range": None,
                    "type": "holiday"
                },
                {
                    "name": "Fall Break",
                    "date": None,
                    "date_range": ["2025-11-28", "2025-11-29"],
                    "type": "break"
                },
                {
                    "name": "Halloween",
                    "date": "2025-10-31",
                    "date_range": None,
                    "type": "other"
                }
            ]
        }

    def test_load_semester_calendar_from_json(self):
        """Test loading calendar data from JSON file"""
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_calendar_data, f)
            temp_path = f.name
        
        try:
            # Load the calendar
            first_days, last_days, no_class_dates, events = load_semester_calendar_from_json(temp_path)
            
            # Test first and last days
            self.assertEqual(len(first_days), 1)
            self.assertEqual(first_days[0].format('YYYY-MM-DD'), '2025-08-25')
            
            self.assertEqual(len(last_days), 1)
            self.assertEqual(last_days[0].format('YYYY-MM-DD'), '2025-12-15')
            
            # Test no class dates
            self.assertEqual(len(no_class_dates), 2)
            no_class_strs = [d.format('YYYY-MM-DD') for d in no_class_dates]
            self.assertIn('2025-11-28', no_class_strs)
            self.assertIn('2025-11-29', no_class_strs)
            
            # Test events
            self.assertEqual(len(events), 3)
            
            # Find Columbus Day event
            columbus_event = next(e for e in events if e['name'] == 'Columbus Day')
            self.assertEqual(columbus_event['type'], 'holiday')
            self.assertEqual(columbus_event['date'].format('YYYY-MM-DD'), '2025-10-13')
            self.assertEqual(len(columbus_event['date_range']), 0)
            
            # Find Fall Break event
            break_event = next(e for e in events if e['name'] == 'Fall Break')
            self.assertEqual(break_event['type'], 'break')
            self.assertIsNone(break_event['date'])
            self.assertEqual(len(break_event['date_range']), 2)
            break_dates = [d.format('YYYY-MM-DD') for d in break_event['date_range']]
            self.assertIn('2025-11-28', break_dates)
            self.assertIn('2025-11-29', break_dates)
            
            # Find Halloween event
            halloween_event = next(e for e in events if e['name'] == 'Halloween')
            self.assertEqual(halloween_event['type'], 'other')
            self.assertEqual(halloween_event['date'].format('YYYY-MM-DD'), '2025-10-31')
            
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_load_semester_calendar_with_tbd_values(self):
        """Test handling of TBD values in JSON"""
        tbd_data = {
            "semester": "fall_2025",
            "first_day": "TBD",
            "last_day": "TBD", 
            "no_class_dates": ["TBD"],
            "events": [
                {
                    "name": "Some Event",
                    "date": "TBD",
                    "date_range": ["TBD"],
                    "type": "other"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(tbd_data, f)
            temp_path = f.name
        
        try:
            first_days, last_days, no_class_dates, events = load_semester_calendar_from_json(temp_path)
            
            # Should return empty lists for TBD values
            self.assertEqual(len(first_days), 0)
            self.assertEqual(len(last_days), 0)
            self.assertEqual(len(no_class_dates), 0)
            self.assertEqual(len(events), 0)  # Events with TBD dates should be filtered out
            
        finally:
            os.unlink(temp_path)

    def test_fetch_registrar_table_json_path(self):
        """Test fetch_registrar_table with JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_calendar_data, f)
            temp_path = f.name
        
        try:
            first_days, last_days, no_class_dates, events = fetch_registrar_table(temp_path)
            
            # Should return 4-tuple with events
            self.assertEqual(len(first_days), 1)
            self.assertEqual(len(last_days), 1) 
            self.assertEqual(len(no_class_dates), 2)
            self.assertEqual(len(events), 3)
            
        finally:
            os.unlink(temp_path)

    def test_event_filtering_by_type(self):
        """Test that events are properly categorized by type"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_calendar_data, f)
            temp_path = f.name
        
        try:
            _, _, _, events = load_semester_calendar_from_json(temp_path)
            
            # Categorize events by type
            holidays = [e for e in events if e['type'] == 'holiday']
            breaks = [e for e in events if e['type'] == 'break']
            others = [e for e in events if e['type'] == 'other']
            
            self.assertEqual(len(holidays), 1)
            self.assertEqual(holidays[0]['name'], 'Columbus Day')
            
            self.assertEqual(len(breaks), 1)
            self.assertEqual(breaks[0]['name'], 'Fall Break')
            
            self.assertEqual(len(others), 1)
            self.assertEqual(others[0]['name'], 'Halloween')
            
        finally:
            os.unlink(temp_path)

if __name__ == '__main__':
    unittest.main()
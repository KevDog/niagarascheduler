#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import unittest
import arrow
from core.schedule_generator import schedule

class TestEventFiltering(unittest.TestCase):
    
    def setUp(self):
        # Sample class dates
        self.possible_classes = [
            arrow.get('2025-10-10'),
            arrow.get('2025-10-13'),  # Columbus Day
            arrow.get('2025-10-31'),  # Halloween  
            arrow.get('2025-11-28'),  # Fall Break
            arrow.get('2025-12-01')
        ]
        
        self.no_classes = []
        
        # Sample events
        self.events = [
            {
                'name': 'Columbus Day',
                'date': arrow.get('2025-10-13'),
                'date_range': [],
                'type': 'holiday'
            },
            {
                'name': 'Halloween',
                'date': arrow.get('2025-10-31'),
                'date_range': [],
                'type': 'other'
            },
            {
                'name': 'Fall Break',
                'date': arrow.get('2025-11-28'),
                'date_range': [],
                'type': 'break'
            }
        ]

    def test_show_all_events(self):
        """Test showing all event types"""
        result = schedule(
            self.possible_classes, 
            self.no_classes, 
            show_no=True, 
            fmt='YYYY-MM-DD',
            events=self.events,
            show_holidays=True,
            show_breaks=True,
            show_events=True
        )
        
        # Should include all events
        result_str = '\n'.join(result)
        self.assertIn('Columbus Day', result_str)
        self.assertIn('Halloween', result_str)
        self.assertIn('Fall Break', result_str)
        
        # Holidays and breaks should show as NO CLASS
        self.assertIn('NO CLASS (Columbus Day)', result_str)
        self.assertIn('NO CLASS (Fall Break)', result_str)
        
        # Other events should show normally
        self.assertIn('2025-10-31 - Halloween', result_str)

    def test_show_only_holidays(self):
        """Test showing only holidays"""
        result = schedule(
            self.possible_classes, 
            self.no_classes, 
            show_no=True, 
            fmt='YYYY-MM-DD',
            events=self.events,
            show_holidays=True,
            show_breaks=False,
            show_events=False
        )
        
        result_str = '\n'.join(result)
        self.assertIn('Columbus Day', result_str)
        self.assertNotIn('Halloween', result_str)
        self.assertNotIn('Fall Break', result_str)

    def test_show_only_breaks(self):
        """Test showing only breaks"""
        result = schedule(
            self.possible_classes, 
            self.no_classes, 
            show_no=True, 
            fmt='YYYY-MM-DD',
            events=self.events,
            show_holidays=False,
            show_breaks=True,
            show_events=False
        )
        
        result_str = '\n'.join(result)
        self.assertNotIn('Columbus Day', result_str)
        self.assertNotIn('Halloween', result_str)
        self.assertIn('Fall Break', result_str)

    def test_show_only_events(self):
        """Test showing only other events"""
        result = schedule(
            self.possible_classes, 
            self.no_classes, 
            show_no=True, 
            fmt='YYYY-MM-DD',
            events=self.events,
            show_holidays=False,
            show_breaks=False,
            show_events=True
        )
        
        result_str = '\n'.join(result)
        self.assertNotIn('Columbus Day', result_str)
        self.assertIn('Halloween', result_str)
        self.assertNotIn('Fall Break', result_str)

    def test_show_no_events(self):
        """Test showing no events at all"""
        result = schedule(
            self.possible_classes, 
            self.no_classes, 
            show_no=True, 
            fmt='YYYY-MM-DD',
            events=self.events,
            show_holidays=False,
            show_breaks=False,
            show_events=False
        )
        
        result_str = '\n'.join(result)
        self.assertNotIn('Columbus Day', result_str)
        self.assertNotIn('Halloween', result_str)
        self.assertNotIn('Fall Break', result_str)
        
        # Should just be plain dates
        self.assertIn('2025-10-10', result_str)
        self.assertIn('2025-10-13', result_str)
        self.assertIn('2025-10-31', result_str)

    def test_date_range_events(self):
        """Test events with date ranges"""
        range_event = {
            'name': 'Spring Break',
            'date': None,
            'date_range': [arrow.get('2025-10-10'), arrow.get('2025-10-13')],
            'type': 'break'
        }
        
        result = schedule(
            self.possible_classes, 
            self.no_classes, 
            show_no=True, 
            fmt='YYYY-MM-DD',
            events=[range_event],
            show_holidays=False,
            show_breaks=True,
            show_events=False
        )
        
        result_str = '\n'.join(result)
        self.assertIn('NO CLASS (Spring Break)', result_str)

    def test_event_formatting_types(self):
        """Test proper formatting for different event types"""
        result = schedule(
            self.possible_classes, 
            self.no_classes, 
            show_no=True, 
            fmt='dddd, MMMM D, YYYY',
            events=self.events,
            show_holidays=True,
            show_breaks=True,
            show_events=True
        )
        
        result_str = '\n'.join(result)
        
        # Holiday should be NO CLASS format
        self.assertTrue(any('NO CLASS (Columbus Day)' in line for line in result))
        
        # Break should be NO CLASS format  
        self.assertTrue(any('NO CLASS (Fall Break)' in line for line in result))
        
        # Other event should be regular format
        self.assertTrue(any('Halloween' in line and 'NO CLASS' not in line for line in result))

if __name__ == '__main__':
    unittest.main()
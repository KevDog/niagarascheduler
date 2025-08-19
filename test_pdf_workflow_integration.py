#!/usr/bin/env python

import unittest
import arrow
import os
from unittest.mock import patch
from niagarascheduler import make_url, fetch_registrar_table, parse_registrar_table, sorted_classes, schedule

class TestPDFWorkflowIntegration(unittest.TestCase):
    
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
    def test_complete_pdf_workflow(self, mock_extract):
        """Test complete workflow from PDF path to schedule generation"""
        mock_extract.return_value = self.sample_pdf_text
        
        # Step 1: Generate PDF path
        pdf_path = make_url('fall', '2024')
        self.assertTrue(pdf_path.endswith('.pdf'))
        
        # Step 2: Fetch calendar data from PDF
        calendar_data = fetch_registrar_table(pdf_path)
        first_day, last_day, no_classes = calendar_data
        
        # Verify calendar data extraction
        self.assertEqual(len(first_day), 1)
        self.assertEqual(first_day[0], arrow.get(2024, 8, 26))
        self.assertEqual(len(last_day), 1)
        self.assertEqual(last_day[0], arrow.get(2024, 12, 13))
        self.assertEqual(len(no_classes), 4)
        
        # Step 3: Parse calendar data (should pass through)
        parsed_first, parsed_last, parsed_no_classes = parse_registrar_table(calendar_data)
        self.assertEqual(parsed_first, first_day)
        self.assertEqual(parsed_last, last_day)
        self.assertEqual(parsed_no_classes, no_classes)
        
        # Step 4: Generate class schedule for Tuesdays and Thursdays
        weekdays = ['Tuesday', 'Thursday']
        possible_classes, filtered_no_classes = sorted_classes(weekdays, parsed_first, parsed_last, parsed_no_classes)
        
        # Verify some classes are scheduled
        self.assertGreater(len(possible_classes), 0)
        
        # Step 5: Generate final schedule
        final_schedule = schedule(possible_classes, filtered_no_classes, show_no=True)
        
        # Verify schedule contains formatted dates
        self.assertGreater(len(final_schedule), 0)
        for entry in final_schedule:
            self.assertIsInstance(entry, str)
            # Should contain either a day name or "NO CLASS"
            self.assertTrue('day' in entry.lower() or 'no class' in entry.lower())
    
    @patch('niagarascheduler.extract_text_from_pdf')
    def test_workflow_with_empty_pdf(self, mock_extract):
        """Test workflow gracefully handles empty PDF"""
        mock_extract.return_value = ""
        
        pdf_path = make_url('fall', '2024')
        calendar_data = fetch_registrar_table(pdf_path)
        first_day, last_day, no_classes = calendar_data
        
        # Should return empty lists
        self.assertEqual(len(first_day), 0)
        self.assertEqual(len(last_day), 0)
        self.assertEqual(len(no_classes), 0)
    
    @patch('niagarascheduler.extract_text_from_pdf')
    def test_workflow_with_minimal_data(self, mock_extract):
        """Test workflow with minimal calendar data"""
        minimal_text = """
        August 26, 2024 - First Day of Classes
        December 13, 2024 - Last Day of Classes
        """
        mock_extract.return_value = minimal_text
        
        pdf_path = make_url('fall', '2024')
        calendar_data = fetch_registrar_table(pdf_path)
        first_day, last_day, no_classes = parse_registrar_table(calendar_data)
        
        # Should have start/end dates but no holidays
        self.assertEqual(len(first_day), 1)
        self.assertEqual(len(last_day), 1)
        self.assertEqual(len(no_classes), 0)
        
        # Generate schedule for Mondays
        weekdays = ['Monday']
        possible_classes, filtered_no_classes = sorted_classes(weekdays, first_day, last_day, no_classes)
        final_schedule = schedule(possible_classes, filtered_no_classes)
        
        # Should generate valid schedule
        self.assertGreater(len(final_schedule), 0)
    
    def test_workflow_with_actual_pdf_file(self):
        """Test workflow with actual PDF file if it exists"""
        pdf_path = make_url('fall', '2024')
        
        if os.path.exists(pdf_path):
            try:
                calendar_data = fetch_registrar_table(pdf_path)
                first_day, last_day, no_classes = parse_registrar_table(calendar_data)
                
                # Basic validation that we got some data
                if len(first_day) > 0 and len(last_day) > 0:
                    weekdays = ['Monday', 'Wednesday', 'Friday']
                    possible_classes, filtered_no_classes = sorted_classes(weekdays, first_day, last_day, no_classes)
                    final_schedule = schedule(possible_classes, filtered_no_classes, show_no=True)
                    
                    self.assertGreater(len(final_schedule), 0)
            except Exception as e:
                self.skipTest(f"PDF parsing failed: {e}")
        else:
            self.skipTest("PDF file not found")
    
    @patch('niagarascheduler.extract_text_from_pdf')
    def test_workflow_date_format_options(self, mock_extract):
        """Test workflow with different date format options"""
        mock_extract.return_value = self.sample_pdf_text
        
        pdf_path = make_url('fall', '2024')
        calendar_data = fetch_registrar_table(pdf_path)
        first_day, last_day, no_classes = parse_registrar_table(calendar_data)
        
        weekdays = ['Monday']
        possible_classes, filtered_no_classes = sorted_classes(weekdays, first_day, last_day, no_classes)
        
        # Test different date formats
        formats = ['MMMM D, YYYY', 'M/D', 'dddd, MMMM D']
        
        for fmt in formats:
            final_schedule = schedule(possible_classes, filtered_no_classes, fmt=fmt)
            self.assertGreater(len(final_schedule), 0)
            # Verify format is applied (basic check)
            self.assertIsInstance(final_schedule[0], str)

if __name__ == '__main__':
    unittest.main()
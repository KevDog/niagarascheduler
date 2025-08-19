#!/usr/bin/env python

import unittest
import arrow
from unittest.mock import patch, MagicMock
import pdfplumber

class TestPDFDateExtraction(unittest.TestCase):
    
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
    
    def test_extract_first_day_classes(self):
        """Test extracting first day of classes from PDF text"""
        from niagarascheduler import extract_first_day_from_pdf_text
        
        result = extract_first_day_from_pdf_text(self.sample_pdf_text)
        expected = arrow.get(2024, 8, 26)
        
        self.assertEqual(result, expected)
    
    def test_extract_last_day_classes(self):
        """Test extracting last day of classes from PDF text"""
        from niagarascheduler import extract_last_day_from_pdf_text
        
        result = extract_last_day_from_pdf_text(self.sample_pdf_text)
        expected = arrow.get(2024, 12, 13)
        
        self.assertEqual(result, expected)
    
    def test_extract_no_class_dates(self):
        """Test extracting no class dates from PDF text"""
        from niagarascheduler import extract_no_class_dates_from_pdf_text
        
        result = extract_no_class_dates_from_pdf_text(self.sample_pdf_text)
        expected = [
            arrow.get(2024, 9, 2),
            arrow.get(2024, 10, 14),
            arrow.get(2024, 11, 28),
            arrow.get(2024, 11, 29)
        ]
        
        self.assertEqual(len(result), len(expected))
        for date in expected:
            self.assertIn(date, result)
    
    def test_handle_date_ranges(self):
        """Test parsing multi-day periods like 'Nov 28-29'"""
        text = "November 28-29, 2024 - Thanksgiving Break - No Classes"
        from niagarascheduler import extract_date_range_from_text
        
        result = extract_date_range_from_text(text)
        expected = [arrow.get(2024, 11, 28), arrow.get(2024, 11, 29)]
        
        self.assertEqual(result, expected)
    
    def test_handle_malformed_dates(self):
        """Test graceful handling of invalid date formats"""
        malformed_text = "Invalid Date Format - First Day of Classes"
        from niagarascheduler import extract_first_day_from_pdf_text
        
        result = extract_first_day_from_pdf_text(malformed_text)
        
        self.assertIsNone(result)
    
    def test_extract_from_actual_pdf(self):
        """Test extracting text from actual PDF file"""
        pdf_path = "/Users/kevdog/Documents/code/niagarascheduler/niagara/Academic-Year-Schedule-Lewiston-2024-2025.pdf"
        
        with patch('pdfplumber.open') as mock_pdf:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = self.sample_pdf_text
            mock_pdf.return_value.__enter__.return_value.pages = [mock_page]
            
            from niagarascheduler import extract_text_from_pdf
            result = extract_text_from_pdf(pdf_path)
            
            self.assertEqual(result.strip(), self.sample_pdf_text.strip())
    
    def test_case_insensitive_matching(self):
        """Test case insensitive matching for class day indicators"""
        text_lower = "august 26, 2024 - first day of classes"
        from niagarascheduler import extract_first_day_from_pdf_text
        
        result = extract_first_day_from_pdf_text(text_lower)
        expected = arrow.get(2024, 8, 26)
        
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import unittest
import json
import arrow
from unittest.mock import patch, mock_open
from calendar_json.json_converter import parse_pdf_to_json, generate_calendar_json
from core.calendar_loader import load_calendar_from_json

class TestPDFToJSON(unittest.TestCase):
    
    def setUp(self):
        self.sample_pdf_text = """
        SUMMER 2024 FALL 2024 SEMESTER SPRING 2025 SEMESTER
        August 24 January 21
        MBA & Graduate 1st Saturday Session Begins Undergraduate and Graduate Classes Begin
        August 26 January 25
        Undergraduate and Graduate Classes Begin MBA & Graduate 1st Saturday Session Begins
        September 02 January 28
        Labor Day Holiday Restricted Drop Add Begins
        """
        
        self.expected_json_structure = {
            "academic_year": "2024-2025",
            "semesters": {
                "fall_2024": {
                    "first_day": "2024-08-26",
                    "last_day": "2024-12-15",
                    "no_class_dates": ["2024-09-02"]
                },
                "spring_2025": {
                    "first_day": "2025-01-25", 
                    "last_day": "2025-05-15",
                    "no_class_dates": []
                }
            }
        }
    
    @patch('pdf.pdf_extractor.extract_text_from_pdf')
    def test_parse_pdf_to_json(self, mock_extract):
        """Test converting PDF to JSON format"""
        mock_extract.return_value = self.sample_pdf_text
        
        result = parse_pdf_to_json("dummy.pdf")
        
        self.assertIn("academic_year", result)
        self.assertIn("semesters", result)
        self.assertIn("fall_2024", result["semesters"])
        self.assertIn("spring_2025", result["semesters"])
    
    def test_generate_calendar_json_for_directory(self):
        """Test generating JSON files for all PDFs in directory"""
        with patch('os.listdir') as mock_listdir, \
             patch('calendar_json.json_converter.parse_pdf_to_json') as mock_parse, \
             patch('builtins.open', mock_open()) as mock_file:
            
            mock_listdir.return_value = ['Academic-Year-Schedule-Lewiston-2024-2025.pdf']
            mock_parse.return_value = self.expected_json_structure
            
            generate_calendar_json()
            
            # Should have written JSON file
            mock_file.assert_called_once()
    
    def test_load_calendar_from_json(self):
        """Test loading calendar data from JSON file"""
        json_data = json.dumps(self.expected_json_structure)
        
        with patch('builtins.open', mock_open(read_data=json_data)):
            result = load_calendar_from_json("dummy.json", "fall", "2024")
            
            first_day, last_day, no_classes = result
            self.assertEqual(len(first_day), 1)
            self.assertEqual(first_day[0], arrow.get("2024-08-26"))
            self.assertEqual(len(last_day), 1)
            self.assertEqual(last_day[0], arrow.get("2024-12-15"))
    
    def test_json_handles_missing_data_with_tbd(self):
        """Test that missing data is replaced with TBD"""
        incomplete_pdf_text = "Some text without clear dates"
        
        with patch('pdf.pdf_extractor.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = incomplete_pdf_text
            
            result = parse_pdf_to_json("dummy.pdf")
            
            # Should contain TBD for missing data
            fall_semester = result["semesters"]["fall_2024"]
            if fall_semester["first_day"] is None:
                self.assertEqual(fall_semester["first_day"], "TBD")
    
    def test_json_output_format_validation(self):
        """Test that JSON output has correct format and types"""
        with patch('pdf.pdf_extractor.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = self.sample_pdf_text
            
            result = parse_pdf_to_json("dummy.pdf")
            
            # Validate structure
            self.assertIsInstance(result["academic_year"], str)
            self.assertIsInstance(result["semesters"], dict)
            
            for semester_key, semester_data in result["semesters"].items():
                self.assertIn("first_day", semester_data)
                self.assertIn("last_day", semester_data) 
                self.assertIn("no_class_dates", semester_data)
                self.assertIsInstance(semester_data["no_class_dates"], list)
    
    def test_multiple_academic_years_support(self):
        """Test handling multiple academic year PDFs"""
        with patch('os.listdir') as mock_listdir, \
             patch('calendar_json.json_converter.parse_pdf_to_json') as mock_parse, \
             patch('builtins.open', mock_open()) as mock_file:
            
            mock_listdir.return_value = [
                'Academic-Year-Schedule-Lewiston-2024-2025.pdf',
                'Academic-Year-Schedule-Lewiston-2025-2026.pdf'
            ]
            mock_parse.return_value = self.expected_json_structure
            
            generate_calendar_json()
            
            # Should have called parse for each PDF
            self.assertEqual(mock_parse.call_count, 2)

if __name__ == '__main__':
    unittest.main()
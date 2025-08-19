#!/usr/bin/env python

import unittest
import os
from unittest.mock import patch
from niagarascheduler import discover_available_years

class TestDiscoverYears(unittest.TestCase):
    
    def setUp(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.niagara_path = os.path.join(self.base_path, 'niagara')
    
    @patch('os.listdir')
    def test_discover_years_from_pdf_filenames(self, mock_listdir):
        """Test discovering years from PDF filenames"""
        mock_listdir.return_value = [
            'Academic-Year-Schedule-Lewiston-2024-2025.pdf',
            'Academic-Year-25-26-Lewiston.pdf',
            'Academic-Year-Schedule-Lewiston-2023-2024.pdf',
            'other_file.txt'
        ]
        
        years = discover_available_years()
        expected = ['2024', '2025', '2023', '2026']
        
        self.assertEqual(sorted(years), sorted(expected))
    
    @patch('os.listdir')
    def test_discover_years_empty_directory(self, mock_listdir):
        """Test discovering years from empty directory"""
        mock_listdir.return_value = []
        
        years = discover_available_years()
        
        self.assertEqual(years, [])
    
    @patch('os.listdir')
    def test_discover_years_no_matching_files(self, mock_listdir):
        """Test discovering years with no matching PDF files"""
        mock_listdir.return_value = [
            'random_file.pdf',
            'other_document.txt',
            'not_calendar.pdf'
        ]
        
        years = discover_available_years()
        
        self.assertEqual(years, [])
    
    def test_discover_years_actual_directory(self):
        """Test discovering years from actual directory"""
        years = discover_available_years()
        
        # Should find years from actual PDF files
        self.assertIsInstance(years, list)
        if len(years) > 0:
            for year in years:
                self.assertIsInstance(year, str)
                self.assertTrue(year.isdigit())
                self.assertEqual(len(year), 4)

if __name__ == '__main__':
    unittest.main()
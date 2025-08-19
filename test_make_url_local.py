#!/usr/bin/env python

import unittest
import os
from unittest.mock import patch
from niagarascheduler import make_url

class TestMakeURLLocal(unittest.TestCase):
    
    def setUp(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.niagara_path = os.path.join(self.base_path, 'niagara')
    
    @patch('os.path.exists')
    def test_make_url_existing_year(self, mock_exists):
        """Test make_url returns correct path for existing year PDF"""
        mock_exists.return_value = True
        
        result = make_url('fall', '2024')
        expected = os.path.join(self.base_path, 'niagara', 'Academic-Year-Schedule-Lewiston-2024-2025.pdf')
        
        self.assertEqual(result, expected)
    
    @patch('os.path.exists')
    def test_make_url_nonexistent_year_fallback(self, mock_exists):
        """Test make_url falls back to default PDF for nonexistent year"""
        mock_exists.return_value = False
        
        result = make_url('spring', '2026')
        expected = os.path.join(self.base_path, 'niagara', 'Academic-Year-Schedule-Lewiston-2024-2025.pdf')
        
        self.assertEqual(result, expected)
    
    def test_make_url_ignores_semester(self):
        """Test make_url ignores semester parameter for PDF selection"""
        result_fall = make_url('fall', '2024')
        result_spring = make_url('spring', '2024')
        
        self.assertEqual(result_fall, result_spring)
    
    def test_make_url_year_formatting(self):
        """Test make_url correctly formats year range"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            result = make_url('fall', '2023')
            expected_filename = 'Academic-Year-Schedule-Lewiston-2023-2024.pdf'
            
            self.assertTrue(result.endswith(expected_filename))
    
    @patch('os.path.exists')
    def test_make_url_path_construction(self, mock_exists):
        """Test make_url constructs correct relative path"""
        mock_exists.return_value = True
        
        result = make_url('fall', '2024')
        
        self.assertTrue(result.endswith('niagara/Academic-Year-Schedule-Lewiston-2024-2025.pdf'))
        self.assertTrue(os.path.isabs(result))
    
    def test_make_url_with_actual_file(self):
        """Test make_url with actual existing file"""
        result = make_url('fall', '2024')
        
        # Should return the fallback file since 2024-2025 PDF exists
        expected = os.path.join(self.base_path, 'niagara', 'Academic-Year-Schedule-Lewiston-2024-2025.pdf')
        self.assertEqual(result, expected)
        self.assertTrue(os.path.exists(result))

if __name__ == '__main__':
    unittest.main()
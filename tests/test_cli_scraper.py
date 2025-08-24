#!/usr/bin/env python

"""
Tests for CLI scraper command-line interface
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO


class TestScrapeOfferingsCLI(unittest.TestCase):
    
    def test_parse_args_required_semester_and_ug(self):
        # Arrange
        from scrape_offerings import parse_args
        test_args = ['--semester', '25/FA', '--ug']
        
        # Act
        args = parse_args(test_args)
        
        # Assert
        self.assertEqual(args.semester, '25/FA')
        self.assertEqual(args.output_dir, '/data')
        self.assertTrue(args.ug)
        self.assertFalse(args.grad)
        
    def test_parse_args_with_grad_flag(self):
        # Arrange
        from scrape_offerings import parse_args
        test_args = ['--semester', '25/FA', '--grad']
        
        # Act
        args = parse_args(test_args)
        
        # Assert
        self.assertTrue(args.grad)
        self.assertFalse(args.ug)
        
    def test_parse_args_with_both_ug_and_grad(self):
        # Arrange
        from scrape_offerings import parse_args
        test_args = ['--semester', '25/FA', '--ug', '--grad']
        
        # Act
        args = parse_args(test_args)
        
        # Assert
        self.assertTrue(args.ug)
        self.assertTrue(args.grad)
        
    def test_parse_args_with_output_dir(self):
        # Arrange
        from scrape_offerings import parse_args
        test_args = ['--semester', '25/FA', '--ug', '--output-dir', '/tmp/courses']
        
        # Act
        args = parse_args(test_args)
        
        # Assert
        self.assertEqual(args.output_dir, '/tmp/courses')
        
    def test_main_function_calls_scraper(self):
        # Arrange
        from scrape_offerings import main
        from unittest.mock import patch
        
        with patch('scrape_offerings.CourseScraperCLI') as mock_scraper_class:
            mock_scraper = mock_scraper_class.return_value
            test_args = ['--semester', '25/FA', '--ug']
            
            # Act
            main(test_args)
            
            # Assert
            mock_scraper_class.assert_called_once()
            mock_scraper.scrape_courses.assert_called_once()
        
    def test_main_function_with_arguments(self):
        # Arrange
        from scrape_offerings import main
        from unittest.mock import patch
        
        with patch('scrape_offerings.CourseScraperCLI') as mock_scraper_class:
            mock_scraper = mock_scraper_class.return_value
            test_args = ['--semester', '25/SP', '--ug', '--grad', '--output-dir', '/custom/path']
            
            # Act
            main(test_args)
            
            # Assert
            mock_scraper.scrape_courses.assert_called_once_with(
                semester='25/SP',
                ug=True,
                grad=True,
                output_dir='/custom/path'
            )


if __name__ == '__main__':
    unittest.main()
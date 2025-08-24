#!/usr/bin/env python

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrape_descriptions import CourseScheduleScraper
from bs4 import BeautifulSoup


class TestCourseScheduleScraper(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.scraper = CourseScheduleScraper(self.temp_dir)
    
    def test_extract_course_schedule_valid_data(self):
        """Test extracting course schedule from valid table cells"""
        # Arrange
        html_cells = [
            '<td>THR103A</td>',
            '<td>Intro to Theatre</td>',
            '<td>LEC</td>',
            '<td>TTH</td>',
            '<td>12:00PM</td>',
            '<td>01:20PM</td>',
            '<td>H*LA</td>',
            '<td>27</td>',
            '<td>3.00</td>'
        ]
        cells = [BeautifulSoup(cell, 'html.parser').find('td') for cell in html_cells]
        
        # Act
        result = self.scraper.extract_course_schedule(cells)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['department'], 'THR')
        self.assertEqual(result['number'], 'THR103A')
        self.assertEqual(result['name'], 'Intro to Theatre')
        self.assertEqual(result['days'], 'TTH')
        self.assertEqual(result['start_time'], '12:00PM')
        self.assertEqual(result['end_time'], '01:20PM')
        self.assertEqual(result['credits'], '3.00')
    
    def test_extract_course_schedule_invalid_course_code(self):
        """Test extracting course schedule with invalid course code format"""
        # Arrange - using a format that doesn't match dept code + numbers pattern
        html_cells = [
            '<td>123INVALID</td>',  # Invalid format (numbers first)
            '<td>Test Course</td>',
            '<td>LEC</td>',
            '<td>MW</td>',
            '<td>10:00AM</td>',
            '<td>11:00AM</td>',
            '<td></td>',
            '<td>20</td>'
        ]
        cells = [BeautifulSoup(cell, 'html.parser').find('td') for cell in html_cells]
        
        # Act
        result = self.scraper.extract_course_schedule(cells)
        
        # Assert
        self.assertIsNone(result)
    
    def test_extract_course_schedule_missing_schedule_info(self):
        """Test extracting course schedule with missing schedule info returns None"""
        # Arrange
        html_cells = [
            '<td>THR103A</td>',
            '<td>Intro to Theatre</td>',
            '<td>LEC</td>',
            '<td></td>',  # No days
            '<td></td>',  # No start time
            '<td></td>',  # No end time
            '<td></td>',
            '<td>27</td>'
        ]
        cells = [BeautifulSoup(cell, 'html.parser').find('td') for cell in html_cells]
        
        # Act
        result = self.scraper.extract_course_schedule(cells)
        
        # Assert
        self.assertIsNone(result)
    
    def test_merge_course_data_with_existing_descriptions(self):
        """Test merging schedule data with existing course descriptions"""
        # Arrange
        existing_courses = [
            {
                "number": "THR103A",
                "name": "Intro to Theatre",
                "credits": "3.00",
                "description": "An introduction to theatrical performance and production."
            }
        ]
        
        schedule_courses = [
            {
                "department": "THR",
                "number": "THR103A",
                "name": "Intro to Theatre",
                "credits": "3.00",
                "days": "TTH",
                "start_time": "12:00PM",
                "end_time": "01:20PM"
            }
        ]
        
        # Act
        result = self.scraper.merge_course_data(existing_courses, schedule_courses)
        
        # Assert
        self.assertEqual(len(result), 1)
        merged_course = result[0]
        self.assertEqual(merged_course['number'], 'THR103A')
        self.assertEqual(merged_course['days'], 'TTH')
        self.assertEqual(merged_course['description'], 'An introduction to theatrical performance and production.')
    
    def test_merge_course_data_preserves_existing_only_courses(self):
        """Test that existing courses without schedule data are preserved"""
        # Arrange
        existing_courses = [
            {
                "number": "THR999",
                "name": "Special Topics",
                "credits": "3.00",
                "description": "Advanced special topics course."
            }
        ]
        
        schedule_courses = [
            {
                "department": "THR",
                "number": "THR103A",
                "name": "Intro to Theatre",
                "credits": "3.00",
                "days": "TTH",
                "start_time": "12:00PM",
                "end_time": "01:20PM"
            }
        ]
        
        # Act
        result = self.scraper.merge_course_data(existing_courses, schedule_courses)
        
        # Assert
        self.assertEqual(len(result), 2)
        # Check that both schedule and existing-only courses are included
        course_numbers = [course['number'] for course in result]
        self.assertIn('THR103A', course_numbers)
        self.assertIn('THR999', course_numbers)
    
    @patch('scrape_descriptions.requests.get')
    def test_scrape_semester_schedule_success(self, mock_get):
        """Test successful semester schedule scraping"""
        # Arrange
        mock_html = '''
        <table>
            <tr>
                <td>THR103A</td>
                <td>Intro to Theatre</td>
                <td>LEC</td>
                <td>TTH</td>
                <td>12:00PM</td>
                <td>01:20PM</td>
                <td>H*LA</td>
                <td>27</td>
                <td>3.00</td>
            </tr>
        </table>
        '''
        
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_get.return_value = mock_response
        
        # Act
        result = self.scraper.scrape_semester_schedule('25_FA')
        
        # Assert
        self.assertTrue(result)
        mock_get.assert_called_once()
        
        # Check that the URL was constructed correctly
        expected_url = "https://apps.niagara.edu/courses/index.php?semester=25/FA&ug=1"
        mock_get.assert_called_with(expected_url)
    
    def test_parse_schedule_data_from_html_table(self):
        """Test parsing schedule data from HTML table structure"""
        # Arrange
        html = '''
        <table>
            <tr>
                <td>THR103A</td>
                <td>Intro to Theatre</td>
                <td>LEC</td>
                <td>TTH</td>
                <td>12:00PM</td>
                <td>01:20PM</td>
                <td>H*LA</td>
                <td>27</td>
                <td>3.00</td>
            </tr>
            <tr>
                <td>ENG101A</td>
                <td>English Composition</td>
                <td>LEC</td>
                <td>MWF</td>
                <td>09:00AM</td>
                <td>10:00AM</td>
                <td>WI</td>
                <td>15</td>
                <td>3.00</td>
            </tr>
        </table>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        # Act
        result = self.scraper.parse_schedule_data(soup)
        
        # Assert
        self.assertEqual(len(result), 2)  # Two departments
        self.assertIn('THR', result)
        self.assertIn('ENG', result)
        
        thr_courses = result['THR']
        self.assertEqual(len(thr_courses), 1)
        self.assertEqual(thr_courses[0]['number'], 'THR103A')
        self.assertEqual(thr_courses[0]['days'], 'TTH')
        
        eng_courses = result['ENG']
        self.assertEqual(len(eng_courses), 1)
        self.assertEqual(eng_courses[0]['number'], 'ENG101A')
        self.assertEqual(eng_courses[0]['days'], 'MWF')


class TestScheduleScraperCLIIntegration(unittest.TestCase):
    """Test CLI integration for schedule scraping"""
    
    @patch('scrape_descriptions.CourseScheduleScraper')
    @patch('scrape_descriptions.os.path.exists')
    @patch('scrape_descriptions.os.listdir')
    def test_cli_schedules_flag_with_semester(self, mock_listdir, mock_exists, mock_scraper_class):
        """Test CLI with --schedules flag and specific semester"""
        # Arrange
        mock_scraper = MagicMock()
        mock_scraper_class.return_value = mock_scraper
        mock_scraper.scrape_semester_schedule.return_value = True
        
        # Import and test main function
        from scrape_descriptions import main
        
        # Mock command line arguments
        import argparse
        test_args = ['--schedules', '--semester', '25_FA']
        
        with patch('sys.argv', ['scrape_descriptions.py'] + test_args):
            # Act
            main()
        
        # Assert
        mock_scraper.scrape_semester_schedule.assert_called_once_with('25_FA')


if __name__ == '__main__':
    unittest.main()
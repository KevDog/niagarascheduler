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

class TestCLIHelpFunctionality(unittest.TestCase):
    """Test CLI help and information functions"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test data structure
        departments_dir = os.path.join(self.temp_dir, 'departments')
        os.makedirs(departments_dir)
        
        # Create mock department files
        test_dept_data = {
            "name": "Theater Arts",
            "mission_statement": "Excellence in theater",
            "office": None,
            "course_listing_url": None,
            "course_descriptions_url": None,
            "courses": [
                {"number": "101", "title": "Intro to Theater", "description": "Basic theater course"},
                {"number": "201", "title": "Advanced Theater", "description": "Advanced course"}
            ]
        }
        
        with open(os.path.join(departments_dir, 'THR.json'), 'w') as f:
            json.dump(test_dept_data, f)
        
        # Create semester data
        semesters_dir = os.path.join(self.temp_dir, 'semesters', '25_FA')
        os.makedirs(semesters_dir)
        
        semester_data = [
            {"number": "THR101A", "name": "Intro to Theater", "credits": "3.00", "days": "MW", "start_time": "10:00AM", "end_time": "11:00AM"}
        ]
        
        with open(os.path.join(semesters_dir, 'THR.json'), 'w') as f:
            json.dump(semester_data, f)
    
    @patch('scrape_descriptions.list_departments')
    def test_list_departments_option(self, mock_list_departments):
        """Test --list-departments flag calls the function and exits"""
        from scrape_descriptions import main
        
        with patch('sys.argv', ['scrape_descriptions.py', '--list-departments']):
            # Act
            main()
        
        # Assert
        mock_list_departments.assert_called_once_with('./data')
    
    @patch('scrape_descriptions.list_semesters')
    def test_list_semesters_option(self, mock_list_semesters):
        """Test --list-semesters flag calls the function and exits"""
        from scrape_descriptions import main
        
        with patch('sys.argv', ['scrape_descriptions.py', '--list-semesters']):
            # Act
            main()
        
        # Assert
        mock_list_semesters.assert_called_once_with('./data')
    
    @patch('scrape_descriptions.show_stats')
    def test_stats_option(self, mock_show_stats):
        """Test --stats flag calls the function and exits"""
        from scrape_descriptions import main
        
        with patch('sys.argv', ['scrape_descriptions.py', '--stats']):
            # Act
            main()
        
        # Assert
        mock_show_stats.assert_called_once_with('./data')
    
    def test_list_departments_output(self):
        """Test that list_departments produces expected output"""
        from scrape_descriptions import list_departments
        import io
        import sys
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            # Act
            list_departments(self.temp_dir)
            output = captured_output.getvalue()
            
            # Assert
            self.assertIn('Available departments', output)
            self.assertIn('THR', output)
            self.assertIn('Theater Arts', output)
        finally:
            sys.stdout = sys.__stdout__
    
    def test_show_stats_output(self):
        """Test that show_stats produces expected output"""
        from scrape_descriptions import show_stats
        import io
        import sys
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            # Act
            show_stats(self.temp_dir)
            output = captured_output.getvalue()
            
            # Assert
            self.assertIn('Course Data Statistics', output)
            self.assertIn('Departments: 1', output)
            self.assertIn('Total Courses: 2', output)
            self.assertIn('25_FA:', output)
        finally:
            sys.stdout = sys.__stdout__


if __name__ == '__main__':
    unittest.main()
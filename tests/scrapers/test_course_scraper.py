#!/usr/bin/env python

"""
Tests for course scraper CLI functionality
"""

import unittest
from utilities.course_scraper import CourseScraperCLI
from core.offering import Offering
from core.department import Department


class TestCourseScraperCLI(unittest.TestCase):
    
    def test_build_query_url_basic(self):
        # Arrange
        scraper = CourseScraperCLI()
        expected_url = "https://apps.niagara.edu/courses/index.php"
        
        # Act
        result = scraper.build_query_url()
        
        # Assert
        self.assertEqual(result, expected_url)
        
    def test_build_query_url_with_semester_year(self):
        # Arrange
        scraper = CourseScraperCLI()
        expected_url = "https://apps.niagara.edu/courses/index.php?semester=25/FA"
        
        # Act
        result = scraper.build_query_url(semester="25/FA")
        
        # Assert
        self.assertEqual(result, expected_url)
        
    def test_build_query_url_with_graduate_flag(self):
        # Arrange
        scraper = CourseScraperCLI()
        expected_url = "https://apps.niagara.edu/courses/index.php?ug=1"
        
        # Act
        result = scraper.build_query_url(undergraduate=True)
        
        # Assert
        self.assertEqual(result, expected_url)
        
    def test_build_query_url_with_all_parameters(self):
        # Arrange
        scraper = CourseScraperCLI()
        expected_url = "https://apps.niagara.edu/courses/index.php?semester=25/FA&ug=1"
        
        # Act
        result = scraper.build_query_url(semester="25/FA", undergraduate=True)
        
        # Assert
        self.assertEqual(result, expected_url)
        
    def test_fetch_course_page(self):
        # Arrange
        scraper = CourseScraperCLI()
        
        # Act
        html_content = scraper.fetch_course_page("25/FA", ug=True)
        
        # Assert
        self.assertIsInstance(html_content, str)
        self.assertGreater(len(html_content), 0)
        
    def test_parse_course_data(self):
        # Arrange
        scraper = CourseScraperCLI()
        sample_html = '''
        <tr class="available">
            <td class="number"><a href="course.php?coursenum=25/FA*THR*101*A1&semester=25/FA&ug=1" class="modal-trigger">THR101A1</a></td>
            <td class="name">Intro to Theatre</td>
            <td class="name">LEC</td>
            <td class="days">MWF</td>
            <td class="start">10:00AM</td>
            <td class="end">11:00AM</td>
            <td class="designation">H*AE</td>
            <td class="availability">15</td>
            <td class="credits">3.00</td>
        </tr>
        '''
        
        # Act
        courses = scraper.parse_course_data(sample_html)
        
        # Assert
        self.assertEqual(len(courses), 1)
        course = courses[0]
        self.assertEqual(course['number'], 'THR101A1')
        self.assertEqual(course['name'], 'Intro to Theatre')
        self.assertEqual(course['credits'], '3.00')
        
    def test_organize_courses_by_department(self):
        # Arrange
        scraper = CourseScraperCLI()
        courses = [
            {'number': 'THR101A1', 'name': 'Intro to Theatre', 'credits': '3.00'},
            {'number': 'ACC111A1', 'name': 'Financial Accounting', 'credits': '3.00'},
            {'number': 'THR223A1', 'name': 'Acting I', 'credits': '3.00'}
        ]
        
        # Act
        organized = scraper.organize_courses_by_department(courses)
        
        # Assert
        self.assertIn('THR', organized)
        self.assertIn('ACC', organized)
        self.assertEqual(len(organized['THR']), 2)
        self.assertEqual(len(organized['ACC']), 1)
        
    def test_parse_offerings_from_courses(self):
        # Arrange
        scraper = CourseScraperCLI()
        courses = [
            {'number': 'THR101A1', 'name': 'Intro to Theatre', 'credits': '3.00', 'delivery_type': 'LEC'},
            {'number': 'ACC111B1', 'name': 'Financial Accounting', 'credits': '3.00', 'delivery_type': 'ONLA'}
        ]
        
        # Act
        offerings = scraper.parse_offerings_from_courses(courses)
        
        # Assert
        self.assertEqual(len(offerings), 2)
        self.assertIsInstance(offerings[0], Offering)
        self.assertEqual(offerings[0].code, 'THR101A1')
        self.assertEqual(offerings[0].department, 'THR')
        self.assertEqual(offerings[0].number, '101')
        self.assertEqual(offerings[0].section, 'A')
        
    def test_create_semester_departments(self):
        # Arrange
        scraper = CourseScraperCLI()
        offerings = [
            Offering('THR101A1', credits=3.0, delivery_type='LEC'),
            Offering('THR223B1', credits=3.0, delivery_type='ONLA'),
            Offering('ACC111A1', credits=3.0, delivery_type='LEC')
        ]
        
        # Act
        departments = scraper.create_semester_departments(offerings)
        
        # Assert
        self.assertIn('THR', departments)
        self.assertIn('ACC', departments)
        self.assertIsInstance(departments['THR'], Department)
        self.assertEqual(len(departments['THR'].courses), 2)
        
    def test_update_department_json_files(self):
        # Arrange
        scraper = CourseScraperCLI()
        organized_courses = {
            'THR': [
                {'number': 'THR101A1', 'name': 'Intro to Theatre', 'credits': '3.00'}
            ]
        }
        
        # Act & Assert
        # This should not raise an exception
        scraper.update_department_json_files(organized_courses, '/tmp/test_data', '25/FA')


if __name__ == '__main__':
    unittest.main()
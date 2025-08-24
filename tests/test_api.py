#!/usr/bin/env python

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import patch, mock_open
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import API after path setup
import api


class TestAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.app = api.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_health_check(self):
        """Test health check endpoint"""
        # Act
        response = self.client.get('/api/health')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['version'], '1.0.0')
    
    def test_get_config_returns_semesters(self):
        """Test config endpoint returns semester information"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock semester directories
            semester_dir = os.path.join(temp_dir, 'semesters')
            os.makedirs(semester_dir)
            os.makedirs(os.path.join(semester_dir, '25_FA'))
            os.makedirs(os.path.join(semester_dir, '25_SP'))
            
            # Mock the data directory
            with patch.object(api, 'data_dir', temp_dir):
                # Act
                response = self.client.get('/api/config')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('semesters', data)
        self.assertEqual(len(data['semesters']), 2)
        
        # Check semester format
        semester_keys = [s['key'] for s in data['semesters']]
        self.assertIn('25_FA', semester_keys)
        self.assertIn('25_SP', semester_keys)
    
    @patch('api.data_loader.get_all_departments')
    @patch('api.data_loader.load_department')
    def test_get_departments(self, mock_load_dept, mock_get_all_depts):
        """Test departments endpoint returns department list"""
        # Arrange
        from core.department import Department
        mock_get_all_depts.return_value = ['THR', 'ENG']
        mock_dept = Department('Theater Arts', mission_statement='Excellence in theater')
        mock_load_dept.return_value = mock_dept
        
        # Act
        response = self.client.get('/api/departments')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('departments', data)
        self.assertEqual(len(data['departments']), 2)
        self.assertEqual(data['departments'][0]['name'], 'Theater Arts')
    
    @patch('api.data_loader.load_department')
    def test_get_department_with_courses(self, mock_load_dept):
        """Test specific department endpoint returns courses"""
        # Arrange
        from core.department import Department
        from core.course import Course
        course = Course("101", title="Intro to Theater", description="Basic theater course")
        mock_dept = Department('Theater Arts', courses=[course])
        mock_load_dept.return_value = mock_dept
        
        # Act
        response = self.client.get('/api/departments/THR')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Theater Arts')
        self.assertEqual(len(data['courses']), 1)
        self.assertEqual(data['courses'][0]['number'], '101')
    
    def test_get_department_not_found(self):
        """Test department endpoint returns 404 for non-existent department"""
        # Act
        response = self.client.get('/api/departments/NONEXISTENT')
        
        # Assert
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_course_offerings(self):
        """Test course offerings endpoint returns schedule data"""
        # Arrange
        mock_offerings_data = [
            {
                "number": "THR103A",
                "name": "Intro to Theatre",
                "credits": "3.00",
                "days": "TTH",
                "start_time": "12:00PM",
                "end_time": "01:20PM"
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock semester file
            semester_dir = os.path.join(temp_dir, 'semesters', '25_FA')
            os.makedirs(semester_dir)
            thr_file = os.path.join(semester_dir, 'THR.json')
            with open(thr_file, 'w') as f:
                json.dump(mock_offerings_data, f)
            
            # Mock the data directory
            with patch.object(api, 'data_dir', temp_dir):
                # Act
                response = self.client.get('/api/offerings/25_FA/THR/103')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('offerings', data)
        self.assertEqual(len(data['offerings']), 1)
        offering = data['offerings'][0]
        self.assertEqual(offering['days'], 'TTH')
        self.assertEqual(offering['start_time'], '12:00PM')
        self.assertEqual(offering['end_time'], '01:20PM')
    
    def test_get_course_offerings_no_file(self):
        """Test course offerings endpoint returns empty list when no data file exists"""
        # Act
        response = self.client.get('/api/offerings/25_FA/NONEXISTENT/101')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['offerings'], [])


if __name__ == '__main__':
    unittest.main()
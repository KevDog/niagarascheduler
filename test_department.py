#!/usr/bin/env python

import unittest
import json
from department import Department


class TestDepartment(unittest.TestCase):
    
    def test_department_has_name(self):
        """A department has a name"""
        # Arrange
        department_name = "Theater Arts"
        
        # Act
        dept = Department(department_name)
        
        # Assert
        self.assertEqual(dept.name, department_name)
    
    def test_department_serializes_to_json(self):
        """A department can be serialized to JSON"""
        # Arrange
        dept = Department("Theater Arts")
        
        # Act
        json_output = dept.to_json()
        
        # Assert
        self.assertIsInstance(json_output, str)
        data = json.loads(json_output)
        self.assertEqual(data["name"], "Theater Arts")
    
    def test_department_has_mission_statement(self):
        """A department has a mission statement"""
        # Arrange
        department_name = "Theater Arts"
        mission_statement = "To provide comprehensive education in theatrical arts"
        
        # Act
        dept = Department(department_name, mission_statement)
        
        # Assert
        self.assertEqual(dept.mission_statement, mission_statement)
    
    def test_department_has_office(self):
        """A department has an office"""
        # Arrange
        department_name = "Theater Arts"
        office_location = "Castellani Art Museum Building, Room 201"
        
        # Act
        dept = Department(department_name, office=office_location)
        
        # Assert
        self.assertEqual(dept.office, office_location)


if __name__ == '__main__':
    unittest.main()
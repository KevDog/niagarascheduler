#!/usr/bin/env python

"""
Course Description Manager for Niagara University Scheduler

Handles loading and retrieving course descriptions from JSON data files.
"""

import json
import os


class CourseDescriptionManager:
    """Manages course description data from JSON files"""
    
    def __init__(self, data_file_path):
        """Initialize with path to course data JSON file"""
        self.data_file_path = data_file_path
        self._course_data = None
    
    def load_course_data(self):
        """Load course data from JSON file"""
        with open(self.data_file_path, 'r') as f:
            self._course_data = json.load(f)
        return self._course_data
    
    def get_course_description(self, course_id):
        """Get course description for given course ID"""
        if self._course_data is None:
            self.load_course_data()
        
        if course_id in self._course_data:
            return self._course_data[course_id]['description']
        return 'Course description not found, insert manually'
    
    def get_course_info(self, course_id):
        """Get complete course information for given course ID"""
        if self._course_data is None:
            self.load_course_data()
        
        if course_id in self._course_data:
            return self._course_data[course_id]
        return None
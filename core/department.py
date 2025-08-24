#!/usr/bin/env python

import json

class Department:
    def __init__(self, name, mission_statement=None, office=None, course_listing_url=None, course_descriptions_url=None, courses=None):
        self.name = name
        self.mission_statement = mission_statement
        self.office = office
        self.course_listing_url = course_listing_url
        self.course_descriptions_url = course_descriptions_url
        self.courses = courses if courses is not None else []
    
    def to_json(self):
        """Serialize department to JSON string"""
        department_data = {
            "name": self.name,
            "mission_statement": self.mission_statement,
            "office": self.office,
            "course_listing_url": self.course_listing_url,
            "course_descriptions_url": self.course_descriptions_url,
            "courses": [course.to_dict() if hasattr(course, 'to_dict') else course for course in self.courses]
        }
        return json.dumps(department_data, indent=4)
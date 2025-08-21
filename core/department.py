#!/usr/bin/env python

import json

class Department:
    def __init__(self, name, mission_statement=None, office=None, course_listing_url=None):
        self.name = name
        self.mission_statement = mission_statement
        self.office = office
        self.course_listing_url = course_listing_url
    
    def to_json(self):
        """Serialize department to JSON string"""
        return json.dumps({"name": self.name})
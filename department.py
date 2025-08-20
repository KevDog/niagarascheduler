#!/usr/bin/env python

import json

class Department:
    def __init__(self, name, mission_statement=None):
        self.name = name
        self.mission_statement = mission_statement
    
    def to_json(self):
        """Serialize department to JSON string"""
        return json.dumps({"name": self.name})
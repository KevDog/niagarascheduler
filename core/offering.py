#!/usr/bin/env python

import re

class Offering:
    def __init__(self, code, delivery_type=None, designation=None, credits=None, instructors=None, textbooks=None, zoom_link=None, meeting_days=None):
        self.code = code
        self.delivery_type = delivery_type
        self.designation = designation
        self.credits = float(credits) if credits is not None else None
        self.instructors = instructors if instructors is not None else []
        self.textbooks = textbooks if textbooks is not None else []
        self.zoom_link = zoom_link
        self.meeting_days = meeting_days if meeting_days is not None else []
        self._parse_code()
    
    def _parse_code(self):
        """Parse offering code into components"""
        # Pattern: {DEPT}{NUMBER}{TYPE}{SECTION}{SUBSECTION}
        # Examples: THR101A1, ACC425LA1, THR223B1
        match = re.match(r'^([A-Z]+)(\d+)([A-Z]*)([A-Z])(\d*)$', self.code)
        if match:
            self.department = match.group(1)
            self.number = match.group(2)
            self.type = match.group(3)  # "" for regular, "L" for lab, etc.
            self.section = match.group(4)  # A, B, C, etc.
            self.subsection = match.group(5)  # 1, 2, etc.
        else:
            self.department = None
            self.number = None
            self.type = None
            self.section = None
            self.subsection = None
    
    def to_dict(self):
        """Serialize offering to dictionary"""
        return {
            "code": self.code,
            "delivery_type": self.delivery_type,
            "designation": self.designation,
            "credits": self.credits,
            "instructors": self.instructors,
            "textbooks": self.textbooks,
            "zoom_link": self.zoom_link,
            "meeting_days": self.meeting_days,
            "department": self.department,
            "number": self.number,
            "type": self.type,
            "section": self.section,
            "subsection": self.subsection
        }
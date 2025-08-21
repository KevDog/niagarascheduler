#!/usr/bin/env python

class Course:
    def __init__(self, number, title=None, description=None, instructors=None, textbooks=None, zoom_link=None, meeting_days=None):
        self.number = number
        self.title = title
        self.description = description
        self.instructors = instructors if instructors is not None else []
        self.textbooks = textbooks if textbooks is not None else []
        self.zoom_link = zoom_link
        self.meeting_days = meeting_days if meeting_days is not None else []
    
    def to_dict(self):
        """Serialize course to dictionary"""
        return {
            "number": self.number,
            "title": self.title,
            "description": self.description,
            "instructors": self.instructors,
            "textbooks": self.textbooks,
            "zoom_link": self.zoom_link,
            "meeting_days": self.meeting_days
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Course object from dictionary"""
        return cls(
            number=data.get("number"),
            title=data.get("title"),
            description=data.get("description"),
            instructors=data.get("instructors"),
            textbooks=data.get("textbooks"),
            zoom_link=data.get("zoom_link"),
            meeting_days=data.get("meeting_days")
        )
#!/usr/bin/env python

class Course:
    def __init__(self, number, title=None, description=None, instructors=None, textbooks=None, zoom_link=None):
        self.number = number
        self.title = title
        self.description = description
        self.instructors = instructors if instructors is not None else []
        self.textbooks = textbooks if textbooks is not None else []
        self.zoom_link = zoom_link
    
    def to_dict(self):
        """Serialize course to dictionary"""
        result = {
            "number": self.number,
            "title": self.title,
            "description": self.description,
            "instructors": self.instructors,
            "textbooks": self.textbooks,
            "zoom_link": self.zoom_link
        }
        
        return result
    
    @classmethod
    def from_dict(cls, data):
        """Create Course object from dictionary"""
        return cls(
            number=data.get("number"),
            title=data.get("title"),
            description=data.get("description"),
            instructors=data.get("instructors"),
            textbooks=data.get("textbooks"),
            zoom_link=data.get("zoom_link")
        )
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
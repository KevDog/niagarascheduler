"""
Calendar Service for Academic Calendar Management

This service handles loading and processing academic calendar data
from JSON files for schedule generation and class date calculation.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class CalendarService:
    """Service for managing academic calendar data and class scheduling"""
    
    def __init__(self, base_path: str = None):
        """Initialize the calendar service with base path to calendar data"""
        if base_path is None:
            # Default to calendars folder in project root
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            base_path = os.path.join(current_dir, 'calendars')
        
        self.calendars_path = base_path
        self._calendar_cache = {}
        logger.info(f"CalendarService initialized with path: {self.calendars_path}")

    def get_calendar(self, semester: str) -> Optional[Dict[str, Any]]:
        """Get calendar data for a specific semester"""
        try:
            # Map semester keys to file names
            semester_files = {
                '25_FA': 'fall_2025.json',
                '25_SU': 'summer_2025.json',
                '26_SP': 'spring_2026.json'
            }
            
            filename = semester_files.get(semester)
            if not filename:
                logger.warning(f"No calendar file mapping for semester: {semester}")
                return None
                
            # Check cache first (disable for now to ensure fresh data)
            # if semester in self._calendar_cache:
            #     return self._calendar_cache[semester]
                
            calendar_file = os.path.join(self.calendars_path, filename)
            
            if not os.path.exists(calendar_file):
                logger.warning(f"Calendar file not found: {calendar_file}")
                return None
                
            with open(calendar_file, 'r', encoding='utf-8') as f:
                calendar_data = json.load(f)
                
            # Cache the data
            self._calendar_cache[semester] = calendar_data
            logger.info(f"Loaded calendar data for {semester}: {len(calendar_data.get('events', []))} events")
            
            return calendar_data
            
        except Exception as e:
            logger.error(f"Error loading calendar for {semester}: {str(e)}")
            return None

    def generate_class_dates(self, semester: str, meeting_days: str, 
                           start_date: str = None, end_date: str = None) -> List[str]:
        """
        Generate specific class meeting dates based on meeting days pattern
        
        Args:
            semester: Semester key (e.g., '25_FA')
            meeting_days: Days pattern (e.g., 'MW', 'TTH', 'MWF')
            start_date: Override start date (YYYY-MM-DD)
            end_date: Override end date (YYYY-MM-DD)
        
        Returns:
            List of class meeting dates in YYYY-MM-DD format
        """
        try:
            calendar_data = self.get_calendar(semester)
            if not calendar_data:
                return []
                
            # Use provided dates or fall back to calendar defaults
            semester_start = start_date or calendar_data.get('first_day')
            semester_end = end_date or calendar_data.get('last_day')
            
            if not semester_start or not semester_end or semester_start == 'TBD':
                logger.warning(f"Invalid semester dates for {semester}")
                return []
                
            # Parse meeting days pattern - handle multi-character patterns like "TH"
            meeting_days = meeting_days.upper()
            class_days = []
            
            # Process string to handle "TH" for Thursday
            i = 0
            while i < len(meeting_days):
                if i < len(meeting_days) - 1 and meeting_days[i:i+2] == 'TH':
                    # Thursday
                    class_days.append(3)  # Thursday is weekday 3
                    i += 2
                elif meeting_days[i] == 'M':
                    # Monday
                    class_days.append(0)
                    i += 1
                elif meeting_days[i] == 'T':
                    # Tuesday (only if not followed by H)
                    if i >= len(meeting_days) - 1 or meeting_days[i+1] != 'H':
                        class_days.append(1)
                    i += 1
                elif meeting_days[i] == 'W':
                    # Wednesday
                    class_days.append(2)
                    i += 1
                elif meeting_days[i] == 'R':
                    # Thursday (alternative notation)
                    class_days.append(3)
                    i += 1
                elif meeting_days[i] == 'F':
                    # Friday
                    class_days.append(4)
                    i += 1
                elif meeting_days[i] == 'S':
                    # Saturday
                    class_days.append(5)
                    i += 1
                elif meeting_days[i] == 'U':
                    # Sunday
                    class_days.append(6)
                    i += 1
                else:
                    # Skip unknown characters
                    i += 1
                    
            if not class_days:
                logger.warning(f"No valid meeting days found in: {meeting_days}")
                return []
                
            # Generate dates
            start = datetime.strptime(semester_start, '%Y-%m-%d')
            end = datetime.strptime(semester_end, '%Y-%m-%d')
            
            class_dates = []
            current_date = start
            
            # Get no-class dates from calendar
            no_class_dates = set(calendar_data.get('no_class_dates', []))
            
            # Add holiday dates from events
            for event in calendar_data.get('events', []):
                if event.get('type') == 'holiday' or 'break' in event.get('name', '').lower():
                    if event.get('date'):
                        no_class_dates.add(event['date'])
                    # Handle date ranges for multi-day holidays
                    if event.get('date_range'):
                        try:
                            start_date = datetime.strptime(event['date'], '%Y-%m-%d')
                            end_date = datetime.strptime(event['date_range'], '%Y-%m-%d')
                            current = start_date
                            while current <= end_date:
                                no_class_dates.add(current.strftime('%Y-%m-%d'))
                                current += timedelta(days=1)
                        except (ValueError, KeyError):
                            logger.warning(f"Invalid date range in event: {event}")
                        
            while current_date <= end:
                # Check if this date matches a class day
                if current_date.weekday() in class_days:
                    date_str = current_date.strftime('%Y-%m-%d')
                    # Skip if it's a no-class date
                    if date_str not in no_class_dates:
                        class_dates.append(date_str)
                        
                current_date += timedelta(days=1)
                
            logger.info(f"Generated {len(class_dates)} class dates for {semester} {meeting_days}")
            return class_dates
            
        except Exception as e:
            logger.error(f"Error generating class dates: {str(e)}")
            return []

    def get_semester_events(self, semester: str, event_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get academic events for a semester, optionally filtered by type
        
        Args:
            semester: Semester key
            event_types: List of event types to filter (e.g., ['holiday', 'academic_deadline'])
        
        Returns:
            List of events sorted by date
        """
        try:
            calendar_data = self.get_calendar(semester)
            if not calendar_data:
                return []
                
            events = calendar_data.get('events', [])
            
            # Filter by event types if specified
            if event_types:
                events = [event for event in events if event.get('type') in event_types]
                
            # Sort by date
            events.sort(key=lambda x: x.get('date', ''))
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting semester events: {str(e)}")
            return []
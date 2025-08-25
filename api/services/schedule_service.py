"""
Schedule service for handling schedule generation business logic
"""
import os
from typing import List, Dict, Any, Tuple
from utilities.scheduler import (
    make_url, sorted_classes, schedule, date_formats,
    parse_registrar_table, fetch_registrar_table,
    discover_available_semesters
)

class ScheduleService:
    """Service class for schedule generation operations"""
    
    def __init__(self, data_dir: str):
        """
        Initialize schedule service
        
        Args:
            data_dir: Path to data directory
        """
        self.data_dir = data_dir
    
    def get_available_semesters(self) -> List[Dict[str, str]]:
        """
        Get list of available semesters with formatted display names
        
        Returns:
            List of semester dictionaries with key, semester, year, and display
        """
        semesters_dir = os.path.join(self.data_dir, 'semesters')
        available_semesters = []
        
        if os.path.exists(semesters_dir):
            for semester_folder in os.listdir(semesters_dir):
                if os.path.isdir(os.path.join(semesters_dir, semester_folder)):
                    semester_info = self._parse_semester_code(semester_folder)
                    if semester_info:
                        available_semesters.append(semester_info)
        
        # Sort semesters by year and season
        available_semesters.sort(key=lambda x: (x['year'], x['semester']))
        return available_semesters
    
    def get_date_formats(self) -> List[Dict[str, str]]:
        """
        Get available date formats
        
        Returns:
            List of format dictionaries with key and value
        """
        formats = date_formats()
        return [{'key': key, 'value': value} for key, value in formats]
    
    def generate_schedule(self, semester_year: str, weekdays: List[str], 
                         date_format: str = '', show_holidays: bool = True,
                         show_breaks: bool = True, show_events: bool = True) -> Dict[str, Any]:
        """
        Generate class schedule for given parameters
        
        Args:
            semester_year: Semester code (e.g., '25_FA')
            weekdays: List of weekdays for classes
            date_format: Date format preference
            show_holidays: Include holidays in schedule
            show_breaks: Include breaks in schedule  
            show_events: Include other events in schedule
        
        Returns:
            Dictionary with schedule data and metadata
            
        Raises:
            Exception: If schedule generation fails
        """
        try:
            # Parse semester and year
            semester, year = self._parse_semester_year(semester_year)
            
            # Get date format
            date_fmt = self._get_date_format(date_format)
            
            # Generate schedule using scheduler utilities
            url = make_url(semester, year)
            calendar_data = fetch_registrar_table(url, semester, year)
            first_day, last_day, no_classes, events = parse_registrar_table(calendar_data)
            possible_classes, no_classes = sorted_classes(weekdays, first_day, last_day, no_classes)
            
            course_schedule = schedule(
                possible_classes, no_classes, show_no=True, fmt=date_fmt, events=events,
                show_holidays=show_holidays, show_breaks=show_breaks, show_events=show_events
            )
            
            return {
                'schedule': course_schedule,
                'semester': semester,
                'year': year,
                'semester_code': semester_year,
                'first_day': first_day.isoformat() if first_day else None,
                'last_day': last_day.isoformat() if last_day else None,
                'weekdays': weekdays,
                'date_format': date_fmt,
                'settings': {
                    'show_holidays': show_holidays,
                    'show_breaks': show_breaks,
                    'show_events': show_events
                }
            }
            
        except Exception as e:
            raise Exception(f'Error generating schedule: {str(e)}')
    
    def _parse_semester_code(self, semester_folder: str) -> Dict[str, str]:
        """
        Parse semester folder name into readable format
        
        Args:
            semester_folder: Folder name like "25_FA"
        
        Returns:
            Semester info dictionary or None if invalid
        """
        if '_' not in semester_folder:
            return None
            
        try:
            year_part, season_part = semester_folder.split('_', 1)
            
            # Convert season abbreviations to full names
            season_map = {
                'FA': 'Fall',
                'SP': 'Spring',
                'SU': 'Summer', 
                'WI': 'Winter'
            }
            
            full_season = season_map.get(season_part, season_part)
            full_year = f"20{year_part}" if len(year_part) == 2 else year_part
            
            return {
                'key': semester_folder,
                'semester': full_season,
                'year': full_year,
                'display': f"{full_season} {full_year}"
            }
        except ValueError:
            return None
    
    def _parse_semester_year(self, semester_year: str) -> Tuple[str, str]:
        """
        Parse semester_year code into semester and year components
        
        Args:
            semester_year: Code like '25_FA'
        
        Returns:
            Tuple of (semester, year)
        """
        if '_' not in semester_year:
            raise ValueError(f"Invalid semester format: {semester_year}")
            
        year_part, season_part = semester_year.split('_', 1)
        
        # Convert to full names expected by scheduler
        season_map = {
            'FA': 'fall',
            'SP': 'spring',
            'SU': 'summer',
            'WI': 'winter'
        }
        
        semester = season_map.get(season_part.upper())
        if not semester:
            raise ValueError(f"Invalid season: {season_part}")
            
        # Convert year to full format
        year = f"20{year_part}" if len(year_part) == 2 else year_part
        
        return semester, year
    
    def _get_date_format(self, requested_format: str = '') -> str:
        """
        Get date format, with fallback to default
        
        Args:
            requested_format: Requested format key
        
        Returns:
            Date format string
        """
        available_formats = date_formats()
        
        if requested_format:
            matching_formats = [fmt for key, fmt in available_formats if key == requested_format]
            if matching_formats:
                return matching_formats[0]
        
        # Return default format
        return available_formats[0][1] if available_formats else '%m/%d'
#!/usr/bin/env python

"""
Course scraper CLI for Niagara University course details
"""

import requests
from bs4 import BeautifulSoup
import os
import json
import sys

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.offering import Offering
from core.department import Department


class CourseScraperCLI:
    """CLI tool for scraping course information from Niagara University"""
    
    BASE_URL = "https://apps.niagara.edu/courses/index.php"
    
    def build_query_url(self, semester=None, undergraduate=None):
        """Build query URL with optional parameters"""
        url = self.BASE_URL
        params = []
        
        if semester:
            params.append(f"semester={semester}")
        
        if undergraduate:
            params.append("ug=1")
        
        if params:
            url += "?" + "&".join(params)
        
        return url
    
    def fetch_course_page(self, semester, ug=False, grad=False):
        """Fetch course page HTML content"""
        if ug:
            url = self.build_query_url(semester=semester, undergraduate=True)
        else:
            url = self.build_query_url(semester=semester, undergraduate=False)
        
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    
    def parse_course_data(self, html_content):
        """Parse course data from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        courses = []
        
        for row in soup.find_all('tr', class_=['available', 'unavailable']):
            tds = row.find_all('td')
            if len(tds) >= 9:
                course = {
                    'number': tds[0].get_text().strip(),
                    'name': tds[1].get_text().strip(),
                    'delivery_type': tds[2].get_text().strip() if len(tds) > 2 else None,
                    'days': tds[3].get_text().strip() if len(tds) > 3 else None,
                    'start_time': tds[4].get_text().strip() if len(tds) > 4 else None,
                    'end_time': tds[5].get_text().strip() if len(tds) > 5 else None,
                    'designation': tds[6].get_text().strip() if len(tds) > 6 else None,
                    'availability': tds[7].get_text().strip() if len(tds) > 7 else None,
                    'credits': tds[8].get_text().strip() if len(tds) > 8 else None
                }
                courses.append(course)
        
        return courses
    
    def parse_offerings_from_courses(self, courses):
        """Convert course data to Offering objects"""
        offerings = []
        
        for course in courses:
            # Convert meeting days to list
            meeting_days = []
            if course.get('days'):
                days_str = course['days']
                # Parse days like "MWF" into ["Monday", "Wednesday", "Friday"]
                day_map = {'M': 'Monday', 'T': 'Tuesday', 'W': 'Wednesday', 'R': 'Thursday', 'F': 'Friday', 'S': 'Saturday', 'U': 'Sunday'}
                for char in days_str:
                    if char in day_map:
                        meeting_days.append(day_map[char])
            
            offering = Offering(
                code=course['number'],
                delivery_type=course.get('delivery_type'),
                designation=course.get('designation'),
                credits=float(course['credits']) if course.get('credits') else None,
                meeting_days=meeting_days
            )
            offerings.append(offering)
        
        return offerings
    
    def create_semester_departments(self, offerings):
        """Create Department objects with Course+Offering structure"""
        from core.course import Course

        
        dept_dict = {}
        
        for offering in offerings:
            dept_code = offering.department
            course_number = offering.number
            
            # Initialize department if needed
            if dept_code not in dept_dict:
                dept_dict[dept_code] = Department(name=f"{dept_code} Department")
            
            # Find or create course
            course = None
            for existing_course in dept_dict[dept_code].courses:
                if existing_course.number == course_number:
                    course = existing_course
                    break
            
            if course is None:
                # Create new course with empty offerings list
                course = Course(number=course_number, title=f"{dept_code} {course_number}")
                course.offerings = []  # Add offerings attribute
                dept_dict[dept_code].courses.append(course)
            
            # Add offering to course
            course.offerings.append(offering)
        
        return dept_dict
    
    def organize_courses_by_department(self, courses):
        """Organize courses by department prefix (legacy method)"""
        organized = {}
        
        for course in courses:
            # Extract department prefix from course number (e.g., THR from THR101A1)
            course_number = course['number']
            department = ''.join([c for c in course_number if c.isalpha()])[:3]
            
            if department not in organized:
                organized[department] = []
            
            organized[department].append(course)
        
        return organized
    
    def update_department_json_files(self, organized_courses, output_dir, semester):
        """Update department JSON files with scraped course data (legacy)"""
        # Create semester-specific directory
        semester_dir = os.path.join(output_dir, semester.replace('/', '_'))
        os.makedirs(semester_dir, exist_ok=True)
        
        for department, courses in organized_courses.items():
            file_path = os.path.join(semester_dir, f"{department}.json")
            
            # For minimal implementation, just write the courses to JSON
            # In full implementation, this would integrate with existing Course/Department objects
            with open(file_path, 'w') as f:
                json.dump(courses, f, indent=2)
    
    def save_semester_departments(self, departments, output_dir, semester):
        """Save Department objects to JSON files using object serialization"""
        # Create semester-specific directory under semesters/
        semester_dir = os.path.join(output_dir, 'semesters', semester.replace('/', '_'))
        os.makedirs(semester_dir, exist_ok=True)
        
        for dept_code, department in departments.items():
            file_path = os.path.join(semester_dir, f"{dept_code}.json")
            
            # Use Department's to_json method for proper serialization
            with open(file_path, 'w') as f:
                f.write(department.to_json())
    
    def scrape_courses(self, semester, ug=False, grad=False, output_dir='/data'):
        """Scrape courses with specified parameters"""
        all_courses = []
        
        # Scrape undergraduate courses if requested
        if ug:
            print(f"Scraping undergraduate courses for {semester}...")
            ug_html = self.fetch_course_page(semester, ug=True)
            ug_courses = self.parse_course_data(ug_html)
            all_courses.extend(ug_courses)
            print(f"Found {len(ug_courses)} undergraduate courses")
        
        # Scrape graduate courses if requested
        if grad:
            print(f"Scraping graduate courses for {semester}...")
            grad_html = self.fetch_course_page(semester, ug=False)
            grad_courses = self.parse_course_data(grad_html)
            all_courses.extend(grad_courses)
            print(f"Found {len(grad_courses)} graduate courses")
        
        # Organize and save courses using object model
        if all_courses:
            # Convert to Offering objects
            offerings = self.parse_offerings_from_courses(all_courses)
            
            # Create Department objects
            departments = self.create_semester_departments(offerings)
            
            # Save using object serialization
            self.save_semester_departments(departments, output_dir, semester)
            
            semester_dir = os.path.join(output_dir, 'semesters', semester.replace('/', '_'))
            print(f"Successfully scraped {len(all_courses)} total courses")
            print(f"Created {len(offerings)} course offerings")
            print(f"Organized into {len(departments)} departments")
            print(f"JSON files saved to: {semester_dir}")
        else:
            print("No courses found or no course types selected")
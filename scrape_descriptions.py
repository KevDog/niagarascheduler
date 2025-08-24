#!/usr/bin/env python

"""
CLI tool for scraping course descriptions from Niagara University catalog
Populates department JSON files with detailed course descriptions
"""

import argparse
import requests
from bs4 import BeautifulSoup
import json
import os
import re
from core.data_loader import DepartmentDataLoader
from core.course import Course
from core.department import Department

class CourseDescriptionScraper:
    """Scraper for course descriptions from catalog URLs"""
    
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.data_loader = DepartmentDataLoader(data_dir)
    
    def scrape_department_courses(self, dept_code):
        """Scrape course descriptions for a specific department"""
        print(f"Scraping courses for department: {dept_code}")
        
        # Load department data
        dept = self.data_loader.load_department(dept_code)
        if not dept:
            print(f"Department {dept_code} not found")
            return False
            
        if not dept.course_descriptions_url:
            print(f"No course descriptions URL found for {dept_code}")
            return False
        
        print(f"Fetching from: {dept.course_descriptions_url}")
        
        try:
            response = requests.get(dept.course_descriptions_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            courses_found = self.parse_course_descriptions(soup, dept_code)
            
            if courses_found:
                # Update department with new courses
                dept.courses.extend(courses_found)
                self.save_department(dept, dept_code)
                print(f"Successfully added {len(courses_found)} courses to {dept_code}")
                return True
            else:
                print(f"No courses found for {dept_code}")
                return False
                
        except requests.RequestException as e:
            print(f"Error fetching {dept.course_descriptions_url}: {e}")
            return False
        except Exception as e:
            print(f"Error parsing course descriptions for {dept_code}: {e}")
            return False
    
    def parse_course_descriptions(self, soup, dept_code):
        """Parse course descriptions from catalog HTML"""
        courses = []
        
        # Multiple parsing strategies for different catalog formats
        
        # Strategy 1: Look for course blocks with specific HTML patterns
        course_blocks = soup.find_all(['div', 'section', 'article'], class_=lambda x: x and 'course' in x.lower())
        for block in course_blocks:
            course_info = self.extract_course_from_block(block, dept_code)
            if course_info:
                courses.append(course_info)
        
        # Strategy 2: Look for elements containing course codes in text
        if not courses:
            course_elements = soup.find_all(string=lambda text: text and f"{dept_code} " in text)
            
            for element in course_elements[:20]:  # Increased limit
                parent = element.parent
                while parent and parent.name != 'body':
                    text_content = parent.get_text(strip=True)
                    
                    if f"{dept_code} " in text_content and len(text_content) > 30:
                        course_info = self.extract_course_info(text_content, dept_code)
                        if course_info and not any(c.number == course_info.number for c in courses):
                            courses.append(course_info)
                            break
                    
                    parent = parent.parent
        
        # Strategy 3: Look for structured course listings
        if not courses:
            courses = self.parse_structured_courses(soup, dept_code)
        
        return courses[:10]  # Limit to 10 courses
    
    def extract_course_from_block(self, block, dept_code):
        """Extract course info from a structured course block"""
        text = block.get_text()
        return self.extract_course_info(text, dept_code)
    
    def parse_structured_courses(self, soup, dept_code):
        """Parse courses from structured HTML like tables or lists"""
        courses = []
        
        # Look for table rows or list items that might contain courses
        for tag_name in ['tr', 'li', 'dt', 'dd']:
            elements = soup.find_all(tag_name)
            for element in elements:
                text = element.get_text()
                if f"{dept_code} " in text:
                    course_info = self.extract_course_info(text, dept_code)
                    if course_info and not any(c.number == course_info.number for c in courses):
                        courses.append(course_info)
        
        return courses
    
    def extract_course_info(self, text, dept_code):
        """Extract course number, title, and description from text"""
        import re
        
        # Multiple patterns to handle different catalog formats
        patterns = [
            # Pattern 1: "DEPT ### - Course Title. Description..."
            rf'{dept_code}\s+(\d+[A-Z]*)\s*[-–]\s*([^.]+)\.\s*(.+)',
            # Pattern 2: "DEPT ###: Course Title Description..."
            rf'{dept_code}\s+(\d+[A-Z]*)\s*:\s*([^.]+?)\s+(.+)',
            # Pattern 3: "DEPT ### Course Title (credits) Description..."
            rf'{dept_code}\s+(\d+[A-Z]*)\s+([^(]+)\s*\([^)]*\)\s*(.+)',
            # Pattern 4: "DEPT ### Course Title Description..." (no separator)
            rf'{dept_code}\s+(\d+[A-Z]*)\s+([A-Z][^.]+?)\s+([a-z].+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                course_number = match.group(1)
                course_title = match.group(2).strip()
                course_description = match.group(3).strip()
                
                # Clean up title and description
                course_title = re.sub(r'\s+', ' ', course_title)
                course_description = re.sub(r'\s+', ' ', course_description)
                
                # Remove common suffixes and credit info
                course_description = re.sub(r'\(.*?credits?\)', '', course_description, flags=re.IGNORECASE)
                course_description = re.sub(r'Prerequisites?:.*', '', course_description, flags=re.IGNORECASE)
                course_description = course_description.strip()
                
                # Validate we have reasonable content
                if (len(course_title) > 5 and len(course_title) < 100 and 
                    len(course_description) > 15 and len(course_description) < 2000):
                    return Course(
                        number=course_number,
                        title=course_title,
                        description=course_description
                    )
        
        return None
    
    def save_department(self, dept, dept_code):
        """Save updated department data to JSON file"""
        dept_file = os.path.join(self.data_dir, 'departments', f"{dept_code}.json")
        
        with open(dept_file, 'w') as f:
            f.write(dept.to_json())
    
    def scrape_all_departments(self):
        """Scrape course descriptions for all departments"""
        departments = self.data_loader.get_all_departments()
        successful = 0
        
        print(f"Starting course description scraping for {len(departments)} departments...")
        
        for dept_code in departments:
            print(f"\n{'='*50}")
            if self.scrape_department_courses(dept_code):
                successful += 1
            
            # Be respectful with requests
            import time
            time.sleep(1)
        
        print(f"\n{'='*50}")
        print(f"Scraping complete! Successfully processed {successful}/{len(departments)} departments")

class CourseScheduleScraper:
    """Scraper for course schedule information from course listing"""
    
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.base_url = "https://apps.niagara.edu/courses/index.php"
    
    def scrape_semester_schedule(self, semester):
        """Scrape schedule data for a specific semester"""
        print(f"Scraping schedule for semester: {semester}")
        
        url = f"{self.base_url}?semester={semester.replace('_', '/')}&ug=1"
        print(f"Fetching from: {url}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            courses = self.parse_schedule_data(soup)
            
            if courses:
                self.save_schedule_data(semester, courses)
                print(f"Successfully scraped {len(courses)} course sections for {semester}")
                return True
            else:
                print(f"No course data found for {semester}")
                return False
                
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return False
        except Exception as e:
            print(f"Error parsing schedule for {semester}: {e}")
            return False
    
    def parse_schedule_data(self, soup):
        """Parse course schedule from HTML table"""
        courses_by_dept = {}
        
        # Look for table rows containing course data
        rows = soup.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 8:  # Expected number of columns
                course_data = self.extract_course_schedule(cells)
                if course_data:
                    dept_code = course_data['department']
                    if dept_code not in courses_by_dept:
                        courses_by_dept[dept_code] = []
                    courses_by_dept[dept_code].append(course_data)
        
        return courses_by_dept
    
    def extract_course_schedule(self, cells):
        """Extract course schedule information from table cells"""
        try:
            # Expected columns: Course, Name, Type, Days, Start, End, Designation, Avail, Credits
            if len(cells) < 8:
                return None
            
            course_code = cells[0].get_text(strip=True)
            course_name = cells[1].get_text(strip=True)
            delivery_type = cells[2].get_text(strip=True)
            days = cells[3].get_text(strip=True)
            start_time = cells[4].get_text(strip=True)
            end_time = cells[5].get_text(strip=True)
            designation = cells[6].get_text(strip=True)
            availability = cells[7].get_text(strip=True)
            credits = cells[8].get_text(strip=True) if len(cells) > 8 else "3.00"
            
            # Parse department and course number
            match = re.match(r'^([A-Z]+)(\d+[A-Z]*)$', course_code)
            if not match:
                return None
            
            department = match.group(1)
            
            # Skip if no schedule info
            if not days or not start_time or not end_time:
                return None
            
            return {
                'department': department,
                'number': course_code,
                'name': course_name,
                'credits': credits,
                'days': days,
                'start_time': start_time,
                'end_time': end_time,
                'delivery_type': delivery_type,
                'designation': designation,
                'availability': availability
            }
            
        except Exception as e:
            print(f"Error extracting course data: {e}")
            return None
    
    def save_schedule_data(self, semester, courses_by_dept):
        """Save schedule data to semester JSON files"""
        semester_dir = os.path.join(self.data_dir, 'semesters', semester)
        os.makedirs(semester_dir, exist_ok=True)
        
        for dept_code, courses in courses_by_dept.items():
            dept_file = os.path.join(semester_dir, f"{dept_code}.json")
            
            # Load existing data if it exists
            existing_data = []
            if os.path.exists(dept_file):
                try:
                    with open(dept_file, 'r') as f:
                        existing_data = json.load(f)
                except:
                    existing_data = []
            
            # Merge with new schedule data
            updated_courses = self.merge_course_data(existing_data, courses)
            
            # Save updated data
            with open(dept_file, 'w') as f:
                json.dump(updated_courses, f, indent=2)
    
    def merge_course_data(self, existing_courses, schedule_courses):
        """Merge existing course data with new schedule information"""
        # Create lookup for existing courses
        existing_lookup = {course.get('number', ''): course for course in existing_courses}
        
        merged = []
        
        # Add schedule courses with enhanced data
        for schedule_course in schedule_courses:
            course_number = schedule_course['number']
            
            # Start with schedule data
            merged_course = schedule_course.copy()
            
            # Enhance with existing data if available
            if course_number in existing_lookup:
                existing = existing_lookup[course_number]
                # Keep existing description and other data, but use schedule data for times
                if 'description' in existing:
                    merged_course['description'] = existing['description']
            
            merged.append(merged_course)
        
        # Add any existing courses not found in schedule
        for existing_course in existing_courses:
            existing_number = existing_course.get('number', '')
            if not any(sc['number'] == existing_number for sc in schedule_courses):
                merged.append(existing_course)
        
        return merged

def main():
    parser = argparse.ArgumentParser(description='Scrape course data from Niagara University')
    parser.add_argument('--department', '-d', 
                       help='Department code to scrape descriptions (e.g., THR). If not specified, scrapes all departments')
    parser.add_argument('--semester', '-s',
                       help='Semester to scrape schedules (e.g., 25_FA). Use with --schedules flag')
    parser.add_argument('--schedules', action='store_true',
                       help='Scrape course schedules instead of descriptions')
    parser.add_argument('--output-dir', '-o',
                       default='./data',
                       help='Directory containing data files (default: ./data)')
    
    args = parser.parse_args()
    
    if args.schedules:
        # Use schedule scraper
        schedule_scraper = CourseScheduleScraper(args.output_dir)
        
        if args.semester:
            schedule_scraper.scrape_semester_schedule(args.semester)
        else:
            # Scrape all available semesters
            semesters_dir = os.path.join(args.output_dir, 'semesters')
            if os.path.exists(semesters_dir):
                successful = 0
                total = 0
                for semester_folder in os.listdir(semesters_dir):
                    if os.path.isdir(os.path.join(semesters_dir, semester_folder)):
                        total += 1
                        if schedule_scraper.scrape_semester_schedule(semester_folder):
                            successful += 1
                print(f"\nSchedule scraping complete! Successfully processed {successful}/{total} semesters")
    else:
        # Use existing description scraper
        scraper = CourseDescriptionScraper(args.output_dir)
        
        if args.department:
            scraper.scrape_department_courses(args.department.upper())
        else:
            scraper.scrape_all_departments()

if __name__ == '__main__':
    main()
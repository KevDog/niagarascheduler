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
import sys

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def list_departments(data_dir):
    """List all available departments"""
    data_loader = DepartmentDataLoader(data_dir)
    departments = data_loader.get_all_departments()
    
    print(f"Available departments ({len(departments)}):")
    print("=" * 40)
    
    dept_info = []
    for dept_code in sorted(departments):
        dept = data_loader.load_department(dept_code)
        if dept:
            dept_info.append((dept_code, dept.name))
        else:
            dept_info.append((dept_code, "Unknown"))
    
    # Format output in columns
    for code, name in dept_info:
        print(f"  {code:<6} - {name}")

def list_semesters(data_dir):
    """List all available semesters"""
    semesters_dir = os.path.join(data_dir, 'semesters')
    
    if not os.path.exists(semesters_dir):
        print("No semester data found.")
        return
    
    semesters = []
    for folder in os.listdir(semesters_dir):
        if os.path.isdir(os.path.join(semesters_dir, folder)):
            # Convert folder name like "25_FA" to readable format
            if '_' in folder:
                year_part, season_part = folder.split('_', 1)
                season_map = {
                    'FA': 'Fall', 'SP': 'Spring', 'SU': 'Summer', 'WI': 'Winter'
                }
                full_season = season_map.get(season_part, season_part)
                full_year = f"20{year_part}" if len(year_part) == 2 else year_part
                display = f"{full_season} {full_year}"
            else:
                display = folder
            semesters.append((folder, display))
    
    semesters.sort(key=lambda x: x[0])
    
    print(f"Available semesters ({len(semesters)}):")
    print("=" * 40)
    for folder, display in semesters:
        print(f"  {folder:<8} - {display}")

def show_stats(data_dir):
    """Show statistics about current data"""
    data_loader = DepartmentDataLoader(data_dir)
    departments = data_loader.get_all_departments()
    
    print("Course Data Statistics")
    print("=" * 40)
    
    # Department statistics
    total_courses = 0
    with_descriptions = 0
    dept_count = 0
    
    for dept_code in departments:
        dept = data_loader.load_department(dept_code)
        if dept:
            dept_count += 1
            dept_courses = len(dept.courses)
            total_courses += dept_courses
            
            courses_with_desc = sum(1 for course in dept.courses if course.description)
            with_descriptions += courses_with_desc
    
    print(f"Departments: {dept_count}")
    print(f"Total Courses: {total_courses}")
    print(f"With Descriptions: {with_descriptions} ({(with_descriptions/total_courses*100):.1f}%)" if total_courses > 0 else "With Descriptions: 0")
    
    # Semester statistics
    semesters_dir = os.path.join(data_dir, 'semesters')
    if os.path.exists(semesters_dir):
        semester_folders = [f for f in os.listdir(semesters_dir) 
                          if os.path.isdir(os.path.join(semesters_dir, f))]
        print(f"Semester Data: {len(semester_folders)} semesters")
        
        # Count offerings per semester
        for semester in sorted(semester_folders):
            semester_dir = os.path.join(semesters_dir, semester)
            dept_files = [f for f in os.listdir(semester_dir) if f.endswith('.json')]
            
            total_offerings = 0
            with_schedules = 0
            
            for dept_file in dept_files:
                try:
                    with open(os.path.join(semester_dir, dept_file), 'r') as f:
                        offerings = json.load(f)
                    
                    total_offerings += len(offerings)
                    with_schedules += sum(1 for offering in offerings 
                                        if isinstance(offering, dict) and 'days' in offering and offering.get('days'))
                except:
                    continue
            
            print(f"  {semester}: {total_offerings} offerings, {with_schedules} with schedules")
    else:
        print("Semester Data: Not available")

def show_quickstart():
    """Show quick start guide"""
    print("""
🚀 Niagara University Course Scraper - Quick Start Guide

COMMON TASKS:

1. Get help and see what's available:
   python scrape_descriptions.py --help            # Full help
   python scrape_descriptions.py --list-departments # See all departments
   python scrape_descriptions.py --list-semesters   # See all semesters
   python scrape_descriptions.py --stats            # Data statistics

2. Update course descriptions:
   python scrape_descriptions.py                    # All departments
   python scrape_descriptions.py -d THR             # Just Theater Arts
   python scrape_descriptions.py -d ACC             # Just Accounting

3. Update schedule data:
   python scrape_descriptions.py --schedules        # All semesters
   python scrape_descriptions.py --schedules -s 25_FA # Just Fall 2025

4. Check results:
   python scrape_descriptions.py --stats            # See updated statistics

DATA SOURCES:
• Course Descriptions: https://catalog.niagara.edu/undergraduate/courses-az/[dept]/
• Course Schedules: https://apps.niagara.edu/courses/index.php?semester=[sem]&ug=1

OUTPUT LOCATIONS:
• Course Descriptions: ./data/departments/[DEPT].json
• Schedule Data: ./data/semesters/[SEM]/[DEPT].json

TIPS:
• Run descriptions first, then schedules to get complete data
• Use --stats to monitor progress and data completeness
• Schedule scraping requires active semester to be available online
• Process is respectful with 1-second delays between requests

Need more help? Run: python scrape_descriptions.py --help
    """)

def main():
    parser = argparse.ArgumentParser(
        description='Niagara University Course Data Scraper - Extract course descriptions and schedules',
        epilog='''
Examples:
  # Scrape all course descriptions from catalog
  %(prog)s

  # Scrape specific department descriptions
  %(prog)s --department THR
  %(prog)s -d ACC

  # Scrape all semester schedules
  %(prog)s --schedules

  # Scrape specific semester schedule
  %(prog)s --schedules --semester 25_FA
  %(prog)s -s 25_SU --schedules

  # Use custom data directory
  %(prog)s --output-dir /path/to/data

Data Sources:
  - Course Descriptions: https://catalog.niagara.edu/undergraduate/courses-az/[dept]/
  - Course Schedules: https://apps.niagara.edu/courses/index.php?semester=[sem]&ug=1

Output:
  - Descriptions: ./data/departments/[DEPT].json
  - Schedules: ./data/semesters/[SEM]/[DEPT].json
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Main operation mode
    parser.add_argument('--schedules', action='store_true',
                       help='Scrape course schedules with meeting times instead of descriptions')
    
    # Filtering options
    parser.add_argument('--department', '-d', metavar='DEPT',
                       help='Department code to scrape (e.g., THR, ACC, ENG). If not specified, scrapes all departments')
    parser.add_argument('--semester', '-s', metavar='SEM', 
                       help='Semester to scrape schedules (e.g., 25_FA, 25_SP, 25_SU). Required with --schedules for single semester')
    
    # Configuration
    parser.add_argument('--output-dir', '-o', metavar='DIR',
                       default='./data',
                       help='Directory containing data files (default: ./data)')
    
    # Information options
    parser.add_argument('--list-departments', action='store_true',
                       help='List all available departments and exit')
    parser.add_argument('--list-semesters', action='store_true', 
                       help='List all available semesters and exit')
    parser.add_argument('--stats', action='store_true',
                       help='Show statistics about current data and exit')
    parser.add_argument('--version', action='version', version='%(prog)s 2.0.0',
                       help='Show version information and exit')
    parser.add_argument('--quickstart', action='store_true',
                       help='Show quick start guide and exit')
    
    args = parser.parse_args()
    
    # Handle information requests first
    if args.list_departments:
        list_departments(args.output_dir)
        return
    
    if args.list_semesters:
        list_semesters(args.output_dir)
        return
    
    if args.stats:
        show_stats(args.output_dir)
        return
    
    if args.quickstart:
        show_quickstart()
        return
    
    # Validation for schedules mode
    if args.schedules and not args.semester:
        # Check if we have semester directories to scrape all
        semesters_dir = os.path.join(args.output_dir, 'semesters')
        if not os.path.exists(semesters_dir) or not os.listdir(semesters_dir):
            print("Error: No semester directories found. Use --semester to specify a semester or --list-semesters to see available options.")
            parser.print_help()
            return
    
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
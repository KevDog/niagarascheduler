#!/usr/bin/env python

"""
Map program overviews to department mission statements
"""

import json
import os
import re

def load_program_overviews():
    """Load program overviews from JSON file"""
    with open('program_overviews.json', 'r') as f:
        return json.load(f)

def create_program_to_department_mapping():
    """Create mapping between program names and department codes"""
    mapping = {
        # Accounting programs
        'Accounting': 'ACC',
        '3+1 Accounting Program': 'ACC',
        'Master of Science in Accounting': 'ACC',
        
        # Business programs
        'Finance': 'FIN',
        'Management': 'MGT',
        'Marketing': 'MKG',
        'Master of Business Administration': 'BUS',
        'Marketing Food and Consumer Packaged Goods': 'MKG',
        'Supply Chain Management': 'BUS',
        'Food Industry Management': 'MHR',
        
        # Biology/Science programs
        'Biology and Biotechnology': 'BIO',
        'Chemistry and Biochemistry': 'CHE',
        'Environmental Science': 'ENV',
        'Mathematics': 'MAT',
        'Actuarial Science': 'MAT',
        'Pre-Health Professions': 'BIO',
        
        # Computer Science
        'Computer and Information Sciences': 'CIS',
        'M.S. Information Security and Digital Forensics Online (ISDF)': 'CIS',
        
        # Education programs
        'Adolescence Education (Grades 7-12)': 'EDU',
        'Childhood and Middle Childhood Education': 'EDU',
        'Early Childhood and Childhood Education': 'EDU',
        'Middle Childhood and Adolescence Education': 'EDU',
        'Special Education': 'EDU',
        'Master of Science in Elementary and Secondary Education Online': 'EDU',
        'Master of Science in Special Education Online': 'EDU',
        'Master of Science in Literacy and English Language Learners Online': 'EDU',
        'Master of Science in Theatre Education Online': 'THR',
        'Teaching English to Speakers of Other Languages': 'ESL',
        
        # Liberal Arts programs
        'English': 'ENG',
        'History': 'HIS',
        'Philosophy': 'PHI',
        'Political Science': 'POL',
        'Psychology': 'PSY',
        'Sociology': 'SOC',
        'Religious Studies': 'REL',
        'French': 'FRE',
        'Spanish': 'SPA',
        'Modern and Classical Languages': 'FRE',  # Could also be SPA, LAT, etc.
        
        # Communication and Media
        'Communication and Media Studies': 'CMS',
        'Social Media, Digital Marketing, and Artificial Intelligence': 'CMS',
        
        # Criminal Justice
        'Criminology and Criminal Justice': 'CRJ',
        'M.S. Criminal Justice Administration': 'CRJ',
        
        # Nursing
        'Nursing': 'NUR',
        'ASDBS Nursing': 'NUR',
        'Nursing RPN to BS': 'NUR',
        'RN to BS Completion Program': 'NUR',
        'Family Nurse Practitioner': 'NUR',
        'Master of Science in Nursing Education': 'NUR',
        
        # Theatre
        'Theatre Studies and Fine Arts': 'THR',
        
        # Economics
        'Economics': 'ECO',
        
        # Fine Arts
        'Art History with Museum Studies': 'FAA',
        
        # Hotel/Tourism Management
        'Hotel and Restaurant Management': 'MHR',
        'Tourism and Event Management': 'TRM',
        'Sport and Recreation Management': 'SPM',
        'Master of Science in Sports Management': 'SPM',
        
        # Social Work
        'Social Work': 'SWK',
        
        # Gerontology
        'Gerontology': 'GRN',
        
        # International Studies
        'International Studies': 'INT',
        
        # Liberal Arts
        'Liberal Arts': 'LAM',
        'General Studies': 'LAM',
        
        # Pre-professional
        'Pre-Law': 'POL',  # Often housed in political science
        
        # Psychology/Counseling
        'Clinical Mental Health Counseling': 'PSY',
        'Master of Science in School Psychology': 'PSY',
        
        # Minor programs - map to related departments
        'American Sign Language and Deaf Studies (Minor)': 'ASL',
        'Africana/Black Studies (Minor)': 'SOC',  # Often in sociology
        'Film Studies (Minor)': 'CMS',  # Often in communication
        'Women\'s Studies (Minor)': 'SOC',  # Often in sociology
    }
    
    return mapping

def update_department_mission_statements():
    """Update department JSON files with mission statements from program overviews"""
    program_overviews = load_program_overviews()
    mapping = create_program_to_department_mapping()
    
    departments_dir = 'data/departments'
    updated_count = 0
    
    for program_name, program_data in program_overviews.items():
        if program_name in mapping:
            dept_code = mapping[program_name]
            dept_file = os.path.join(departments_dir, f"{dept_code}.json")
            
            if os.path.exists(dept_file):
                # Read department data
                with open(dept_file, 'r') as f:
                    dept_data = json.load(f)
                
                # Update mission statement if it's currently null/empty
                if not dept_data.get('mission_statement'):
                    dept_data['mission_statement'] = program_data['overview']
                    
                    # Write updated data
                    with open(dept_file, 'w') as f:
                        json.dump(dept_data, f, indent=4)
                    
                    print(f"Updated {dept_code} with mission statement from '{program_name}'")
                    updated_count += 1
                else:
                    print(f"Skipped {dept_code} - mission statement already exists")
            else:
                print(f"Department file not found: {dept_file}")
        else:
            print(f"No mapping found for program: {program_name}")
    
    print(f"\nUpdated {updated_count} department mission statements")

def main():
    if not os.path.exists('program_overviews.json'):
        print("program_overviews.json not found. Run scrape_program_overviews.py first.")
        return
    
    update_department_mission_statements()

if __name__ == '__main__':
    main()
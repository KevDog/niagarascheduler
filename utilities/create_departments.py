#!/usr/bin/env python

"""
Create department JSON files for all departments from Niagara University catalog
"""

import os
import json

# Department data extracted from catalog.niagara.edu/undergraduate/courses-az/
departments = [
    ("Accounting", "ACC"),
    ("American Sign Language", "ASL"),
    ("Arabic", "ARA"),
    ("Biology", "BIO"),
    ("Business", "BUS"),
    ("Chemistry", "CHE"),
    ("Chinese", "CHI"),
    ("Communication and Media Studies", "CMS"),
    ("Computer Information Sciences", "CIS"),
    ("Criminology & Criminal Justice", "CRJ"),
    ("Critical Literacy", "CRL"),
    ("Dance", "DAN"),
    ("Earth Science", "ESC"),
    ("Economics", "ECO"),
    ("Education", "EDU"),
    ("English", "ENG"),
    ("English As a Foreign Language", "ESL"),
    ("English As a Second Language", "ESLC"),
    ("Environmental Studies", "ENV"),
    ("Finance", "FIN"),
    ("Fine Arts", "FAA"),
    ("French", "FRE"),
    ("Geography", "GEO"),
    ("Gerontology", "GRN"),
    ("Greek", "GRK"),
    ("History", "HIS"),
    ("Hotel Restaurant Management", "MHR"),
    ("Hotel/Sport/Tourism", "HST"),
    ("International Studies", "INT"),
    ("Italian", "ITA"),
    ("Japanese", "JPN"),
    ("Latin", "LAT"),
    ("Latin American Studies", "LAS"),
    ("Learning Skills", "LSK"),
    ("Liberal Arts", "LAM"),
    ("Management", "MGT"),
    ("Marketing", "MKG"),
    ("Mathematics", "MAT"),
    ("Military Science", "MIL"),
    ("Nursing", "NUR"),
    ("Philosophy", "PHI"),
    ("Physics", "PHY"),
    ("Political Science", "POL"),
    ("Psychology", "PSY"),
    ("Religious Studies", "REL"),
    ("Social Work", "SWK"),
    ("Sociology", "SOC"),
    ("Spanish", "SPA"),
    ("Speech", "SPK"),
    ("Sport Management", "SPM"),
    ("Statistics", "STA"),
    ("Study Abroad", "STY"),
    ("Theatre Studies", "THR"),
    ("Tourism/Recreation Management", "TRM")
]

def create_department_json(name, code, output_dir):
    """Create basic department JSON file"""
    department_data = {
        "name": name,
        "mission_statement": None,
        "office": None,
        "course_listing_url": None,
        "courses": []
    }
    
    file_path = os.path.join(output_dir, f"{code}.json")
    
    # Don't overwrite existing files
    if os.path.exists(file_path):
        print(f"Skipping {code}.json - file already exists")
        return False
    
    with open(file_path, 'w') as f:
        json.dump(department_data, f, indent=4)
    
    print(f"Created {file_path}")
    return True

def main():
    output_dir = "data/departments"
    os.makedirs(output_dir, exist_ok=True)
    
    created_count = 0
    skipped_count = 0
    
    for name, code in departments:
        if create_department_json(name, code, output_dir):
            created_count += 1
        else:
            skipped_count += 1
    
    print(f"\nSummary:")
    print(f"Created: {created_count} department files")
    print(f"Skipped: {skipped_count} existing files")
    print(f"Total departments: {len(departments)}")

if __name__ == '__main__':
    main()
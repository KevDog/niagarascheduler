#!/usr/bin/env python

"""
Update department JSON files with course_descriptions_url field
"""

import os
import json

# Base URL for course descriptions
BASE_URL = "https://catalog.niagara.edu"

# Department codes to URL paths mapping
department_urls = {
    "ACC": "/undergraduate/courses-az/acc/",
    "ASL": "/undergraduate/courses-az/asl/",
    "ARA": "/undergraduate/courses-az/ara/",
    "BIO": "/undergraduate/courses-az/bio/",
    "BUS": "/undergraduate/courses-az/bus/",
    "CHE": "/undergraduate/courses-az/che/",
    "CHI": "/undergraduate/courses-az/chi/",
    "CMS": "/undergraduate/courses-az/cms/",
    "CIS": "/undergraduate/courses-az/cis/",
    "CRJ": "/undergraduate/courses-az/crj/",
    "CRL": "/undergraduate/courses-az/crl/",
    "DAN": "/undergraduate/courses-az/dan/",
    "ESC": "/undergraduate/courses-az/esc/",
    "ECO": "/undergraduate/courses-az/eco/",
    "EDU": "/undergraduate/courses-az/edu/",
    "ENG": "/undergraduate/courses-az/eng/",
    "ESL": "/undergraduate/courses-az/esl/",
    "ESLC": "/undergraduate/courses-az/eslc/",
    "ENV": "/undergraduate/courses-az/env/",
    "FIN": "/undergraduate/courses-az/fin/",
    "FAA": "/undergraduate/courses-az/faa/",
    "FRE": "/undergraduate/courses-az/fre/",
    "GEO": "/undergraduate/courses-az/geo/",
    "GRN": "/undergraduate/courses-az/grn/",
    "GRK": "/undergraduate/courses-az/grk/",
    "HIS": "/undergraduate/courses-az/his/",
    "MHR": "/undergraduate/courses-az/mhr/",
    "HST": "/undergraduate/courses-az/hst/",
    "INT": "/undergraduate/courses-az/int/",
    "ITA": "/undergraduate/courses-az/ita/",
    "JPN": "/undergraduate/courses-az/jpn/",
    "LAT": "/undergraduate/courses-az/lat/",
    "LAS": "/undergraduate/courses-az/las/",
    "LSK": "/undergraduate/courses-az/lsk/",
    "LAM": "/undergraduate/courses-az/lam/",
    "MGT": "/undergraduate/courses-az/mgt/",
    "MKG": "/undergraduate/courses-az/mkg/",
    "MAT": "/undergraduate/courses-az/mat/",
    "MIL": "/undergraduate/courses-az/mil/",
    "NUR": "/undergraduate/courses-az/nur/",
    "PHI": "/undergraduate/courses-az/phi/",
    "PHY": "/undergraduate/courses-az/phy/",
    "POL": "/undergraduate/courses-az/pol/",
    "PSY": "/undergraduate/courses-az/psy/",
    "REL": "/undergraduate/courses-az/rel/",
    "SWK": "/undergraduate/courses-az/swk/",
    "SOC": "/undergraduate/courses-az/soc/",
    "SPA": "/undergraduate/courses-az/spa/",
    "SPK": "/undergraduate/courses-az/spk/",
    "SPM": "/undergraduate/courses-az/spm/",
    "STA": "/undergraduate/courses-az/sta/",
    "STY": "/undergraduate/courses-az/sty/",
    "THR": "/undergraduate/courses-az/thr/",
    "TRM": "/undergraduate/courses-az/trm/"
}

def update_department_json(code, output_dir):
    """Add course_descriptions_url field to department JSON"""
    file_path = os.path.join(output_dir, f"{code}.json")
    
    if not os.path.exists(file_path):
        print(f"Skipping {code}.json - file does not exist")
        return False
    
    # Read existing data
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Add course_descriptions_url field
    if code in department_urls:
        data["course_descriptions_url"] = BASE_URL + department_urls[code]
        
        # Write updated data
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"Updated {file_path} with URL: {data['course_descriptions_url']}")
        return True
    else:
        print(f"No URL found for department {code}")
        return False

def main():
    output_dir = "data/departments"
    
    if not os.path.exists(output_dir):
        print(f"Directory {output_dir} does not exist")
        return
    
    updated_count = 0
    skipped_count = 0
    
    for code in department_urls.keys():
        if update_department_json(code, output_dir):
            updated_count += 1
        else:
            skipped_count += 1
    
    print(f"\nSummary:")
    print(f"Updated: {updated_count} department files")
    print(f"Skipped: {skipped_count} files")
    print(f"Total departments: {len(department_urls)}")

if __name__ == '__main__':
    main()
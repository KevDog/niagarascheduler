#!/usr/bin/env python

"""
Scrape program overviews from Niagara University programs pages
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os

def get_program_links(base_url):
    """Scrape all program links from the programs page"""
    response = requests.get(base_url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    program_links = []
    
    # Find all program links - adjust selector based on page structure
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/programs/' in href and href.endswith('/'):
            # Convert relative URLs to absolute
            if href.startswith('/'):
                full_url = 'https://www.niagara.edu' + href
            else:
                full_url = href
                
            program_name = link.get_text().strip()
            if program_name:
                program_links.append({
                    'name': program_name,
                    'url': full_url
                })
    
    # Remove duplicates
    seen_urls = set()
    unique_programs = []
    for program in program_links:
        if program['url'] not in seen_urls:
            seen_urls.add(program['url'])
            unique_programs.append(program)
    
    return unique_programs

def extract_program_overview(program_url):
    """Extract Program Overview content from a program page"""
    try:
        response = requests.get(program_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find H2 tag with "Program Overview"
        overview_heading = soup.find('h2', string='Program Overview')
        if not overview_heading:
            # Try case-insensitive search
            overview_heading = soup.find('h2', string=lambda text: text and 'program overview' in text.lower())
        
        if not overview_heading:
            return None
        
        # Extract text following the heading
        overview_text = []
        current_element = overview_heading.find_next_sibling()
        
        while current_element:
            # Stop at next heading
            if current_element.name and current_element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                break
                
            # Extract text from paragraphs
            if current_element.name == 'p':
                text = current_element.get_text().strip()
                # Skip paragraphs starting with "Credits"
                if text and not text.lower().startswith('credits'):
                    overview_text.append(text)
            
            current_element = current_element.find_next_sibling()
        
        return '\n\n'.join(overview_text) if overview_text else None
        
    except requests.RequestException as e:
        print(f"Error fetching {program_url}: {e}")
        return None

def main():
    base_url = "https://www.niagara.edu/programs/"
    output_file = "data/program_overviews.json"
    
    print("Fetching program links...")
    programs = get_program_links(base_url)
    print(f"Found {len(programs)} programs")
    
    program_overviews = {}
    
    for i, program in enumerate(programs):
        print(f"Processing {i+1}/{len(programs)}: {program['name']}")
        
        overview = extract_program_overview(program['url'])
        if overview:
            program_overviews[program['name']] = {
                'url': program['url'],
                'overview': overview
            }
            print(f"  ✓ Found overview")
        else:
            print(f"  - No overview found")
        
        # Be respectful with requests
        time.sleep(0.5)
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(program_overviews, f, indent=2)
    
    print(f"\nComplete! Found overviews for {len(program_overviews)} programs")
    print(f"Results saved to {output_file}")

if __name__ == '__main__':
    main()
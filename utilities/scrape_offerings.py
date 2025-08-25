#!/usr/bin/env python

"""
CLI tool for scraping course offerings from Niagara University
"""

import argparse
from utilities.course_scraper import CourseScraperCLI


def parse_args(args=None):
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Scrape course offerings from Niagara University')
    
    parser.add_argument('--semester', required=True, help='Semester code (e.g., 25/FA)')
    parser.add_argument('--ug', action='store_true', help='Include undergraduate courses')
    parser.add_argument('--grad', action='store_true', help='Include graduate courses')
    parser.add_argument('--output-dir', default='/data', help='Directory to save JSON files (default: /data)')
    
    if args is None:
        return parser.parse_args()
    else:
        return parser.parse_args(args)


def main(args=None):
    """Main CLI function"""
    parsed_args = parse_args(args)
    
    scraper = CourseScraperCLI()
    scraper.scrape_courses(
        semester=parsed_args.semester,
        ug=parsed_args.ug,
        grad=parsed_args.grad,
        output_dir=parsed_args.output_dir
    )


if __name__ == '__main__':
    main()
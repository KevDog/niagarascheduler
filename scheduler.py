#!/usr/bin/env python

"""
Niagara University Scheduler - Main Module

This module provides the public API for the refactored scheduler system.
It imports and exposes all the necessary functions from the modular components.
"""

# Core functionality
from core.utils import locale, regex, date_formats, range_of_days, clean_cell, parse_td_for_dates
from core.calendar_loader import make_url, fetch_registrar_table, parse_registrar_table, load_semester_calendar_from_json, load_calendar_from_json
from core.schedule_generator import sorted_classes, schedule, discover_available_semesters
from core.output_formatter import markdown, output

# PDF processing
from pdf.pdf_extractor import extract_text_from_pdf, extract_first_day_from_pdf_text, extract_last_day_from_pdf_text, extract_no_class_dates_from_pdf_text, parse_pdf_calendar
from pdf.date_parser import extract_date_range_from_text, parse_single_date_from_text, parse_date_range_from_text
from pdf.semester_parser import extract_semester_dates_from_pdf_text, parse_pdf_calendar_for_semester
from pdf.event_parser import classify_event_type, extract_semester_events_from_pdf_text

# JSON processing
from calendar_json.json_converter import parse_pdf_to_json, parse_pdf_to_json_with_events
from calendar_json.calendar_manager import discover_available_years, generate_active_semester_config, generate_calendar_json

# Public API - expose most commonly used functions
__all__ = [
    # Core API
    'make_url', 'fetch_registrar_table', 'parse_registrar_table', 
    'sorted_classes', 'schedule', 'output', 'date_formats',
    'discover_available_semesters', 'locale',
    
    # Calendar management
    'generate_calendar_json', 'parse_pdf_to_json',
    
    # PDF processing (for advanced use)
    'parse_pdf_calendar', 'parse_pdf_calendar_for_semester',
    
    # JSON utilities
    'load_semester_calendar_from_json', 'load_calendar_from_json'
]
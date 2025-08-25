#!/usr/bin/env python

"""
CLI script to generate JSON calendar files from PDFs.
Run this before deployment to convert PDFs to JSON format.

Usage:
    python generate_calendars.py
    python generate_calendars.py --input-dir ./custom_pdfs --output-dir ./custom_calendars
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scheduler import generate_calendar_json

def check_tbd_items(output_dir):
    """Check generated JSON files for TBD items and report them"""
    tbd_items = []
    
    if not os.path.exists(output_dir):
        return tbd_items
    
    import json
    json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    
    for json_file in json_files:
        json_path = os.path.join(output_dir, json_file)
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            file_tbds = []
            
            # Check for parsing errors
            if 'error' in data:
                file_tbds.append({
                    'field': 'parsing_error',
                    'location': 'root',
                    'suggestion': f'Fix PDF parsing error: {data["error"]}'
                })
            
            # Check each semester
            for semester_key, semester_data in data.get('semesters', {}).items():
                if semester_data.get('first_day') == 'TBD':
                    file_tbds.append({
                        'field': 'first_day',
                        'location': semester_key,
                        'suggestion': 'Set first day of classes in YYYY-MM-DD format'
                    })
                
                if semester_data.get('last_day') == 'TBD':
                    file_tbds.append({
                        'field': 'last_day', 
                        'location': semester_key,
                        'suggestion': 'Set last day of classes in YYYY-MM-DD format'
                    })
                
                # Check events for TBD dates
                for event in semester_data.get('events', []):
                    if event.get('date') == 'TBD':
                        file_tbds.append({
                            'field': 'event_date',
                            'location': f"{semester_key}/events",
                            'suggestion': f'Set date for event "{event.get("name", "Unknown")}"'
                        })
                    
                    if event.get('date_range') and 'TBD' in str(event.get('date_range')):
                        file_tbds.append({
                            'field': 'event_date_range',
                            'location': f"{semester_key}/events", 
                            'suggestion': f'Set date range for event "{event.get("name", "Unknown")}"'
                        })
            
            if file_tbds:
                tbd_items.append({
                    'file': json_file,
                    'items': file_tbds
                })
                
        except Exception as e:
            tbd_items.append({
                'file': json_file,
                'items': [{
                    'field': 'file_error',
                    'location': 'file',
                    'suggestion': f'Fix JSON file error: {e}'
                }]
            })
    
    return tbd_items

def write_tbd_report(tbd_items, output_dir, preservation_notes=None):
    """Write TBD items and preservation notes to a report file"""
    report_path = os.path.join(output_dir, 'TBD_ITEMS.txt')
    
    with open(report_path, 'w') as f:
        f.write("TBD ITEMS REQUIRING MANUAL REVIEW\n")
        f.write("="*50 + "\n\n")
        import datetime
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Write preservation notes first
        if preservation_notes:
            f.write("🔒 PRESERVED MANUAL EDITS\n")
            f.write("-" * 25 + "\n\n")
            f.write("The following manual edits were preserved from existing JSON files:\n\n")
            
            for note in preservation_notes:
                f.write(f"📁 FILE: {note['file']}\n")
                f.write("-" * (len(note['file']) + 8) + "\n")
                f.write(f"  ✅ {note['message']}\n")
                if note['preserved_fields']:
                    f.write(f"     📋 Preserved fields: {', '.join(note['preserved_fields'])}\n")
                f.write("\n")
            
            f.write("Note: These values will NOT be overwritten by future runs.\n")
            f.write("To update them, edit the JSON files manually or delete them to allow re-parsing.\n\n")
            f.write("="*50 + "\n\n")
        
        # Write TBD items
        if not tbd_items:
            f.write("✅ No TBD items found! All calendar data was parsed successfully.\n")
        else:
            f.write(f"Found TBD items in {len(tbd_items)} file(s):\n\n")
            
            for file_info in tbd_items:
                f.write(f"📁 FILE: {file_info['file']}\n")
                f.write("-" * (len(file_info['file']) + 8) + "\n")
                
                for item in file_info['items']:
                    f.write(f"  ❌ {item['field']} in {item['location']}\n")
                    f.write(f"     💡 {item['suggestion']}\n\n")
                
                f.write("\n")
        
        f.write("\nTo fix TBD items:\n")
        f.write("1. Edit the JSON files directly, or\n")
        f.write("2. Improve the PDF parsing logic in niagarascheduler.py, or\n")
        f.write("3. Provide cleaner PDF source files\n\n")
        f.write("Re-run generate_calendars.py after making changes.\n")
    
    return report_path

def main():
    import datetime
    
    parser = argparse.ArgumentParser(description='Generate JSON calendar files from PDFs')
    parser.add_argument('--input-dir', 
                       help='Directory containing PDF files (default: ./niagara)',
                       default=None)
    parser.add_argument('--output-dir',
                       help='Directory to output JSON files (default: ./calendars)', 
                       default=None)
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Verbose output')
    parser.add_argument('--no-tbd-report',
                       action='store_true', 
                       help='Skip TBD item reporting')
    
    args = parser.parse_args()
    
    output_dir = args.output_dir or os.path.join(os.path.dirname(__file__), 'calendars')
    
    if args.verbose:
        print("Generating JSON calendar files...")
        print(f"Input directory: {args.input_dir or 'default (./niagara)'}")
        print(f"Output directory: {output_dir}")
        print()
    
    try:
        from scheduler import generate_calendar_json
        generate_calendar_json(args.input_dir, args.output_dir)
        
        # Get preservation notes if any
        preservation_notes = getattr(generate_calendar_json, '_preservation_notes', [])
        
        if args.verbose:
            # List generated files
            if os.path.exists(output_dir):
                json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
                print(f"\nGenerated {len(json_files)} JSON files:")
                for json_file in sorted(json_files):
                    print(f"  - {json_file}")
        
        # Check for TBD items
        if not args.no_tbd_report:
            print("\nChecking for TBD items...")
            tbd_items = check_tbd_items(output_dir)
            
            # Write report file including preservation notes
            report_path = write_tbd_report(tbd_items, output_dir, preservation_notes)
            
            # Print summary to terminal
            if not tbd_items and not preservation_notes:
                print("✅ No TBD items found! All calendar data was parsed successfully.")
            else:
                if tbd_items:
                    print(f"⚠️  Found TBD items in {len(tbd_items)} file(s):")
                    
                    for file_info in tbd_items:
                        print(f"\n📁 {file_info['file']}:")
                        for item in file_info['items']:
                            print(f"  ❌ {item['field']} in {item['location']}")
                            print(f"     💡 {item['suggestion']}")
                
                if preservation_notes:
                    print(f"\n🔒 Preserved manual edits in {len(preservation_notes)} file(s):")
                    for note in preservation_notes:
                        print(f"\n📁 {note['file']}:")
                        print(f"  ✅ {note['message']}")
                        if note['preserved_fields']:
                            print(f"     📋 Fields: {', '.join(note['preserved_fields'])}")
                
                print(f"\n📝 Detailed report written to: {report_path}")
                print("\nTo fix TBD items:")
                print("1. Edit the JSON files directly, or")
                print("2. Improve the PDF parsing logic in niagarascheduler.py, or") 
                print("3. Provide cleaner PDF source files")
        
        print("\nJSON generation complete!")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
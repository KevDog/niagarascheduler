# Niagara University Scheduler

A comprehensive Flask web application for generating course syllabi for Niagara University. Features a rich course data system, markdown-first template architecture, and automated class scheduling based on official academic calendar data.

## Features

- **Rich Course Database**: Object-oriented course management with department-specific JSON storage
- **Markdown-First Templates**: Professional syllabus generation with multiple export formats
- **Preview-Then-Export UX**: See formatted preview before downloading in chosen format
- **Calendar Integration**: Automated parsing of Niagara University academic calendar PDFs
- **Multiple Output Formats**: Export to DOCX, HTML, LaTeX, PDF, and Markdown
- **Course Metadata Support**: Instructors, textbooks, zoom links, meeting days, and more
- **Department Organization**: Structured data storage by academic department

## Quick Start

### Running the Application

```bash
# Start the web server
python app.py

# Or specify a custom port
python app.py --port 3000

# Generate calendars and start server
python app.py --generate
```

### Calendar Management

```bash
# Generate JSON calendar files from PDFs
python generate_calendars.py

# Check for missing data
cat calendars/TBD_ITEMS.txt
```

Visit `http://localhost:5001` to use the web interface.

## Usage

### Web Interface

1. **Course Information**: Enter course ID (e.g., "THR 101") for automatic data lookup
2. **Select Semester**: Choose from available semesters (Fall/Spring + Year)  
3. **Choose Meeting Days**: Select which days your course meets
4. **Configure Options**: Enable course descriptions, holidays, breaks, and events
5. **Preview**: Review formatted syllabus with rich course metadata
6. **Export**: Download in preferred format (DOCX, PDF, HTML, LaTeX, Markdown)

### Course Data Management

The system uses a rich object model for course data:

- **Course Properties**: number, title, description, instructors, textbooks, zoom_link, meeting_days
- **Department Properties**: name, mission_statement, office, course_listing_url, courses
- **Storage Format**: Department-specific JSON files (e.g., `data/THR.json`, `data/MATH.json`)

## Project Structure

```
├── app.py                      # Flask web application with preview/export workflow
├── scheduler.py               # Main API module for schedule generation
├── generate_calendars.py      # Calendar generation utility
├── core/                      # Core application modules
│   ├── course.py             # Course class with full serialization
│   ├── department.py         # Department class with course collection
│   ├── data_loader.py        # Load Course/Department objects from JSON
│   ├── data_migration.py     # Migrate legacy course data
│   ├── markdown_processor.py # Markdown generation with rich Course objects
│   ├── utils.py             # Basic utilities & constants
│   ├── calendar_loader.py   # Calendar data loading
│   ├── schedule_generator.py # Core scheduling logic
│   └── output_formatter.py  # Template generation
├── pdf/                       # PDF processing modules
│   ├── pdf_extractor.py     # PDF text extraction
│   ├── date_parser.py       # Date parsing utilities
│   ├── semester_parser.py   # Semester-specific parsing
│   └── event_parser.py      # Event extraction
├── calendar_json/             # JSON processing modules
│   ├── json_converter.py    # PDF to JSON conversion
│   └── calendar_manager.py  # Calendar file management
├── data/                      # Course data storage
│   ├── THR.json            # Theater Arts department courses
│   └── MATH.json           # Mathematics department courses
├── tests/                     # Comprehensive test suite using TDD
│   ├── test_course.py       # Course class tests
│   ├── test_department.py   # Department class tests
│   ├── test_data_loader.py  # Data loading tests
│   └── test_data_migration.py # Migration tests
├── niagara/                   # Academic calendar PDFs
├── calendars/                 # Generated JSON calendar data
└── templates/                 # Syllabus templates
    └── syllabus_master.md    # Core markdown template
```

## Calendar Data

The system converts PDF academic calendars to structured JSON format:

- **PDF Source**: Place academic calendar PDFs in `niagara/` directory
- **JSON Output**: Generated semester-specific files in `calendars/`
- **Manual Editing**: JSON files can be manually edited for corrections

### Adding New Academic Years

1. Place new academic calendar PDF in `niagara/` directory
2. Run `python generate_calendars.py` to generate JSON
3. Edit JSON files to fix any "TBD" values
4. Update `calendars/active_semester.json` if needed

## Development

### Modular Architecture

The codebase is organized into focused modules for maintainability:

- **`core/`**: Core scheduling logic and utilities (~50-120 LOC each)
- **`pdf/`**: PDF processing and date extraction (~70-145 LOC each)  
- **`calendar_json/`**: JSON conversion and calendar management (~85-100 LOC each)
- **`scheduler.py`**: Public API exposing main functions

### Dependencies

- Flask
- Arrow (date handling)
- PyPandoc (template conversion)
- PDFplumber (PDF parsing)
- BeautifulSoup4

### Running with Debug Mode

```bash
python app.py  # Debug mode enabled by default
```

### Testing

The project uses Test-Driven Development (TDD) with comprehensive test coverage:

```bash
# Run all tests
python -m tests.test_course
python -m tests.test_department  
python -m tests.test_data_loader
python -m tests.test_data_migration

# Run specific test modules
python -m tests.test_course
```

### Architecture Highlights

- **Object-Oriented Design**: Rich Course and Department classes with full metadata
- **Markdown-First Generation**: Professional templates with Pandoc conversion
- **Department-Specific Storage**: Organized JSON files by academic department
- **TDD Implementation**: Complete test coverage using "Arrange, Act, Assert" pattern
- **Data Migration Tools**: Utilities for converting legacy course data

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

<https://www.gnu.org/licenses/>.

## Credits

Based on original work by W. Caleb McDaniel (2015-2019)  
Modified for Niagara University by Kevin Stevens
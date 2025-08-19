# Niagara University Scheduler

A Flask web application that automatically generates class meeting schedules for Niagara University courses using official academic calendar data. Creates syllabi with properly formatted class dates, accounting for university holidays and breaks.

## Features

- **Web Interface**: Simple form-based interface for generating schedules
- **Calendar Integration**: Uses Niagara University academic calendar PDFs
- **Multiple Output Formats**: Plain text, DOCX, HTML, and LaTeX templates
- **Flexible Scheduling**: Supports any combination of weekdays
- **Holiday Awareness**: Automatically excludes university holidays and breaks

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

1. **Select Semester**: Choose from available semesters (Fall/Spring + Year)
2. **Choose Meeting Days**: Select which days your course meets
3. **Pick Format**: Choose output format and date style
4. **Generate**: Get class schedule or download syllabus template

## Project Structure

```
├── app.py                    # Flask web application
├── scheduler.py             # Main API module
├── generate_calendars.py    # Calendar generation utility
├── core/                    # Core scheduling components
│   ├── utils.py            # Basic utilities & constants
│   ├── calendar_loader.py  # Calendar data loading
│   ├── schedule_generator.py # Core scheduling logic
│   └── output_formatter.py # Template generation
├── pdf/                     # PDF processing modules
│   ├── pdf_extractor.py    # PDF text extraction
│   ├── date_parser.py      # Date parsing utilities
│   ├── semester_parser.py  # Semester-specific parsing
│   └── event_parser.py     # Event extraction
├── calendar_json/           # JSON processing modules
│   ├── json_converter.py   # PDF to JSON conversion
│   └── calendar_manager.py # Calendar file management
├── niagara/                 # Academic calendar PDFs
├── calendars/               # Generated JSON calendar data
└── templates/               # Syllabus templates (DOCX, HTML, LaTeX, MD)
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

```bash
# Run test suite
python -m pytest test_*.py
```

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

<https://www.gnu.org/licenses/>.

## Credits

Based on original work by W. Caleb McDaniel (2015-2019)  
Modified for Niagara University by Kevin Stevens
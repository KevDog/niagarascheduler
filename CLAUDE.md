The context of this project is to repurpose the project to create syllabi for Niagara University. Academic calendars in .xslx format can be found in the ./niagara folder

Be terse and don't overexplain

TEST-DRIVEN DEVELOPMENT PROCESS:
1. Create test file with empty test functions (just function names)
2. Implement one test method at a time, in order
3. Use "Arrange, Act, Assert" pattern in test methods wherever practical
4. Write minimal code to make current test pass
5. Move to next test method
6. Refactor when all tests pass
7. Run git add . after each passing test
8. When asked a question, answer it before suggesting changes.
Propose functionality in the following format:

All tests going in the ./tests folder

Function: <what functionality is being added to the code>
Affected Files:
Test(s):

run curl commands without asking to proceed

The course listing matrix below has department name, three-letter abbreviation, and course listing URL
Course listing matrix
Department,Abbreviation,URL    
Theater Arts, THR, https://catalog.niagara.edu/undergraduate/programs-az/arts-sciences/theatre-studies-fine-arts/#coursestext

Proposed features:
Course Description Lookup: Given a course I.D., e.g. "THR 101", the system looks up the department URL from the course listing matrix, downloads the appropriate description, and adds it to the syllabus text.

"NU_Syllabus_Template.docx" is the template

# DESIGN NOTES & PROJECT STATUS

## Current Implementation Status (Dec 2025) ✅ COMPLETE
- **Web Application**: Fully functional Flask app with markdown-first architecture
- **Syllabus Generation**: Complete preview system with export to DOCX, HTML, LaTeX, PDF, and Markdown
- **Calendar Integration**: JSON-based calendar parsing from PDF academic calendars
- **Rich Course Data System**: Complete object-oriented course management with department-specific JSON files

## Key Architecture Decisions
1. **Markdown-First Approach**: All syllabus generation starts with markdown template, converts to other formats via pandoc
2. **Preview-Then-Export UX**: Users see formatted preview before downloading in chosen format
3. **JSON Calendar Storage**: Academic calendars converted from PDF to JSON for programmatic access
4. **Object-Oriented Course Model**: Full Course and Department classes with rich metadata
5. **Department-Specific Storage**: One JSON file per department (THR.json, MATH.json, etc.)

## File Structure
- `templates/syllabus_master.md` - Core markdown template for all syllabi
- `core/markdown_processor.py` - Markdown generation and format conversion with rich Course objects
- `core/course.py` - Course class with full serialization (to_dict/from_dict)
- `core/department.py` - Department class with course collection and JSON export
- `core/data_loader.py` - Load Course/Department objects from JSON files
- `core/data_migration.py` - Migrate legacy course data to new structure
- `app.py` - Flask web application with preview/export workflow
- `calendars/*.json` - Academic calendar data parsed from PDFs
- `data/THR.json`, `data/MATH.json` - Department-specific course databases
- `tests/` - Comprehensive test suite using TDD approach

## Course Object Model ✅ IMPLEMENTED
**Course Properties**: number, title, description, instructors[], textbooks[], zoom_link, meeting_days[]
**Department Properties**: name, mission_statement, office, course_listing_url, courses[]

## Data Flow Architecture ✅ IMPLEMENTED
1. **JSON Storage**: Department files (THR.json) → DepartmentDataLoader
2. **Object Creation**: JSON data → Course/Department objects via from_dict()
3. **Syllabus Generation**: Rich Course objects → Enhanced markdown templates
4. **Export Options**: Markdown → Pandoc → DOCX/HTML/LaTeX/PDF

## Next Development Phase: CLI Tool for Course Scraping
**Purpose**: Administrative tool for course description management
**Goal**: Scrape course descriptions from catalog URLs and populate department JSON files

### Planned CLI Features
1. **Course Description Scraper**: Parse department catalog pages for course descriptions
2. **Department JSON Builder**: Create/update THR.json, MATH.json files with scraped data
3. **Validation Tools**: Verify course data integrity and completeness
4. **Bulk Operations**: Process multiple departments/courses in batch

### Course Listing Matrix (Partial)
Department,Abbreviation,URL    
Theater Arts, THR, https://catalog.niagara.edu/undergraduate/programs-az/arts-sciences/theatre-studies-fine-arts/#coursestext

### CLI Implementation Notes
- Use TDD approach: tests first, then implementation
- Consider using requests/BeautifulSoup for web scraping
- **JSON File Structure**: ✅ IMPLEMENTED - One JSON file per department using abbreviation naming
- JSON structure: ✅ IMPLEMENTED - Matches Course/Department object model
- Include error handling for network failures and parsing errors
- Course lookup: ✅ IMPLEMENTED - DepartmentDataLoader searches across department files
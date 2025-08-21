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

## Current Implementation Status (Aug 2025)
- **Web Application**: Fully functional Flask app with markdown-first architecture
- **Syllabus Generation**: Complete preview system with export to DOCX, HTML, LaTeX, PDF, and Markdown
- **Calendar Integration**: JSON-based calendar parsing from PDF academic calendars
- **Course Descriptions**: Basic JSON-based lookup system (limited dataset)

## Key Architecture Decisions
1. **Markdown-First Approach**: All syllabus generation starts with markdown template, converts to other formats via pandoc
2. **Preview-Then-Export UX**: Users see formatted preview before downloading in chosen format
3. **JSON Calendar Storage**: Academic calendars converted from PDF to JSON for programmatic access
4. **Template-Based Generation**: Single master template with placeholder replacement

## File Structure
- `templates/syllabus_master.md` - Core markdown template for all syllabi
- `core/markdown_processor.py` - Markdown generation and format conversion
- `app.py` - Flask web application with preview/export workflow
- `calendars/*.json` - Academic calendar data parsed from PDFs
- `data/courses.json` - Course description lookup data

## Next Development Phase: CLI Tool
**Purpose**: Administrative tool for course description management
**Goal**: Scrape course descriptions from catalog URLs and populate JSON database

### Planned CLI Features
1. **Course Description Scraper**: Parse department catalog pages for course descriptions
2. **JSON Database Builder**: Update `data/courses.json` with scraped descriptions  
3. **Validation Tools**: Verify course data integrity and completeness
4. **Bulk Operations**: Process multiple departments/courses in batch

### Course Listing Matrix (Partial)
Department,Abbreviation,URL    
Theater Arts, THR, https://catalog.niagara.edu/undergraduate/programs-az/arts-sciences/theatre-studies-fine-arts/#coursestext

### CLI Implementation Notes
- Use TDD approach: tests first, then implementation
- Consider using requests/BeautifulSoup for web scraping
- **JSON File Structure**: One JSON file per department using abbreviation naming (e.g., THR.json, ENG.json)
- JSON structure should match existing `data/courses.json` format
- Include error handling for network failures and parsing errors
- Update course description lookup to search across department-specific JSON files
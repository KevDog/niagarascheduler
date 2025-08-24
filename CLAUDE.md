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
9. Describe functionality before proposing code. I.e., what is the workflow?
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

## Current Implementation Status (Aug 2025) ✅ COMPLETE
- **Web Application**: Fully functional Flask app with markdown-first architecture
- **Syllabus Generation**: Complete preview system with export to DOCX, HTML, LaTeX, PDF, and Markdown
- **Calendar Integration**: JSON-based calendar parsing from PDF academic calendars
- **Rich Course Data System**: Complete object-oriented course management with department-specific JSON files
- **Course Offerings Scraper**: CLI tool for scraping semester course offerings from Niagara course portal
- **Department Data System**: Complete department structure with mission statements and course description URLs
- **Program Overview Integration**: Mission statements populated from program overview pages

## Key Architecture Decisions
1. **Markdown-First Approach**: All syllabus generation starts with markdown template, converts to other formats via pandoc
2. **Preview-Then-Export UX**: Users see formatted preview before downloading in chosen format
3. **JSON Calendar Storage**: Academic calendars converted from PDF to JSON for programmatic access
4. **Object-Oriented Course Model**: Full Course and Department classes with rich metadata
5. **Data Organization**: Static department data (departments/) separate from dynamic semester data (semesters/)
6. **Mission Statement Auto-Population**: Department mission statements automatically included in syllabi

## File Structure
- `templates/syllabus_master.md` - Core markdown template with mission statement integration
- `core/markdown_processor.py` - Enhanced markdown generation with department mission statement loading
- `core/course.py` - Course class with full serialization and offerings support
- `core/department.py` - Department class with mission statements and URL management
- `core/data_loader.py` - Load Course/Department objects with backward compatibility
- `app.py` - Flask web application with preview/export workflow
- `calendars/*.json` - Academic calendar data parsed from PDFs
- `data/departments/` - Static department JSON files with mission statements and URLs
- `data/semesters/` - Dynamic semester offering data by term
- `scrape_offerings.py` - CLI tool for scraping course offerings by semester
- `tests/` - Comprehensive test suite using TDD approach

## Course Object Model ✅ IMPLEMENTED
**Course Properties**: number, title, description, instructors[], textbooks[], zoom_link, meeting_days[], offerings[]
**Department Properties**: name, mission_statement, office, course_listing_url, course_descriptions_url, courses[]
**Offering Properties**: code, delivery_type, designation, credits, meeting_days[], department, number, section

## Data Flow Architecture ✅ IMPLEMENTED
1. **Static Data**: Department files (departments/THR.json) → Mission statements and course description URLs
2. **Dynamic Data**: Semester files (semesters/25_FA/THR.json) → Course offerings and scheduling
3. **Object Creation**: JSON data → Course/Department/Offering objects via from_dict()
4. **Syllabus Generation**: Rich objects → Enhanced markdown templates with mission statements
5. **Export Options**: Markdown → Pandoc → DOCX/HTML/LaTeX/PDF

## CLI Tools ✅ IMPLEMENTED
1. **Course Offerings Scraper** (`scrape_offerings.py`): 
   - Command: `python scrape_offerings.py --semester 25/FA --ug --output-dir ./data`
   - Scrapes semester course offerings from apps.niagara.edu
   - Creates Department→Course→Offerings structure in semesters/ folder
2. **Department Creator** (`create_departments.py`):
   - Creates JSON files for all 54 departments from catalog
3. **URL Updater** (`update_departments_urls.py`):
   - Adds course_descriptions_url to department files
4. **Program Overview Mapper** (`map_program_overviews.py`):
   - Maps program overviews to department mission statements

## Department Data System ✅ IMPLEMENTED
- **54 Departments**: All departments from catalog.niagara.edu/undergraduate/courses-az/
- **Mission Statements**: Populated from program overview pages at www.niagara.edu/programs/
- **Course Description URLs**: Direct links to catalog pages for each department
- **Organized Structure**: Static department info separated from dynamic semester offerings

## TODO: Next Development Phase
### UI/UX Enhancements
1. **TailwindCSS Integration**: Add modern styling framework to Flask app
2. **Editable Syllabus Preview**: Allow in-browser editing before download
3. **Syllabus Creation Wizard**: Multi-step form for guided syllabus building
4. **Enhanced User Experience**: Modern, responsive interface

### Data Enhancement
1. **Course Description Scraper**: CLI tool to populate course descriptions from catalog URLs
   - Command: `python scrape_descriptions.py --department THR --output-dir ./data/departments`
   - Parse course descriptions from course_descriptions_url in department files
   - Update Course objects with detailed descriptions
2. **Bulk Department Processing**: Process all departments for course descriptions
3. **Data Validation Tools**: Verify course data integrity and completeness

### Planned Workflow
1. **Wizard Interface**: Step-by-step syllabus creation
2. **Live Preview**: Real-time markdown rendering with TailwindCSS styling
3. **In-Browser Editing**: Rich text editor for final adjustments
4. **Export Options**: Download in multiple formats after editing

### Technical Resources
- **TailwindCSS Documentation**: https://tailwindcss.com/docs/
- **Integration Method**: CDN or npm installation for Flask templates
- **Responsive Design**: Mobile-first approach with Tailwind utility classes
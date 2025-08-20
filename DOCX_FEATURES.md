# Enhanced DOCX Editing Capabilities

The Niagara University Scheduler now includes enhanced DOCX editing capabilities using the `python-docx` library.

## Features Added

### 1. Direct DOCX Manipulation
- **Template Variable Replacement**: Replace placeholders like `{{SEMESTER}}`, `{{YEAR}}`, etc.
- **Dynamic Content Insertion**: Add schedule tables, course information, and formatted content
- **Header/Footer Customization**: Modify document headers and footers
- **Table Creation**: Generate formatted schedule tables with proper styling

### 2. Enhanced Template System
- **Custom Template Creation**: Generate syllabus templates with placeholders
- **Smart Template Detection**: Automatically use enhanced editing when available
- **Fallback Support**: Falls back to PyPandoc if python-docx is not available

### 3. Schedule Integration
- **Formatted Schedule Tables**: Convert schedule data into formatted tables
- **Event Handling**: Properly display events, holidays, and no-class dates
- **Date Formatting**: Support for multiple date formats in templates

## Usage

### Command Line Tools

```bash
# Check DOCX editing capabilities
python docx_tools.py check

# Create a custom syllabus template
python docx_tools.py create-template --output "my_template.docx"

# Enhance an existing template with schedule data
python docx_tools.py enhance --template "template.docx" --output "syllabus.docx" --semester "Fall" --year "2025"
```

### Web Interface
The enhanced DOCX features are automatically integrated into the web interface. When generating a DOCX syllabus:

1. The system first tries to use enhanced DOCX editing if available
2. Falls back to PyPandoc method if enhanced editing fails
3. Uses the Niagara University template (`NU 2025 Syllabus Template.docx`) when available

### Programmatic API

```python
from core.docx_editor import enhance_syllabus_docx, create_custom_syllabus_template

# Create a custom template
success, template = create_custom_syllabus_template()
if success:
    template.save("custom_template.docx")

# Enhance an existing template
schedule_data = ["Monday, Sept 7", "Wednesday, Sept 9", "Friday, Sept 11"]
success = enhance_syllabus_docx(
    template_path="template.docx",
    schedule_data=schedule_data,
    output_path="enhanced_syllabus.docx",
    semester="Fall",
    year="2025"
)
```

## Template Placeholders

The system supports these template placeholders:

- `{{SEMESTER}}` - Semester name (e.g., "Fall")
- `{{YEAR}}` - Academic year (e.g., "2025")  
- `{{SEMESTER_YEAR}}` - Combined (e.g., "Fall 2025")
- `{{COURSE_TITLE}}` - Course title
- `{{INSTRUCTOR_NAME}}` - Instructor name
- `{{INSTRUCTOR_EMAIL}}` - Instructor email
- `{{OFFICE_HOURS}}` - Office hours
- `{{SCHEDULE}}` - Class schedule (replaced with formatted table)
- `{{OBJECTIVES}}` - Course objectives
- `{{MATERIALS}}` - Required materials
- `{{GRADING_POLICY}}` - Grading policy
- `{{ATTENDANCE_POLICY}}` - Attendance policy

## Installation

The enhanced DOCX features require the `python-docx` library:

```bash
pip install python-docx==0.8.11
```

This dependency is included in `requirements.txt` and will be installed automatically.

## Testing

Comprehensive tests are available for DOCX functionality:

```bash
# Run all DOCX tests
python run_tests.py docx

# Run all core tests (includes DOCX)
python run_tests.py core
```

## Benefits

1. **Richer Formatting**: Direct control over document structure, tables, and styling
2. **Better Template Control**: More precise placeholder replacement and content insertion
3. **Professional Output**: Formatted tables and properly structured syllabi
4. **Flexibility**: Both programmatic API and web interface support
5. **Backward Compatibility**: Graceful fallback to existing PyPandoc system

## Files Added/Modified

- `core/docx_editor.py` - Main DOCX editing functionality
- `core/output_formatter.py` - Enhanced to use DOCX editing
- `docx_tools.py` - Command-line utilities
- `tests/core/test_docx_editor.py` - Comprehensive test coverage
- `requirements.txt` - Added python-docx dependency
- `templates/Enhanced_Syllabus_Template.docx` - Custom template with placeholders

The enhanced DOCX capabilities provide a modern, flexible approach to document generation while maintaining compatibility with existing workflows.
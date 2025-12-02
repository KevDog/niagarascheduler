The context of this project is to repurpose the project to create syllabi for Niagara University. Academic calendars in .xslx format can be found in the ./niagara folder


## TESTING FRAMEWORK STANDARDS ✅

### **Consistent Test Frameworks by Layer**
- **Python/API Tests**: `unittest` (Python standard library)
- **Frontend Tests**: `Vitest` + `Vue Test Utils` + `jsdom`
- **Pinia Store Tests**: `Vitest` + `Pinia` test utilities
- **Component Tests**: `Vitest` + `Vue Test Utils` + component mounting
- **Integration Tests**: `Vitest` for frontend, `unittest` for Python

### **Test Organization Structure**
```
tests/
├── api/                    # Python API tests (unittest)
├── models/                 # Python model tests (unittest)  
├── core/                   # Python core logic tests (unittest)
└── frontend/               # Frontend tests (Vitest)
    ├── src/test/stores/    # Pinia store tests
    ├── src/test/views/     # Vue component tests
    └── src/test/setup.ts   # Test configuration
```

## TEST-DRIVEN DEVELOPMENT PROCESS:
1. Create test file with empty test functions (just function names)
2. Implement one test method at a time, in order
3. **MANDATORY**: Use "Arrange, Act, Assert" pattern in ALL test methods
4. Write minimal code to make current test pass
5. Move to next test method
6. Refactor when all tests pass
7. Run git add . after each passing test
8. When asked a question, answer it before suggesting changes.
9. Describe functionality before proposing code. I.e., what is the workflow?

### **Arrange/Act/Assert Pattern Requirements**
**All tests MUST follow this structure:**
```python
def test_example_functionality(self):
    """Test description"""
    # Arrange - Set up test data and conditions
    input_data = "test_input"
    expected_result = "expected_output"
    
    # Act - Execute the function/method being tested
    actual_result = function_under_test(input_data)
    
    # Assert - Verify the results
    self.assertEqual(actual_result, expected_result)
```

```typescript
it('should test example functionality', () => {
  // Arrange - Set up test data and conditions
  const inputData = 'test_input'
  const expectedResult = 'expected_output'
  
  // Act - Execute the function/method being tested
  const actualResult = functionUnderTest(inputData)
  
  // Assert - Verify the results
  expect(actualResult).toBe(expectedResult)
})
```

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
- `api.py` - Flask JSON API server for Vue frontend
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
   - Command: `python utilities/scrape_offerings.py --semester 25/FA --ug --output-dir ./data`
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

## Vue Frontend Architecture ✅ IMPLEMENTED

### Component-Based Development Standards
**All Vue functionality must be implemented as reusable components following these patterns:**

#### **Component Structure** 📁
```
src/
├── components/
│   ├── ui/                          # Reusable UI components
│   │   ├── CustomListbox.vue        # HeadlessUI Listbox wrapper
│   │   ├── FormField.vue           # Standard form input wrapper
│   │   └── LoadingSpinner.vue       # Loading states
│   ├── CourseSelectionForm.vue      # Main form logic
│   ├── ProgressIndicator.vue        # Wizard progress bar
│   └── [FeatureName]Component.vue   # Feature-specific components
├── composables/
│   ├── useApiData.ts               # API data fetching
│   ├── useCourseSelection.ts       # Form state management
│   ├── useNavigation.ts            # Router utilities
│   └── use[FeatureName].ts         # Feature-specific logic
└── views/
    └── [Page]View.vue              # Page orchestration only (~50 lines max)
```

#### **Development Rules** 🔧
1. **No Logic in Views**: Views should only orchestrate components (≤50 lines)
2. **Single Responsibility**: Each component has one clear purpose
3. **Composable First**: Extract reusable logic to composables
4. **TypeScript Required**: All components must have proper type definitions
5. **Emit Events**: Use events for parent-child communication
6. **Props Interface**: Define clear prop interfaces with defaults

#### **Modularization Benefits** ✅
- **HomeView.vue**: Reduced from 498 lines to 36 lines (93% reduction)
- **Reusable Components**: ProgressIndicator, CourseSelectionForm
- **Shared Logic**: useApiData, useCourseSelection, useNavigation composables
- **Type Safety**: Better TypeScript support with focused interfaces
- **Maintainability**: Easier testing, debugging, and feature additions

## Current Status: Production Ready ✅ (August 2025)

### Recently Completed Features
1. **Complete 6-Step Wizard**: Full workflow from course selection to syllabus preview
2. **Syllabus Preview & Export**: Working preview with DOCX, PDF, HTML downloads 
3. **Schedule Integration**: Academic calendar with class date generation
4. **Data Persistence**: Pinia store with localStorage for session management
5. **Markdown Rendering**: Proper formatting with front matter removal
6. **Error Handling**: Function declaration fixes and proper navigation flow
7. **UI Polish**: Correct step indicators (1-6) and progress tracking

### System Architecture ✅
- **Frontend**: Vue 3 + TypeScript + TailwindCSS + Pinia
- **Backend**: Flask with modular blueprints and comprehensive API
- **Data Layer**: JSON-based course/schedule data with object models
- **Export System**: Pandoc-based multi-format generation
- **Testing**: TDD approach with comprehensive coverage

### Future Enhancements (Optional)
1. **Template System**: Save/load syllabus templates for reuse
2. **Advanced Editing**: In-browser rich text editing capabilities
3. **Batch Operations**: Generate multiple syllabi simultaneously
4. **Analytics**: Usage tracking and popular course insights

## Testing Strategy for Schedule Notes Feature ✅ IMPLEMENTED

### **Test Framework & Scope**
- **Framework**: Vitest + Vue Test Utils
- **Scope**: Both unit tests (Pinia store) and integration tests (Vue components)
- **Mock Strategy**: Mock localStorage and API calls as needed
- **Test Location**: `/tests/frontend/` directory

### **Character Limits & Unicode Support**
- **Character Limit**: 750 characters maximum per note
- **Unicode Support**: Full Unicode support (mathematical symbols, international characters)
- **Validation**: Client-side character count validation with visual feedback
- **Error Handling**: Graceful handling of character limit exceeded

### **Test Coverage Requirements**

#### **1. Pinia Store Tests (`useScheduleStore`)**
```typescript
// Core functionality
- openNotesModal(date) → sets selectedDate, loads existing note to tempNote, shows modal
- saveNote(semester, dept, course) → saves note to dateNotes, persists to localStorage, closes modal
- closeNotesModal() → clears temporary state, hides modal
- hasNoteForDate(date) → returns boolean based on note existence
- getNoteForDate(date) → retrieves note text for given date

// Persistence
- loadNotesFromStorage(semester, dept, course) → loads notes from localStorage
- saveNotesToStorage(semester, dept, course) → persists with correct storage key
- Storage key format: `schedule-notes-{semester}-{department}-{course}`

// Character limits
- Character validation (750 max)
- Unicode character handling
- Truncation behavior
```

#### **2. Component Integration Tests (ScheduleSetupView)**
```typescript
// User interactions
- Click schedule item → opens notes modal
- Modal displays correct date in header
- Textarea pre-populates with existing note content
- Save button → persists note and updates UI indicator
- Cancel button → discards changes and closes modal

// Visual feedback
- Notes indicator (📝 Notes badge) appears when note exists
- Character count display (e.g., "245/750 characters")
- Character limit warning/error states
- Empty notes removal from storage
```

#### **3. Edge Cases & Error Handling**
```typescript
// Data validation
- Very long notes (750+ characters)
- Special characters (mathematical symbols: ∑, ∫, π, ∞)
- International characters (Chinese: 汉字, Arabic: العربية, etc.)
- Empty/whitespace-only notes

// Storage scenarios
- Invalid JSON in localStorage
- Storage quota exceeded
- Course-specific note isolation
- Cross-session persistence

// User experience
- Modal auto-focus on textarea
- Keyboard navigation (ESC to close)
- Click outside modal behavior
```

#### **4. Mock Data Structure**
```typescript
// Test course data
const mockWizardData = {
  semester: '25_FA',
  department: 'THR', 
  course: '101',
  instructor: 'Test Professor'
}

// Test calendar data
const mockScheduleItems = [
  { date: '2025-08-26', type: 'class' },
  { date: '2025-09-01', type: 'holiday', name: 'Labor Day' },
  { date: '2025-08-28', type: 'class' }
]

// Test notes
const mockNotes = {
  '2025-08-26': 'Assignment 1 due - Mathematical proofs (∑, ∫)',
  '2025-08-28': 'Quiz on Chapter 1 中文测试'
}
```

### **Implementation Priority**
1. **Character Limit Implementation**: Add 750-character validation to store and UI
2. **Unit Tests**: Test Pinia store functionality with Unicode edge cases  
3. **Integration Tests**: Test full user workflow with mock data
4. **Edge Case Coverage**: Comprehensive error handling and validation tests
- Document structure is in place. The text under "Student Learning Outcomes", "Assessment", "Requirements of Course and Workload Information" is informational for the instructor and can be in a help popover. The "Vincentian Excellence" and "Sexual Harassment" sections are required.
# Niagara University Scheduler

A modern Vue 3 + Flask application for generating course syllabi for Niagara University. Features a comprehensive course selection wizard, live schedule integration, and automated syllabus generation with multiple export formats.

## Current Architecture (August 2025) ✨

- **Vue 3 Frontend**: Modern SPA with TypeScript, Pinia state management, and TailwindCSS
- **Flask JSON API**: CORS-enabled backend serving course and schedule data
- **Live Schedule Integration**: Real-time course offering data with meeting times
- **Comprehensive Data Pipeline**: Automated course description and schedule scraping
- **Rich Course Selection**: Multi-step wizard with semester, department, course, and section selection

## Features

- **🎯 Smart Course Selection Wizard**: Semester → Instructor → Department → Course → Section
- **📅 Live Schedule Data**: Real meeting times and days (e.g., "Section A - MW 10:30AM-11:50AM")
- **📚 Rich Course Database**: 52/55 departments populated with course descriptions
- **🔄 Automated Data Scraping**: CLI tools for course descriptions and schedule updates
- **📄 Multiple Export Formats**: DOCX, PDF, HTML, LaTeX, and Markdown
- **🎨 Modern UI**: TailwindCSS with responsive design and intuitive workflow
- **⚡ Fast Development**: Hot reload, TypeScript support, and modern tooling

## Quick Start

### Development Setup

```bash
# Backend API (Terminal 1)
python api.py --port 8000

# Frontend Dev Server (Terminal 2)
cd frontend && npm run dev

# Access the application
# Frontend: http://localhost:5173
# API: http://localhost:8000
```

### Production Deployment

```bash
# Build frontend
cd frontend && npm run build

# Start production servers
python api.py --port 8000  # API server
# Serve frontend build files with web server (nginx, apache, etc.)
```

## API Documentation

### Core Endpoints

#### Configuration
```http
GET /api/config
```
Returns available semesters and system configuration.

**Response:**
```json
{
  "semesters": [
    {
      "key": "25_FA",
      "semester": "Fall", 
      "year": "2025",
      "display": "Fall 2025"
    }
  ],
  "date_formats": [...],
  "months": [...],
  "days": [...]
}
```

#### Departments
```http
GET /api/departments
```
Returns list of all academic departments.

**Response:**
```json
{
  "departments": [
    {
      "code": "THR",
      "name": "Theater Arts",
      "mission_statement": "Excellence in theatrical arts..."
    }
  ]
}
```

#### Department Courses
```http
GET /api/departments/{dept_code}
```
Returns detailed course information for a department.

**Response:**
```json
{
  "code": "THR",
  "name": "Theater Arts",
  "courses": [
    {
      "number": "101",
      "title": "Introduction to Theater",
      "description": "An introductory course covering..."
    }
  ]
}
```

#### Course Offerings (with Schedule)
```http
GET /api/offerings/{semester}/{dept_code}/{course_number}
```
Returns section offerings with meeting times for a specific course.

**Parameters:**
- `semester`: e.g., "25_FA" 
- `dept_code`: e.g., "THR"
- `course_number`: e.g., "103"

**Response:**
```json
{
  "offerings": [
    {
      "number": "THR103A",
      "name": "Intro to Theatre", 
      "section": "A",
      "credits": "3.00",
      "days": "TTH",
      "start_time": "12:00PM",
      "end_time": "01:20PM",
      "delivery_type": "LEC",
      "availability": "27"
    }
  ]
}
```

#### Health Check
```http
GET /api/health
```
Returns API status and version information.

## CLI Tools

### Course Description Scraper
```bash
# Scrape all department course descriptions
python utilities/scrape_descriptions.py

# Scrape specific department
python utilities/scrape_descriptions.py --department THR
```

### Schedule Data Scraper
```bash
# Scrape all semester schedules
python utilities/scrape_descriptions.py --schedules

# Scrape specific semester
python utilities/scrape_descriptions.py --schedules --semester 25_FA
```

The scraper pulls live data from: https://apps.niagara.edu/courses/index.php?semester=25/FA&ug=1

## Project Structure

```
├── frontend/                   # Vue 3 + TypeScript + TailwindCSS frontend
│   ├── src/
│   │   ├── views/HomeView.vue # Main syllabus wizard component
│   │   ├── types/api.ts       # TypeScript API interfaces
│   │   └── stores/            # Pinia state management
│   ├── package.json           # Vue project dependencies
│   └── vite.config.ts         # Vite configuration with API proxy
├── api.py                     # Flask JSON API server
├── utilities/                 # CLI tools and utilities
│   ├── scrape_descriptions.py # Course data scraping tool
│   ├── scrape_offerings.py    # Schedule scraping tool
│   └── ...
├── core/                      # Core application modules
│   ├── course.py             # Course class with serialization
│   ├── department.py         # Department class with course collection  
│   ├── data_loader.py        # JSON data loading utilities
│   └── markdown_processor.py # Syllabus generation
├── data/
│   ├── departments/          # Course description data by department
│   │   ├── THR.json         # Theater Arts courses with descriptions
│   │   └── ACC.json         # Accounting courses with descriptions
│   └── semesters/           # Schedule data by semester
│       ├── 25_FA/           # Fall 2025 schedule data
│       │   ├── THR.json    # Theater section schedules
│       │   └── ACC.json    # Accounting section schedules
│       └── 25_SU/          # Summer 2025 schedule data
├── tests/                    # Comprehensive test suite
│   ├── test_api.py          # API endpoint tests
│   ├── test_schedule_scraper.py # Schedule scraper tests
│   ├── test_course.py       # Course model tests
│   └── test_department.py   # Department model tests
└── templates/               # Syllabus templates
    ├── syllabus_master.md   # Core markdown template
    └── NU 2025 Syllabus Template.docx  # DOCX template
```

## Data Architecture

### Separation of Concerns
- **`/data/departments/`**: Static course descriptions and department info
- **`/data/semesters/`**: Dynamic schedule data with meeting times
- **Vue Frontend**: User interface and workflow management
- **Flask API**: Data serving and business logic

### Course Selection Flow
1. **Semester Selection**: User chooses from available semesters
2. **Instructor Input**: Enter instructor name
3. **Department Selection**: Choose from alphabetically sorted departments
4. **Course Selection**: Pick from department-specific courses with descriptions
5. **Section Selection**: Choose specific meeting times (e.g., "A - TTH 12:00PM-01:20PM")

## Development

### Vue Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

### API Development
```bash
# Start API server with auto-reload
python api.py --port 8000

# Run tests
python -m unittest discover tests -v

# Test specific functionality
python -m unittest tests.test_api tests.test_schedule_scraper -v
```

### Testing

The project uses comprehensive test coverage with Python unittest:

```bash
# Run all tests
python -m unittest discover tests -v

# Core functionality tests (32+ tests)
python -m unittest tests.test_course tests.test_department tests.test_data_loader tests.test_api tests.test_schedule_scraper -v
```

**Test Coverage:**
- ✅ Course and Department object models
- ✅ JSON serialization/deserialization
- ✅ API endpoints with mock data
- ✅ Schedule scraper with HTML parsing
- ✅ CLI integration testing
- ✅ Data loading and validation

## Current Status & Todos

### ✅ Completed Features
- [x] Vue 3 + Vite project with TypeScript and TailwindCSS
- [x] Flask JSON API with CORS support  
- [x] Complete syllabus wizard with 5-step form
- [x] Course description scraper (52/55 departments populated)
- [x] Schedule scraper with live meeting times
- [x] API endpoints for all data access
- [x] Comprehensive test suite (32+ tests)
- [x] Development proxy and hot reload setup

### 🚧 Pending Features
- [ ] Pinia state management for syllabus data
- [ ] Editable preview component for syllabus content
- [ ] TailwindCSS Plus component integration
- [ ] File download functionality (DOCX, PDF exports)
- [ ] Production deployment configuration
- [ ] Vue component testing setup

### 🔄 Data Pipeline Status
- **Course Descriptions**: 52/55 departments complete (✅ THR, ACC, ENG, MAT, etc.)
- **Schedule Data**: Integrated for Fall 2025 and Summer 2025 semesters
- **API Integration**: All endpoints tested and operational

## Deployment

### Development
```bash
# Start both servers
python api.py --port 8000 &
cd frontend && npm run dev
```

### Production
```bash
# Build frontend assets
cd frontend && npm run build

# Start production API
python api.py --port 8000 --env production
```

## Course Data Management

### Data Sources
- **Course Descriptions**: University course catalog (automated scraping)
- **Schedule Data**: Live course offerings from https://apps.niagara.edu/courses/
- **Department Info**: Manually curated department data

### Updates
```bash
# Update course descriptions
python utilities/scrape_descriptions.py

# Update current semester schedules  
python utilities/scrape_descriptions.py --schedules --semester 25_FA

# Update all available semesters
python utilities/scrape_descriptions.py --schedules
```

## License

MIT License - see LICENSE file for details.

## Credits

Created by Kevin Stevens (2025)

---

🚀 **Ready for development!** Start the API server and Vue dev server to begin working with the modern syllabus generator.
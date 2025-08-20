The context of this project is to repurpose the project to create syllabi for Niagara University. Academic calendars in .xslx format can be found in the ./niagara folder

Be terse and don't overexplain

TEST-DRIVEN DEVELOPMENT PROCESS:
1. Create test file with empty test functions (just function names)
2. Implement one test method at a time, in order
3. Write minimal code to make current test pass
4. Move to next test method
5. Refactor when all tests pass
6. Run git add . after each passing test

Propose functionality in the following format:

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

"NU_Syllabus_Template.docx" is the te
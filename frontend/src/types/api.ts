export interface Department {
  code: string
  name: string
  mission_statement: string | null
}

export interface Course {
  number: string
  title: string
  description: string | null
}

export interface DepartmentWithCourses extends Department {
  courses: Course[]
}

export interface ApiResponse<T> {
  [key: string]: T
}

export interface DepartmentsResponse {
  departments: Department[]
}
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Department, Course, DepartmentsResponse, DepartmentWithCourses } from '@/types/api'

interface Semester {
  key: string
  semester: string
  display: string
}

interface Offering {
  number: string
  name: string
  credits: string
  section: string
  days?: string
  start_time?: string
  end_time?: string
}

export const useApiStore = defineStore('api', {
  state: () => ({
    config: null as any,
    departments: [] as Department[],
    courses: [] as Course[],
    offerings: [] as Offering[],
    loading: false,
    semesters: [
      { key: '25_FA', semester: 'Fall 2025', display: 'Fall 2025' },
      { key: '25_SU', semester: 'Summer 2025', display: 'Summer 2025' },
      { key: '26_SP', semester: 'Spring 2026', display: 'Spring 2026' }
    ] as Semester[]
  }),

  actions: {
    async fetchConfig() {
      try {
        const response = await fetch('/api/config')
        if (response.ok) {
          this.config = await response.json()
        }
      } catch (error) {
        console.error('Error fetching config:', error)
      }
    },

    async fetchDepartments() {
      console.log('Store fetchDepartments called, current departments:', this.departments.length)
      if (this.departments.length > 0) {
        console.log('Departments already loaded, skipping fetch')
        return // Already loaded
      }
      
      console.log('Making API call to /api/departments')
      this.loading = true
      try {
        const response = await fetch('/api/departments')
        console.log('API response status:', response.status, response.ok)
        if (response.ok) {
          const data: DepartmentsResponse = await response.json()
          console.log('API data received:', data.data.departments.length, 'departments')
          this.departments = data.data.departments
          console.log('Store departments after assignment:', this.departments.length)
        } else {
          console.error('API response not ok:', response.status, response.statusText)
        }
      } catch (error) {
        console.error('Error fetching departments:', error)
      } finally {
        this.loading = false
        console.log('fetchDepartments completed, final count:', this.departments.length)
      }
    },

    async fetchCourses(departmentCode: string) {
      if (!departmentCode) {
        this.courses = []
        return
      }

      this.loading = true
      try {
        const response = await fetch(`/api/departments/${departmentCode}`)
        if (response.ok) {
          const data: DepartmentWithCourses = await response.json()
          this.courses = data.data.courses
        }
      } catch (error) {
        console.error('Error fetching courses:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchOfferings(semester: string, departmentCode: string) {
      if (!semester || !departmentCode) {
        this.offerings = []
        return
      }

      this.loading = true
      try {
        const response = await fetch(`/api/offerings/${semester}/${departmentCode}`)
        if (response.ok) {
          const data = await response.json()
          this.offerings = data.data.offerings
        }
      } catch (error) {
        console.error('Error fetching offerings:', error)
      } finally {
        this.loading = false
      }
    }
  },

  getters: {
    getDepartmentByCode: (state) => (code: string) => {
      return state.departments.find(dept => dept.code === code)
    },

    getCourseByNumber: (state) => (number: string) => {
      return state.courses.find(course => course.number === number)
    },

    getOfferingsByCourse: (state) => (courseNumber: string) => {
      return state.offerings.filter(offering => offering.course_number === courseNumber)
    }
  }
})
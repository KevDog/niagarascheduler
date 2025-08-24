<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import type { Department, Course, DepartmentsResponse, DepartmentWithCourses } from '@/types/api'

interface Semester {
  key: string
  semester: string
  year: string
  display: string
}

// Reactive data
const selectedSemester = ref('')
const instructorName = ref('')
const selectedDepartment = ref('')
const selectedCourse = ref('')
const selectedOffering = ref('')
const semesters = ref<Semester[]>([])
const departments = ref<Department[]>([])
const courses = ref<Course[]>([])
const offerings = ref<any[]>([])
const loading = ref(false)

// API calls
const fetchConfig = async () => {
  try {
    loading.value = true
    const response = await fetch('/api/config')
    const data = await response.json()
    semesters.value = data.semesters || []
  } catch (error) {
    console.error('Error fetching config:', error)
  } finally {
    loading.value = false
  }
}

const fetchDepartments = async () => {
  try {
    loading.value = true
    const response = await fetch('/api/departments')
    const data: DepartmentsResponse = await response.json()
    // Sort departments alphabetically by code
    departments.value = (data.departments || []).sort((a, b) => a.code.localeCompare(b.code))
  } catch (error) {
    console.error('Error fetching departments:', error)
  } finally {
    loading.value = false
  }
}

const fetchCourses = async (deptCode: string) => {
  if (!deptCode) {
    courses.value = []
    return
  }
  
  try {
    loading.value = true
    const response = await fetch(`/api/departments/${deptCode}`)
    const data: DepartmentWithCourses = await response.json()
    courses.value = data.courses || []
  } catch (error) {
    console.error('Error fetching courses:', error)
    courses.value = []
  } finally {
    loading.value = false
  }
}

const fetchOfferings = async (semester: string, deptCode: string, courseNumber: string) => {
  if (!semester || !deptCode || !courseNumber) {
    offerings.value = []
    return
  }
  
  try {
    loading.value = true
    const response = await fetch(`/api/offerings/${semester}/${deptCode}/${courseNumber}`)
    const data = await response.json()
    offerings.value = data.offerings || []
  } catch (error) {
    console.error('Error fetching offerings:', error)
    offerings.value = []
  } finally {
    loading.value = false
  }
}

// Watch for department changes
watch(selectedDepartment, (newDept) => {
  selectedCourse.value = '' // Reset course selection
  selectedOffering.value = '' // Reset offering selection
  if (newDept) {
    fetchCourses(newDept)
  } else {
    courses.value = []
    offerings.value = []
  }
})

// Watch for course changes
watch(selectedCourse, (newCourse) => {
  selectedOffering.value = '' // Reset offering selection
  if (newCourse && selectedDepartment.value && selectedSemester.value) {
    fetchOfferings(selectedSemester.value, selectedDepartment.value, newCourse)
  } else {
    offerings.value = []
  }
})

// Watch for semester changes (to refresh offerings if course is selected)
watch(selectedSemester, (newSemester) => {
  if (newSemester && selectedDepartment.value && selectedCourse.value) {
    fetchOfferings(newSemester, selectedDepartment.value, selectedCourse.value)
  }
})

// Computed properties
const canProceed = computed(() => {
  return selectedSemester.value && instructorName.value.trim() && selectedDepartment.value && selectedCourse.value && selectedOffering.value
})

const proceedToNext = () => {
  if (canProceed.value) {
    console.log('Proceeding with:', {
      semester: selectedSemester.value,
      instructor: instructorName.value,
      department: selectedDepartment.value,
      course: selectedCourse.value,
      offering: selectedOffering.value
    })
    // TODO: Navigate to next step
  }
}

// Load initial data on mount
onMounted(() => {
  fetchConfig()
  fetchDepartments()
})
</script>

<template>
  <main class="min-h-screen bg-gray-50 py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">
          Niagara University Syllabus Generator
        </h1>
        <p class="text-lg text-gray-600">
          Create professional syllabi with our easy-to-use wizard
        </p>
      </div>
      
      <!-- Syllabus Creation Form -->
      <div class="bg-white rounded-lg shadow-lg p-8">
        <div class="mb-8">
          <h2 class="text-2xl font-semibold text-gray-800 mb-2">Create New Syllabus</h2>
          <p class="text-gray-600">Enter your information to get started</p>
        </div>

        <form @submit.prevent="proceedToNext" class="space-y-6">
          <!-- Semester Selection -->
          <div>
            <label for="semester" class="block text-sm font-medium text-gray-700 mb-2">
              Semester <span class="text-red-500">*</span>
            </label>
            <select
              id="semester"
              v-model="selectedSemester"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              :disabled="loading"
            >
              <option value="">Select a semester</option>
              <option
                v-for="semester in semesters"
                :key="semester.key"
                :value="semester.key"
              >
                {{ semester.display }}
              </option>
            </select>
          </div>

          <!-- Instructor Name -->
          <div>
            <label for="instructor" class="block text-sm font-medium text-gray-700 mb-2">
              Instructor Name <span class="text-red-500">*</span>
            </label>
            <input
              id="instructor"
              v-model="instructorName"
              type="text"
              required
              placeholder="Enter your full name"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
            />
          </div>

          <!-- Department Selection -->
          <div>
            <label for="department" class="block text-sm font-medium text-gray-700 mb-2">
              Department <span class="text-red-500">*</span>
            </label>
            <select
              id="department"
              v-model="selectedDepartment"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              :disabled="loading"
            >
              <option value="">Select a department</option>
              <option
                v-for="dept in departments"
                :key="dept.code"
                :value="dept.code"
              >
                {{ dept.code }} - {{ dept.name }}
              </option>
            </select>
          </div>

          <!-- Course Selection -->
          <div>
            <label for="course" class="block text-sm font-medium text-gray-700 mb-2">
              Course <span class="text-red-500">*</span>
            </label>
            <select
              id="course"
              v-model="selectedCourse"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              :disabled="!selectedDepartment || loading"
            >
              <option value="">{{ selectedDepartment ? 'Select a course' : 'Select department first' }}</option>
              <option
                v-for="course in courses"
                :key="course.number"
                :value="course.number"
              >
                {{ selectedDepartment }} {{ course.number }} - {{ course.title }}
              </option>
            </select>
          </div>

          <!-- Course Offering Selection -->
          <div>
            <label for="offering" class="block text-sm font-medium text-gray-700 mb-2">
              Section <span class="text-red-500">*</span>
            </label>
            <select
              id="offering"
              v-model="selectedOffering"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              :disabled="!selectedCourse || loading || offerings.length === 0"
            >
              <option value="">{{ selectedCourse ? (offerings.length > 0 ? 'Select a section' : 'No sections available') : 'Select course first' }}</option>
              <option
                v-for="offering in offerings"
                :key="offering.number"
                :value="offering.number"
              >
                {{ offering.section || offering.number.substring(offering.number.length - 1) }} - 
                {{ offering.days && offering.start_time ? `${offering.days} ${offering.start_time}-${offering.end_time}` : `${offering.name} (${offering.credits} credits)` }}
              </option>
            </select>
          </div>

          <!-- Progress Indicator -->
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center justify-between text-sm text-gray-600 mb-2">
              <span>Step 1 of 4</span>
              <span>Basic Information</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-blue-600 h-2 rounded-full w-1/4"></div>
            </div>
          </div>

          <!-- Continue Button -->
          <button
            type="submit"
            :disabled="!canProceed"
            class="w-full py-3 px-6 rounded-lg font-medium transition duration-200"
            :class="canProceed 
              ? 'bg-blue-600 hover:bg-blue-700 text-white' 
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'"
          >
            <span v-if="loading">Loading...</span>
            <span v-else>Continue to Schedule Setup</span>
          </button>
        </form>
      </div>

      <!-- Features Section -->
      <div class="mt-12 bg-white rounded-lg shadow-lg p-8">
        <h2 class="text-2xl font-semibold text-gray-800 mb-6">Features</h2>
        <div class="grid md:grid-cols-3 gap-6">
          <div class="flex items-start">
            <svg class="w-6 h-6 text-green-500 mr-3 mt-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            <div>
              <h3 class="font-medium text-gray-800">Auto-populated Data</h3>
              <p class="text-gray-600 text-sm mt-1">Department mission statements and course information automatically included</p>
            </div>
          </div>
          <div class="flex items-start">
            <svg class="w-6 h-6 text-green-500 mr-3 mt-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            <div>
              <h3 class="font-medium text-gray-800">Multiple Formats</h3>
              <p class="text-gray-600 text-sm mt-1">Export to DOCX, PDF, HTML, and Markdown formats</p>
            </div>
          </div>
          <div class="flex items-start">
            <svg class="w-6 h-6 text-green-500 mr-3 mt-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            <div>
              <h3 class="font-medium text-gray-800">Live Preview</h3>
              <p class="text-gray-600 text-sm mt-1">Real-time preview and in-browser editing capabilities</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

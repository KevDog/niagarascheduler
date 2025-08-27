<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { Listbox, ListboxButton, ListboxOption, ListboxOptions } from '@headlessui/vue'
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/vue/20/solid'
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
    const result = await response.json()
    semesters.value = result.data?.semesters || []
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
    const result = await response.json()
    // Sort departments alphabetically by code
    departments.value = (result.data?.departments || []).sort((a, b) => a.code.localeCompare(b.code))
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
    const result = await response.json()
    courses.value = result.data?.courses || []
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
    const result = await response.json()
    offerings.value = result.data?.offerings || []
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
        <h1 class="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
          Purple Eagle Syllabus Wizard
        </h1>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto">
          Create professional syllabi with our easy-to-use wizard
        </p>
      </div>
      
      <!-- Syllabus Creation Form -->
      <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Create New Syllabus</h2>
          <p class="text-gray-600">Enter your information to get started with your professional syllabus</p>
        </div>

        <form @submit.prevent="proceedToNext" class="space-y-6">
          <!-- Semester Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Semester <span class="text-red-500">*</span>
            </label>
            <Listbox v-model="selectedSemester" :disabled="loading">
              <div class="relative">
                <ListboxButton
                  class="relative w-full cursor-default rounded-lg bg-white py-3 pl-4 pr-10 text-left border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 disabled:opacity-50"
                >
                  <span class="block truncate text-gray-900">
                    {{ selectedSemester ? semesters.find(s => s.key === selectedSemester)?.display : 'Select a semester' }}
                  </span>
                  <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
                  </span>
                </ListboxButton>

                <transition
                  leave-active-class="transition duration-100 ease-in"
                  leave-from-class="opacity-100"
                  leave-to-class="opacity-0"
                >
                  <ListboxOptions
                    class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-lg bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                  >
                    <ListboxOption
                      v-slot="{ active, selected }"
                      v-for="semester in semesters"
                      :key="semester.key"
                      :value="semester.key"
                      as="template"
                    >
                      <li
                        :class="[
                          active ? 'bg-blue-100 text-blue-900' : 'text-gray-900',
                          'relative cursor-default select-none py-3 pl-10 pr-4',
                        ]"
                      >
                        <span :class="[selected ? 'font-medium' : 'font-normal', 'block truncate']">
                          {{ semester.display }}
                        </span>
                        <span
                          v-if="selected"
                          class="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-600"
                        >
                          <CheckIcon class="h-5 w-5" aria-hidden="true" />
                        </span>
                      </li>
                    </ListboxOption>
                  </ListboxOptions>
                </transition>
              </div>
            </Listbox>
          </div>

          <!-- Instructor Name -->
          <div>
            <label for="instructor" class="block text-sm font-medium text-gray-700 mb-2">
              Instructor Name <span class="text-red-500">*</span>
            </label>
            <div class="relative rounded-lg shadow-sm">
              <input
                id="instructor"
                v-model="instructorName"
                type="text"
                required
                placeholder="Enter your full name"
                class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 transition duration-200"
              />
            </div>
          </div>

          <!-- Department Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Department <span class="text-red-500">*</span>
            </label>
            <Listbox v-model="selectedDepartment" :disabled="loading">
              <div class="relative">
                <ListboxButton
                  class="relative w-full cursor-default rounded-lg bg-white py-3 pl-4 pr-10 text-left border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 disabled:opacity-50"
                >
                  <span class="block truncate text-gray-900">
                    {{ selectedDepartment ? `${selectedDepartment} - ${departments.find(d => d.code === selectedDepartment)?.name}` : 'Select a department' }}
                  </span>
                  <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
                  </span>
                </ListboxButton>

                <transition
                  leave-active-class="transition duration-100 ease-in"
                  leave-from-class="opacity-100"
                  leave-to-class="opacity-0"
                >
                  <ListboxOptions
                    class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-lg bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                  >
                    <ListboxOption
                      v-slot="{ active, selected }"
                      v-for="dept in departments"
                      :key="dept.code"
                      :value="dept.code"
                      as="template"
                    >
                      <li
                        :class="[
                          active ? 'bg-blue-100 text-blue-900' : 'text-gray-900',
                          'relative cursor-default select-none py-3 pl-10 pr-4',
                        ]"
                      >
                        <span :class="[selected ? 'font-medium' : 'font-normal', 'block truncate']">
                          {{ dept.code }} - {{ dept.name }}
                        </span>
                        <span
                          v-if="selected"
                          class="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-600"
                        >
                          <CheckIcon class="h-5 w-5" aria-hidden="true" />
                        </span>
                      </li>
                    </ListboxOption>
                  </ListboxOptions>
                </transition>
              </div>
            </Listbox>
          </div>

          <!-- Course Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Course <span class="text-red-500">*</span>
            </label>
            <Listbox v-model="selectedCourse" :disabled="!selectedDepartment || loading">
              <div class="relative">
                <ListboxButton
                  class="relative w-full cursor-default rounded-lg bg-white py-3 pl-4 pr-10 text-left border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 disabled:opacity-50"
                >
                  <span class="block truncate text-gray-900">
                    {{ selectedCourse ? `${selectedDepartment} ${selectedCourse} - ${courses.find(c => c.number === selectedCourse)?.title}` : (selectedDepartment ? 'Select a course' : 'Select department first') }}
                  </span>
                  <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
                  </span>
                </ListboxButton>

                <transition
                  leave-active-class="transition duration-100 ease-in"
                  leave-from-class="opacity-100"
                  leave-to-class="opacity-0"
                >
                  <ListboxOptions
                    class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-lg bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                  >
                    <ListboxOption
                      v-slot="{ active, selected }"
                      v-for="course in courses"
                      :key="course.number"
                      :value="course.number"
                      as="template"
                    >
                      <li
                        :class="[
                          active ? 'bg-blue-100 text-blue-900' : 'text-gray-900',
                          'relative cursor-default select-none py-3 pl-10 pr-4',
                        ]"
                      >
                        <span :class="[selected ? 'font-medium' : 'font-normal', 'block truncate']">
                          {{ selectedDepartment }} {{ course.number }} - {{ course.title }}
                        </span>
                        <span
                          v-if="selected"
                          class="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-600"
                        >
                          <CheckIcon class="h-5 w-5" aria-hidden="true" />
                        </span>
                      </li>
                    </ListboxOption>
                  </ListboxOptions>
                </transition>
              </div>
            </Listbox>
          </div>

          <!-- Course Offering Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Section <span class="text-red-500">*</span>
            </label>
            <Listbox v-model="selectedOffering" :disabled="!selectedCourse || loading || offerings.length === 0">
              <div class="relative">
                <ListboxButton
                  class="relative w-full cursor-default rounded-lg bg-white py-3 pl-4 pr-10 text-left border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 disabled:opacity-50"
                >
                  <span class="block truncate text-gray-900">
                    {{ selectedOffering ? 
                      `${offerings.find(o => o.number === selectedOffering)?.section || selectedOffering.substring(selectedOffering.length - 1)} - ${offerings.find(o => o.number === selectedOffering)?.days && offerings.find(o => o.number === selectedOffering)?.start_time ? 
                        `${offerings.find(o => o.number === selectedOffering)?.days} ${offerings.find(o => o.number === selectedOffering)?.start_time}-${offerings.find(o => o.number === selectedOffering)?.end_time}` : 
                        `${offerings.find(o => o.number === selectedOffering)?.name} (${offerings.find(o => o.number === selectedOffering)?.credits} credits)`}`
                      : (selectedCourse ? (offerings.length > 0 ? 'Select a section' : 'No sections available') : 'Select course first') }}
                  </span>
                  <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
                  </span>
                </ListboxButton>

                <transition
                  leave-active-class="transition duration-100 ease-in"
                  leave-from-class="opacity-100"
                  leave-to-class="opacity-0"
                >
                  <ListboxOptions
                    class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-lg bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                  >
                    <ListboxOption
                      v-slot="{ active, selected }"
                      v-for="offering in offerings"
                      :key="offering.number"
                      :value="offering.number"
                      as="template"
                    >
                      <li
                        :class="[
                          active ? 'bg-blue-100 text-blue-900' : 'text-gray-900',
                          'relative cursor-default select-none py-3 pl-10 pr-4',
                        ]"
                      >
                        <span :class="[selected ? 'font-medium' : 'font-normal', 'block truncate']">
                          {{ offering.section || offering.number.substring(offering.number.length - 1) }} - 
                          {{ offering.days && offering.start_time ? `${offering.days} ${offering.start_time}-${offering.end_time}` : `${offering.name} (${offering.credits} credits)` }}
                        </span>
                        <span
                          v-if="selected"
                          class="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-600"
                        >
                          <CheckIcon class="h-5 w-5" aria-hidden="true" />
                        </span>
                      </li>
                    </ListboxOption>
                  </ListboxOptions>
                </transition>
              </div>
            </Listbox>
          </div>

          <!-- Progress Indicator -->
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
            <div class="flex items-center justify-between text-sm font-medium text-gray-700 mb-3">
              <span class="text-blue-600">Step 1 of 4</span>
              <span>Basic Information</span>
            </div>
            <div class="w-full bg-blue-100 rounded-full h-2.5 shadow-inner">
              <div class="bg-gradient-to-r from-blue-500 to-indigo-600 h-2.5 rounded-full w-1/4 shadow-sm transition-all duration-300"></div>
            </div>
          </div>

          <!-- Continue Button -->
          <button
            type="submit"
            :disabled="!canProceed || loading"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-base font-medium rounded-lg text-white transition duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            :class="canProceed && !loading
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5' 
              : 'bg-gray-300 cursor-not-allowed'"
          >
            <span v-if="loading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Loading...
            </span>
            <span v-else class="flex items-center">
              Continue to Schedule Setup
              <svg class="ml-2 -mr-1 w-5 h-5 transition-transform group-hover:translate-x-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"></path>
              </svg>
            </span>
          </button>
        </form>
      </div>

      <!-- Features Section -->
      <div class="mt-12 bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-8 text-center">Features</h2>
        <div class="grid md:grid-cols-3 gap-8">
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

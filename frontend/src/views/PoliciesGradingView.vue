<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Get wizard data from query parameters (passed from previous steps)
const wizardData = ref({
  semester: route.query.semester as string || '',
  instructor: route.query.instructor as string || '',
  department: route.query.department as string || '',
  course: route.query.course as string || '',
  offering: route.query.offering as string || '',
})

// Form data for policies and grading
const policiesData = ref({
  attendancePolicy: '',
  latePolicy: '',
  makeupPolicy: '',
  gradingScale: 'standard', // standard, custom
  customGradingScale: {
    aPlus: 97,
    a: 93,
    aMinus: 90,
    bPlus: 87,
    b: 83,
    bMinus: 80,
    cPlus: 77,
    c: 73,
    cMinus: 70,
    dPlus: 67,
    d: 63,
    dMinus: 60,
    f: 0
  },
  gradingComponents: [
    { name: 'Participation', percentage: 10 },
    { name: 'Assignments', percentage: 30 },
    { name: 'Midterm Exam', percentage: 25 },
    { name: 'Final Exam', percentage: 35 }
  ],
  academicIntegrityPolicy: '',
  accommodationsPolicy: 'Students with documented disabilities who may need accommodations should schedule an appointment with the instructor as soon as possible. All discussions will remain confidential. Students with disabilities should also contact the Office of Accessibility Services to verify their eligibility for reasonable accommodations.',
  communicationPolicy: '',
  technologyPolicy: ''
})

const loading = ref(false)

// Computed properties
const canProceed = computed(() => {
  return policiesData.value.attendancePolicy.trim() && 
         policiesData.value.gradingComponents.length > 0 &&
         totalPercentage.value === 100
})

const totalPercentage = computed(() => {
  return policiesData.value.gradingComponents.reduce((sum, component) => sum + component.percentage, 0)
})

const totalPercentageColor = computed(() => {
  if (totalPercentage.value === 100) return 'text-green-600'
  if (totalPercentage.value > 100) return 'text-red-600'
  return 'text-amber-600'
})

// Methods
const addGradingComponent = () => {
  policiesData.value.gradingComponents.push({ name: '', percentage: 0 })
}

const removeGradingComponent = (index: number) => {
  policiesData.value.gradingComponents.splice(index, 1)
}

const savePoliciesData = async () => {
  loading.value = true
  try {
    // Store policies data locally (managed by component state)
    console.log('Policies data configured:', policiesData.value)
    
    // Navigate to next step (class policies)
    router.push({
      name: 'class-policies',
      query: wizardData.value
    })
  } catch (error) {
    console.error('Error navigating to class policies:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push({ 
    name: 'course-content',
    query: wizardData.value
  })
}

onMounted(() => {
  // If no wizard data, redirect to home
  if (!wizardData.value.semester || !wizardData.value.instructor) {
    router.push({ name: 'home' })
    return
  }
})
</script>

<template>
  <main class="min-h-screen bg-gray-900 py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold bg-gradient-to-r from-purple-500 to-purple-700 bg-clip-text text-transparent mb-4">
          Policies & Grading
        </h1>
        <p class="text-xl text-gray-300 max-w-2xl mx-auto">
          Define your course policies and grading structure
        </p>
      </div>

      <!-- Course Info Summary -->
      <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 mb-8">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Course Information</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span class="font-medium text-gray-500">Semester:</span>
            <p class="text-gray-900">{{ wizardData.semester }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-500">Instructor:</span>
            <p class="text-gray-900">{{ wizardData.instructor }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-500">Course:</span>
            <p class="text-gray-900">{{ wizardData.department }} {{ wizardData.course }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-500">Section:</span>
            <p class="text-gray-900">{{ wizardData.offering }}</p>
          </div>
        </div>
      </div>
      
      <!-- Policies and Grading Form -->
      <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Course Policies & Grading</h2>
          <p class="text-gray-600">Set up your course policies and grading structure</p>
        </div>

        <div class="space-y-8">
          <!-- Attendance Policy -->
          <div>
            <label for="attendancePolicy" class="block text-sm font-medium text-gray-700 mb-2">
              Attendance Policy *
            </label>
            <textarea
              id="attendancePolicy"
              v-model="policiesData.attendancePolicy"
              rows="4"
              placeholder="Describe your attendance requirements and policies..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>

          <!-- Grading Components -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-4">
              Grading Components *
              <div class="flex items-center justify-between mt-2">
                <span class="text-xs text-gray-500">Total must equal 100%</span>
                <span :class="totalPercentageColor" class="text-sm font-semibold">
                  Total: {{ totalPercentage }}%
                </span>
              </div>
            </label>
            
            <div class="space-y-3">
              <div
                v-for="(component, index) in policiesData.gradingComponents"
                :key="index"
                class="flex gap-3 items-center bg-gray-50 p-3 rounded-lg"
              >
                <input
                  v-model="component.name"
                  type="text"
                  placeholder="Component name"
                  class="flex-1 rounded-lg border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-purple-600"
                />
                <div class="flex items-center gap-2">
                  <input
                    v-model.number="component.percentage"
                    type="number"
                    min="0"
                    max="100"
                    class="w-20 rounded-lg border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-purple-600"
                  />
                  <span class="text-gray-600">%</span>
                </div>
                <button
                  type="button"
                  @click="removeGradingComponent(index)"
                  class="text-red-600 hover:text-red-800 px-2 py-1"
                >
                  ✕
                </button>
              </div>
              
              <button
                type="button"
                @click="addGradingComponent"
                class="text-purple-600 hover:text-purple-800 font-medium px-3 py-2 border border-purple-300 rounded-lg hover:bg-purple-50 transition-colors"
              >
                + Add Component
              </button>
            </div>
          </div>

          <!-- Late Policy -->
          <div>
            <label for="latePolicy" class="block text-sm font-medium text-gray-700 mb-2">
              Late Assignment Policy
            </label>
            <textarea
              id="latePolicy"
              v-model="policiesData.latePolicy"
              rows="3"
              placeholder="Describe penalties for late submissions..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>

          <!-- Makeup Policy -->
          <div>
            <label for="makeupPolicy" class="block text-sm font-medium text-gray-700 mb-2">
              Makeup Exam/Assignment Policy
            </label>
            <textarea
              id="makeupPolicy"
              v-model="policiesData.makeupPolicy"
              rows="3"
              placeholder="Describe makeup policies for exams and assignments..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>

          <!-- Academic Integrity Policy -->
          <div>
            <label for="academicIntegrityPolicy" class="block text-sm font-medium text-gray-700 mb-2">
              Academic Integrity Policy
            </label>
            <textarea
              id="academicIntegrityPolicy"
              v-model="policiesData.academicIntegrityPolicy"
              rows="4"
              placeholder="Describe your academic integrity expectations and consequences..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>

          <!-- Communication Policy -->
          <div>
            <label for="communicationPolicy" class="block text-sm font-medium text-gray-700 mb-2">
              Communication Policy
            </label>
            <textarea
              id="communicationPolicy"
              v-model="policiesData.communicationPolicy"
              rows="3"
              placeholder="Describe office hours, email response time, preferred communication methods..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>
        </div>

        <!-- Progress Indicator -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100 mt-8">
          <div class="flex items-center justify-between text-sm font-medium text-gray-700 mb-3">
            <span class="text-purple-600">Step 5 of 7</span>
            <span>Policies & Grading</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-gradient-to-r from-purple-500 to-purple-700 h-2 rounded-full" style="width: 71%"></div>
          </div>
        </div>

        <!-- Navigation -->
        <div class="flex justify-between items-center pt-8">
          <button
            type="button"
            @click="goBack"
            class="inline-flex items-center px-6 py-3 border border-gray-300 shadow-sm text-base font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition duration-200"
          >
            <svg class="mr-2 -ml-1 w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd"></path>
            </svg>
            Back to Course Content
          </button>
          
          <button
            type="button"
            @click="savePoliciesData"
            :disabled="!canProceed || loading"
            :class="{
              'opacity-50 cursor-not-allowed': !canProceed || loading,
              'hover:bg-purple-700 hover:shadow-lg transform hover:-translate-y-0.5': canProceed && !loading
            }"
            class="group inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-purple-600 shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition duration-200"
          >
            <span v-if="loading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating Syllabus...
            </span>
            <span v-else class="flex items-center">
              Continue to Class Policies
              <svg class="ml-2 -mr-1 w-5 h-5 transition-transform group-hover:translate-x-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"></path>
              </svg>
            </span>
          </button>
        </div>
      </div>
    </div>
  </main>
</template>
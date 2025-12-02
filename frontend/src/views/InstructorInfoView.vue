<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Get wizard data from query parameters (passed from previous step)
const wizardData = ref({
  semester: route.query.semester as string || '',
  department: route.query.department as string || '',
  course: route.query.course as string || '',
  offering: route.query.offering as string || '',
})

// Form data for instructor information
const instructorData = ref({
  instructorName: '',
  officeHours: '',
  officeLocation: '',
  emailAddress: '',
  phoneNumber: ''
})

const loading = ref(false)

// Computed properties
const canProceed = computed(() => {
  return instructorData.value.instructorName.trim().length > 0 &&
         instructorData.value.officeHours.trim().length > 0 &&
         instructorData.value.officeLocation.trim().length > 0 &&
         instructorData.value.emailAddress.trim().length > 0 &&
         instructorData.value.phoneNumber.trim().length > 0
})

// Methods
const saveInstructorData = async () => {
  loading.value = true
  try {
    // Navigate to next step (schedule setup) with all wizard data including instructor
    router.push({
      name: 'schedule-setup',
      query: {
        ...wizardData.value,
        instructor: instructorData.value.instructorName,
        officeHours: instructorData.value.officeHours,
        officeLocation: instructorData.value.officeLocation,
        emailAddress: instructorData.value.emailAddress,
        phoneNumber: instructorData.value.phoneNumber
      }
    })
  } catch (error) {
    console.error('Error navigating to schedule setup:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push({ 
    name: 'home',
    query: wizardData.value
  })
}

onMounted(() => {
  // If no wizard data from previous step, redirect to home
  if (!wizardData.value.semester || !wizardData.value.department) {
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
          Instructor Information
        </h1>
        <p class="text-xl text-gray-300 max-w-2xl mx-auto">
          Enter your information as the course instructor
        </p>
      </div>

      <!-- Course Info Summary -->
      <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 mb-8">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Selected Course</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span class="font-medium text-gray-500">Semester:</span>
            <p class="text-gray-900">{{ wizardData.semester }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-500">Department:</span>
            <p class="text-gray-900">{{ wizardData.department }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-500">Course:</span>
            <p class="text-gray-900">{{ wizardData.course }}</p>
          </div>
          <div>
            <span class="font-medium text-gray-500">Section:</span>
            <p class="text-gray-900">{{ wizardData.offering }}</p>
          </div>
        </div>
      </div>
      
      <!-- Instructor Information Form -->
      <form @submit.prevent="saveInstructorData" class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Instructor Information</h2>
          <p class="text-gray-600">Please enter your information as the course instructor</p>
        </div>

        <div class="space-y-6">
          <!-- Instructor Name -->
          <div>
            <label for="instructorName" class="block text-sm font-medium text-gray-700 mb-2">
              Instructor Name <span class="text-red-500">*</span>
            </label>
            <input
              id="instructorName"
              v-model="instructorData.instructorName"
              type="text"
              required
              placeholder="Enter your full name (e.g., Dr. Jane Smith)"
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            />
            <p class="mt-2 text-sm text-gray-500">
              This name will appear on the syllabus and course materials
            </p>
          </div>

          <!-- Office Hours -->
          <div>
            <label for="officeHours" class="block text-sm font-medium text-gray-700 mb-2">
              Office Hours <span class="text-red-500">*</span>
            </label>
            <input
              id="officeHours"
              v-model="instructorData.officeHours"
              type="text"
              required
              placeholder="e.g., MWF 2:00-3:00 PM, or by appointment"
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            />
            <p class="mt-2 text-sm text-gray-500">
              When students can meet with you for help
            </p>
          </div>

          <!-- Office Location -->
          <div>
            <label for="officeLocation" class="block text-sm font-medium text-gray-700 mb-2">
              Office Location <span class="text-red-500">*</span>
            </label>
            <input
              id="officeLocation"
              v-model="instructorData.officeLocation"
              type="text"
              required
              placeholder="e.g., Castellani Art Museum 123, or Virtual via Zoom"
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            />
            <p class="mt-2 text-sm text-gray-500">
              Where students can find your office
            </p>
          </div>

          <!-- Email Address -->
          <div>
            <label for="emailAddress" class="block text-sm font-medium text-gray-700 mb-2">
              Email Address <span class="text-red-500">*</span>
            </label>
            <input
              id="emailAddress"
              v-model="instructorData.emailAddress"
              type="email"
              required
              placeholder="e.g., jsmith@niagara.edu"
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            />
            <p class="mt-2 text-sm text-gray-500">
              Your university email address for student communication
            </p>
          </div>

          <!-- Phone Number -->
          <div>
            <label for="phoneNumber" class="block text-sm font-medium text-gray-700 mb-2">
              Phone Number <span class="text-red-500">*</span>
            </label>
            <input
              id="phoneNumber"
              v-model="instructorData.phoneNumber"
              type="tel"
              required
              placeholder="e.g., (716) 286-8000"
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            />
            <p class="mt-2 text-sm text-gray-500">
              Your office or departmental phone number
            </p>
          </div>
        </div>

        <!-- Progress Indicator -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100 mt-8">
          <div class="flex items-center justify-between text-sm font-medium text-gray-700 mb-3">
            <span class="text-purple-600">Step 2 of 7</span>
            <span>Instructor Information</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-gradient-to-r from-purple-500 to-purple-700 h-2 rounded-full" style="width: 29%"></div>
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
            Back to Course Selection
          </button>
          
          <button
            type="submit"
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
              Processing...
            </span>
            <span v-else class="flex items-center">
              Continue to Schedule Setup
              <svg class="ml-2 -mr-1 w-5 h-5 transition-transform group-hover:translate-x-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"></path>
              </svg>
            </span>
          </button>
        </div>
      </form>
    </div>
  </main>
</template>
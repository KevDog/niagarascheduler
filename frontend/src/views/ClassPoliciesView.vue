<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useScheduleStore } from '@/stores/schedule'
import { storeToRefs } from 'pinia'

const router = useRouter()
const route = useRoute()
const scheduleStore = useScheduleStore()
const { scheduleItems } = storeToRefs(scheduleStore)

// Get wizard data from query parameters (passed from previous steps)
const wizardData = ref({
  semester: route.query.semester as string || '',
  instructor: route.query.instructor as string || '',
  department: route.query.department as string || '',
  course: route.query.course as string || '',
  offering: route.query.offering as string || '',
})

// Form data for class policies
const classPoliciesData = ref({
  classroomBehavior: 'Please arrive on time and come prepared for class. Cell phones should be silenced and put away during class time. Laptops are permitted for note-taking and course-related activities only.',
  participationExpectations: 'Active participation in class discussions, activities, and group work is expected and will contribute to your learning and grade.',
  emailPolicy: 'I will respond to emails within 24-48 hours during weekdays. Please use your university email address and include the course name in the subject line.',
  officeHoursPolicy: 'Office hours are available for questions about course material, assignments, or academic concerns. Please feel free to stop by or schedule an appointment.',
  resourcesPolicy: 'All required readings and materials will be made available through the course management system. Additional resources may be provided as needed.',
  diversityStatement: 'This classroom is committed to creating an inclusive environment where all students feel valued and respected regardless of background, identity, or experience.',
  mentalHealthResources: 'Your mental health and well-being are important. If you are struggling, please reach out to campus counseling services or speak with me about accommodations.',
  emergencyProcedures: 'In case of emergency, follow university protocols. Emergency information and procedures are posted in the classroom and available in the student handbook.'
})

const loading = ref(false)

// Computed properties
const canProceed = computed(() => {
  return classPoliciesData.value.classroomBehavior.trim() && 
         classPoliciesData.value.participationExpectations.trim()
})

// Methods
const generateSyllabus = async () => {
  loading.value = true
  try {
    // Parse semester to extract year
    const semesterParts = wizardData.value.semester.split('_')
    const year = 2000 + parseInt(semesterParts[0]) // Convert "25" to 2025
    
    const requestData = {
      // Required API fields
      schedule: scheduleItems.value || [],
      semester: wizardData.value.semester,
      year: year,
      
      // Optional API fields
      course_id: `${wizardData.value.department} ${wizardData.value.course}`,
      instructor_name: wizardData.value.instructor,
      
      // Map class policies data to API expected fields
      attendance_policy: classPoliciesData.value.classroomBehavior || '',
      grading_policy: classPoliciesData.value.participationExpectations || '',
      ai_policy: classPoliciesData.value.emailPolicy || '',
      textbooks: '',
      assignments: '',
      bibliography: ''
    }
    
    console.log('Sending syllabus generation request with data:', requestData)
    
    const response = await fetch('/api/generate-syllabus', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    })
    
    if (response.ok) {
      const data = await response.json()
      console.log('Syllabus generated:', data)
      // Navigate back to home with success (temporary - until syllabus preview is created)
      alert('Syllabus generated successfully!')
      router.push({ name: 'home' })
    } else {
      const errorData = await response.text()
      console.error('API Error:', response.status, response.statusText)
      console.error('Error response:', errorData)
      alert(`Error generating syllabus (${response.status}): ${errorData}`)
    }
  } catch (error) {
    console.error('Error generating syllabus:', error)
    alert('Error generating syllabus. Please check your connection and try again.')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push({ name: 'policies-grading' })
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
          Class Policies
        </h1>
        <p class="text-xl text-gray-300 max-w-2xl mx-auto">
          Set expectations and guidelines for your classroom environment
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
      
      <!-- Class Policies Form -->
      <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Class Policies & Expectations</h2>
          <p class="text-gray-600">Define classroom behavior, expectations, and support resources</p>
        </div>

        <div class="space-y-8">
          <!-- Classroom Behavior -->
          <div>
            <label for="classroomBehavior" class="block text-sm font-medium text-gray-700 mb-2">
              Classroom Behavior & Expectations *
            </label>
            <textarea
              id="classroomBehavior"
              v-model="classPoliciesData.classroomBehavior"
              rows="4"
              placeholder="Describe expectations for classroom behavior, punctuality, technology use..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>

          <!-- Participation Expectations -->
          <div>
            <label for="participationExpectations" class="block text-sm font-medium text-gray-700 mb-2">
              Participation Expectations *
            </label>
            <textarea
              id="participationExpectations"
              v-model="classPoliciesData.participationExpectations"
              rows="3"
              placeholder="Describe how students should participate in class discussions and activities..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>

          <!-- Communication Policy -->
          <div>
            <label for="emailPolicy" class="block text-sm font-medium text-gray-700 mb-2">
              Email & Communication Policy
            </label>
            <textarea
              id="emailPolicy"
              v-model="classPoliciesData.emailPolicy"
              rows="3"
              placeholder="Describe email response time, office hours, communication expectations..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>

          <!-- Office Hours Policy -->
          <div>
            <label for="officeHoursPolicy" class="block text-sm font-medium text-gray-700 mb-2">
              Office Hours & Support
            </label>
            <textarea
              id="officeHoursPolicy"
              v-model="classPoliciesData.officeHoursPolicy"
              rows="3"
              placeholder="Describe office hours availability, how to get help, appointment scheduling..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>

          <!-- Resources Policy -->
          <div>
            <label for="resourcesPolicy" class="block text-sm font-medium text-gray-700 mb-2">
              Course Resources & Materials
            </label>
            <textarea
              id="resourcesPolicy"
              v-model="classPoliciesData.resourcesPolicy"
              rows="3"
              placeholder="Describe how course materials will be distributed, resource access..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>

          <!-- Diversity & Inclusion -->
          <div>
            <label for="diversityStatement" class="block text-sm font-medium text-gray-700 mb-2">
              Diversity & Inclusion Statement
            </label>
            <textarea
              id="diversityStatement"
              v-model="classPoliciesData.diversityStatement"
              rows="3"
              placeholder="Describe your commitment to creating an inclusive learning environment..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>

          <!-- Mental Health & Wellness -->
          <div>
            <label for="mentalHealthResources" class="block text-sm font-medium text-gray-700 mb-2">
              Mental Health & Wellness Resources
            </label>
            <textarea
              id="mentalHealthResources"
              v-model="classPoliciesData.mentalHealthResources"
              rows="3"
              placeholder="Provide information about campus mental health resources and support..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>

          <!-- Emergency Procedures -->
          <div>
            <label for="emergencyProcedures" class="block text-sm font-medium text-gray-700 mb-2">
              Emergency Procedures
            </label>
            <textarea
              id="emergencyProcedures"
              v-model="classPoliciesData.emergencyProcedures"
              rows="3"
              placeholder="Describe emergency procedures and safety protocols..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>
        </div>

        <!-- Progress Indicator -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100 mt-8">
          <div class="flex items-center justify-between text-sm font-medium text-gray-700 mb-3">
            <span class="text-purple-600">Step 5 of 5</span>
            <span>Class Policies</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-gradient-to-r from-purple-500 to-purple-700 h-2 rounded-full" style="width: 100%"></div>
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
            Back to Policies & Grading
          </button>
          
          <button
            type="button"
            @click="generateSyllabus"
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
              Generate Syllabus
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
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useApiStore } from '@/stores/api'
import { storeToRefs } from 'pinia'
import type { Course } from '@/types/api'

const router = useRouter()
const route = useRoute()
const apiStore = useApiStore()

// Get wizard data from query parameters (passed from previous steps)
const wizardData = ref({
  semester: route.query.semester as string || '',
  instructor: route.query.instructor as string || '',
  department: route.query.department as string || '',
  course: route.query.course as string || '',
  offering: route.query.offering as string || '',
})

// AI Policy options
const aiPolicyOptions = {
  restrictive: `It is expected that all work you submit in this course will be your own. The use of generative artificial intelligence (A.I.) tools like ChatGPT, Dall-E, Gemini, or similar is expressly prohibited. Students are forbidden from using A.I. tools at all stages of their creative process. Use of a generative A.I. tool is considered academic misconduct, and the violation will be reported to the University's Academic Integrity Board. Academic misconduct includes (but is not limited to) using ideas, words, images, or other content that you did not create without attribution and presenting that content as if you were the creator.`,
  moderate: `Certain assignments in this course will permit the use of generative artificial intelligence (A.I.) tools such as ChatGPT, Dall-E, Gemini, or similar. By default, the use of such tools is disallowed unless otherwise stated. You may only use generative A.I. tools on those assignments where permission is expressly granted. Further, any use must be appropriately acknowledged and include a corresponding citation. It is the student's responsibility to evaluate the A.I. output for validity and applicability to the topic. Violations of this policy will be considered academic misconduct.`,
  permissive: `Students are encouraged to utilize generative artificial intelligence (A.I.) tools like ChatGPT, Dall-E, Gemini, or similar for all assignments and assessments in this course. Proper acknowledgment and corresponding citations are required for any use of such tools. It is the student's responsibility to evaluate the A.I. output for validity and applicability to the topic. Violations of this policy will be considered academic misconduct.`
}

// Form data for course content
const courseContentData = ref({
  courseDescription: '',
  methodOfTeaching: '',
  studentLearningOutcomes: '',
  assessment: '',
  textbooks: '',
  majorAssignments: '',
  bibliography: '',
  aiPolicyType: 'restrictive' as keyof typeof aiPolicyOptions,
  aiPolicy: aiPolicyOptions.restrictive
})

// Load course data and populate description
const loadCourseData = async () => {
  try {
    const response = await fetch(`/api/departments/${wizardData.value.department}`)
    if (response.ok) {
      const data = await response.json()
      const course = data.courses?.find((c: Course) => c.number === wizardData.value.course)
      if (course?.description) {
        courseContentData.value.courseDescription = course.description
      }
    }
  } catch (error) {
    console.error('Error loading course data:', error)
  }
}

const loading = ref(false)

// Help text for informational sections
const helpTexts = {
  studentLearningOutcomes: 'Please list the student learning objectives here. If you are unsure of the departmental student learning objectives associated with the course, please check with the department chair.\n\nLearning Objectives should indicate skills, knowledge and competencies students should have acquired by the end of the semester. All syllabi must articulate clear links between course goals, department/program goals, college goals, or Gen Ed goals.',
  assessment: 'Please describe assessment information here by indicating clearly how each of the stated student learning objectives will be assessed.',
  workloadInfo: 'A typical three-credit course expects an average of two hours of coursework outside of the classroom for every one hour of in-class instruction.'
}

// Computed properties
const canProceed = computed(() => {
  return courseContentData.value.courseDescription.trim() && 
         courseContentData.value.methodOfTeaching.trim() &&
         courseContentData.value.studentLearningOutcomes.trim() &&
         courseContentData.value.assessment.trim()
})

// Methods
const updateAiPolicy = () => {
  courseContentData.value.aiPolicy = aiPolicyOptions[courseContentData.value.aiPolicyType]
}

const saveCourseContentData = async () => {
  loading.value = true
  try {
    console.log('Course content data configured:', courseContentData.value)
    
    // Navigate to next step (policies and grading)
    router.push({
      name: 'policies-grading',
      query: wizardData.value
    })
  } catch (error) {
    console.error('Error navigating to policies:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push({ 
    name: 'schedule-setup',
    query: wizardData.value
  })
}

onMounted(async () => {
  // If no wizard data, redirect to home
  if (!wizardData.value.semester || !wizardData.value.instructor) {
    router.push({ name: 'home' })
    return
  }
  
  // Load course data and pre-populate description
  await loadCourseData()
})
</script>

<template>
  <main class="min-h-screen bg-gray-900 py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold bg-gradient-to-r from-purple-500 to-purple-700 bg-clip-text text-transparent mb-4">
          Course Content
        </h1>
        <p class="text-xl text-gray-300 max-w-2xl mx-auto">
          Define course descriptions, learning outcomes, and materials
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
      
      <!-- Course Content Form -->
      <form @submit.prevent="saveCourseContentData" class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Course Content & Materials</h2>
          <p class="text-gray-600">Define course content, learning outcomes, and required materials</p>
        </div>

        <div class="space-y-8">
          <!-- Course Description -->
          <div>
            <label for="courseDescription" class="block text-sm font-medium text-gray-700 mb-2">
              Course Description *
              <span class="text-xs text-gray-500 font-normal">(from catalog, may be edited)</span>
            </label>
            <textarea
              id="courseDescription"
              v-model="courseContentData.courseDescription"
              rows="4"
              placeholder="Loading course description from catalog..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
              required
            ></textarea>
          </div>

          <!-- Method of Teaching -->
          <div>
            <label for="methodOfTeaching" class="block text-sm font-medium text-gray-700 mb-2">
              Method of Teaching *
            </label>
            <textarea
              id="methodOfTeaching"
              v-model="courseContentData.methodOfTeaching"
              rows="3"
              placeholder="Describe your teaching methodology, classroom format, instructional strategies..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
              required
            ></textarea>
          </div>

          <!-- Student Learning Outcomes -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <label for="studentLearningOutcomes" class="block text-sm font-medium text-gray-700">
                Student Learning Outcomes *
              </label>
              <button
                type="button" 
                class="text-purple-600 hover:text-purple-500 text-xs"
                @click="$refs.learningOutcomesHelp.showModal()"
              >
                ℹ Help
              </button>
            </div>
            <textarea
              id="studentLearningOutcomes"
              v-model="courseContentData.studentLearningOutcomes"
              rows="5"
              placeholder="List specific learning objectives and outcomes students should achieve..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
              required
            ></textarea>
          </div>

          <!-- Assessment -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <label for="assessment" class="block text-sm font-medium text-gray-700">
                Assessment *
              </label>
              <button
                type="button" 
                class="text-purple-600 hover:text-purple-500 text-xs"
                @click="$refs.assessmentHelp.showModal()"
              >
                ℹ Help
              </button>
            </div>
            <textarea
              id="assessment"
              v-model="courseContentData.assessment"
              rows="4"
              placeholder="Describe how each learning objective will be assessed..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
              required
            ></textarea>
          </div>

          <!-- Textbooks -->
          <div>
            <label for="textbooks" class="block text-sm font-medium text-gray-700 mb-2">
              Textbook(s) and Required Materials
            </label>
            <textarea
              id="textbooks"
              v-model="courseContentData.textbooks"
              rows="3"
              placeholder="List required textbooks, materials, software, etc..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>

          <!-- Major Assignments -->
          <div>
            <label for="majorAssignments" class="block text-sm font-medium text-gray-700 mb-2">
              Major Assignments
            </label>
            <textarea
              id="majorAssignments"
              v-model="courseContentData.majorAssignments"
              rows="4"
              placeholder="Describe major projects, papers, exams, and assignments..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>

          <!-- AI Policy -->
          <div>
            <label for="aiPolicyType" class="block text-sm font-medium text-gray-700 mb-2">
              Course Policy on Generative A.I.
            </label>
            <select
              id="aiPolicyType"
              v-model="courseContentData.aiPolicyType"
              @change="updateAiPolicy"
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200 mb-4"
            >
              <option value="restrictive">Restrictive - AI tools expressly prohibited</option>
              <option value="moderate">Moderate - AI tools allowed on specific assignments only</option>
              <option value="permissive">Permissive - AI tools encouraged with proper citation</option>
            </select>
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p class="text-sm text-gray-700 leading-relaxed">{{ courseContentData.aiPolicy }}</p>
            </div>
          </div>

          <!-- Bibliography -->
          <div>
            <label for="bibliography" class="block text-sm font-medium text-gray-700 mb-2">
              Bibliography / Additional Resources
            </label>
            <textarea
              id="bibliography"
              v-model="courseContentData.bibliography"
              rows="3"
              placeholder="List supplementary readings, references, and resources..."
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            ></textarea>
          </div>
        </div>

        <!-- Progress Indicator -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100 mt-8">
          <div class="flex items-center justify-between text-sm font-medium text-gray-700 mb-3">
            <span class="text-purple-600">Step 4 of 7</span>
            <span>Course Content</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-gradient-to-r from-purple-500 to-purple-700 h-2 rounded-full" style="width: 57%"></div>
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
            Back to Schedule
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
              Saving Content...
            </span>
            <span v-else class="flex items-center">
              Grading
              <svg class="ml-2 -mr-1 w-5 h-5 transition-transform group-hover:translate-x-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"></path>
              </svg>
            </span>
          </button>
        </div>
      </form>
    </div>

    <!-- Help Modals -->
    <dialog ref="learningOutcomesHelp" class="rounded-xl p-6 max-w-2xl">
      <h3 class="text-lg font-semibold mb-4">Student Learning Outcomes - Guidelines</h3>
      <p class="text-gray-700 whitespace-pre-line">{{ helpTexts.studentLearningOutcomes }}</p>
      <button @click="$refs.learningOutcomesHelp.close()" class="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">Close</button>
    </dialog>

    <dialog ref="assessmentHelp" class="rounded-xl p-6 max-w-2xl">
      <h3 class="text-lg font-semibold mb-4">Assessment - Guidelines</h3>
      <p class="text-gray-700 whitespace-pre-line">{{ helpTexts.assessment }}</p>
      <button @click="$refs.assessmentHelp.close()" class="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">Close</button>
    </dialog>
  </main>
</template>
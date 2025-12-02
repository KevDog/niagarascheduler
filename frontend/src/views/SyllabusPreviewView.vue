<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useScheduleStore } from '@/stores/schedule'
import { storeToRefs } from 'pinia'
import { marked } from 'marked'

const router = useRouter()
const route = useRoute()
const scheduleStore = useScheduleStore()
const { scheduleItems } = storeToRefs(scheduleStore)

// Get wizard data from query parameters
const wizardData = ref({
  semester: route.query.semester as string || '',
  instructor: route.query.instructor as string || '',
  department: route.query.department as string || '',
  course: route.query.course as string || '',
  offering: route.query.offering as string || '',
})

const syllabusContent = ref('')
const loading = ref(false)
const generatingDownload = ref('')

// Configure marked options
marked.setOptions({
  breaks: true,
  gfm: true
})

// Function to remove YAML front matter from markdown
const stripFrontMatter = (markdown: string): string => {
  // Remove YAML front matter (content between --- at the beginning)
  const frontMatterRegex = /^---\s*\n([\s\S]*?)\n---\s*\n/
  return markdown.replace(frontMatterRegex, '')
}

// Computed property for rendered HTML
const renderedContent = computed(() => {
  if (!syllabusContent.value) return ''
  try {
    const cleanMarkdown = stripFrontMatter(syllabusContent.value)
    return marked(cleanMarkdown)
  } catch (error) {
    console.error('Error rendering markdown:', error)
    return syllabusContent.value // Fallback to raw content
  }
})

// Generate syllabus content for preview
const generateSyllabusPreview = async () => {
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
      
      // TODO: Get actual data from previous wizard steps
      attendance_policy: '',
      grading_policy: '',
      ai_policy: '',
      textbooks: '',
      assignments: '',
      bibliography: ''
    }
    
    const response = await fetch('/api/generate-syllabus', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    })
    
    if (response.ok) {
      const responseData = await response.json()
      // API returns { success: true, data: { markdown: "...", metadata: {...} }, message: "..." }
      if (responseData.success && responseData.data) {
        if (typeof responseData.data === 'object' && responseData.data.markdown) {
          syllabusContent.value = responseData.data.markdown
        } else if (typeof responseData.data === 'string') {
          syllabusContent.value = responseData.data
        } else {
          syllabusContent.value = JSON.stringify(responseData.data, null, 2)
        }
      } else {
        syllabusContent.value = responseData.message || 'Syllabus content generated successfully'
      }
    } else {
      const errorData = await response.text()
      console.error('API Error:', response.status, response.statusText)
      syllabusContent.value = `Error generating syllabus: ${errorData}`
    }
  } catch (error) {
    console.error('Error generating syllabus:', error)
    syllabusContent.value = 'Error generating syllabus. Please try again.'
  } finally {
    loading.value = false
  }
}

// Download syllabus in different formats
const downloadSyllabus = async (format: string) => {
  generatingDownload.value = format
  try {
    // Parse semester to extract year
    const semesterParts = wizardData.value.semester.split('_')
    const year = 2000 + parseInt(semesterParts[0])
    
    const requestData = {
      schedule: scheduleItems.value || [],
      semester: wizardData.value.semester,
      year: year,
      course_id: `${wizardData.value.department} ${wizardData.value.course}`,
      instructor_name: wizardData.value.instructor,
      format: format.toLowerCase(),
      attendance_policy: '',
      grading_policy: '',
      ai_policy: '',
      textbooks: '',
      assignments: '',
      bibliography: ''
    }
    
    const response = await fetch('/api/export-syllabus', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      a.download = `${wizardData.value.department}_${wizardData.value.course}_syllabus.${format.toLowerCase()}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } else {
      const errorData = await response.json()
      console.error('Download Error:', errorData)
      alert(`Error downloading syllabus: ${errorData.error?.message || 'Please try again.'}`)
    }
  } catch (error) {
    console.error('Error downloading syllabus:', error)
    alert('Error downloading syllabus. Please try again.')
  } finally {
    generatingDownload.value = ''
  }
}

// Copy syllabus to clipboard
const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(syllabusContent.value)
    alert('Syllabus copied to clipboard!')
  } catch (error) {
    console.error('Error copying to clipboard:', error)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = syllabusContent.value
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    alert('Syllabus copied to clipboard!')
  }
}

const goBack = () => {
  router.push({ 
    name: 'class-policies',
    query: wizardData.value
  })
}

const startOver = () => {
  router.push({ name: 'home' })
}

onMounted(async () => {
  // If no wizard data, redirect to home
  if (!wizardData.value.semester || !wizardData.value.instructor) {
    router.push({ name: 'home' })
    return
  }
  
  // Generate syllabus preview
  await generateSyllabusPreview()
})
</script>

<template>
  <main class="min-h-screen bg-gray-900 py-12">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold bg-gradient-to-r from-purple-500 to-purple-700 bg-clip-text text-transparent mb-4">
          Syllabus Preview
        </h1>
        <p class="text-xl text-gray-300 max-w-2xl mx-auto">
          Review your syllabus and download in your preferred format
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

      <!-- Action Buttons -->
      <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 mb-8">
        <div class="flex flex-wrap gap-4 justify-center">
          <!-- Download Buttons -->
          <button
            @click="downloadSyllabus('DOCX')"
            :disabled="loading || generatingDownload === 'DOCX'"
            class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="generatingDownload === 'DOCX'" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="mr-2 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
            Download DOCX
          </button>

          <button
            @click="downloadSyllabus('PDF')"
            :disabled="loading || generatingDownload === 'PDF'"
            class="inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="generatingDownload === 'PDF'" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="mr-2 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
            Download PDF
          </button>

          <button
            @click="downloadSyllabus('HTML')"
            :disabled="loading || generatingDownload === 'HTML'"
            class="inline-flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="generatingDownload === 'HTML'" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="mr-2 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
            Download HTML
          </button>

          <!-- Copy to Clipboard -->
          <button
            @click="copyToClipboard"
            :disabled="loading || !syllabusContent"
            class="inline-flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="mr-2 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M8 2a1 1 0 000 2h2a1 1 0 100-2H8z"></path>
              <path d="M3 5a2 2 0 012-2 3 3 0 003 3h6a3 3 0 003-3 2 2 0 012 2v6h-4.586l1.293-1.293a1 1 0 00-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L10.414 13H15v3a2 2 0 01-2 2H5a2 2 0 01-2-2V5zM15 11.586l-3-3a1 1 0 00-1.414 1.414L11.586 11H9a1 1 0 100 2h2.586l-1 1a1 1 0 001.414 1.414l3-3z"></path>
            </svg>
            Copy to Clipboard
          </button>
        </div>
      </div>
      
      <!-- Syllabus Content -->
      <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div class="mb-6">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Generated Syllabus</h2>
          <p class="text-gray-600">Preview your syllabus content below</p>
        </div>

        <div class="border border-gray-200 rounded-lg p-6 bg-gray-50">
          <div v-if="loading" class="text-center py-12">
            <svg class="animate-spin mx-auto h-12 w-12 text-purple-600 mb-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="text-gray-600">Generating syllabus preview...</p>
          </div>
          
          <div v-else-if="syllabusContent" class="bg-white p-6 rounded border overflow-auto max-h-96">
            <div 
              v-html="renderedContent" 
              class="prose prose-sm max-w-none 
                     prose-headings:text-gray-900 prose-headings:font-bold 
                     prose-h1:text-xl prose-h1:mb-4 prose-h1:mt-6
                     prose-h2:text-lg prose-h2:mb-3 prose-h2:mt-5
                     prose-h3:text-base prose-h3:mb-2 prose-h3:mt-4
                     prose-p:text-gray-800 prose-p:leading-relaxed prose-p:mb-3
                     prose-strong:text-gray-900 prose-strong:font-semibold
                     prose-ul:text-gray-800 prose-li:mb-1
                     prose-table:border-collapse prose-table:w-full
                     prose-th:border prose-th:p-2 prose-th:bg-gray-50
                     prose-td:border prose-td:p-2"
            ></div>
          </div>
          
          <div v-else class="text-center py-8">
            <p class="text-gray-500">No syllabus content available</p>
          </div>
        </div>

        <!-- Progress Indicator -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100 mt-8">
          <div class="flex items-center justify-between text-sm font-medium text-gray-700 mb-3">
            <span class="text-purple-600">Step 7 of 7</span>
            <span>Syllabus Preview</span>
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
            Back to Class Policies
          </button>
          
          <button
            type="button"
            @click="startOver"
            class="inline-flex items-center px-6 py-3 border border-gray-300 shadow-sm text-base font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition duration-200"
          >
            <svg class="mr-2 -ml-1 w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            Start New Syllabus
          </button>
        </div>
      </div>
    </div>
  </main>
</template>
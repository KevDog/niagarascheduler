<script setup lang="ts">
import { onMounted } from 'vue'
import CourseSelectionForm from '@/components/CourseSelectionForm.vue'
import { useApiData } from '@/composables/useApiData'
import { useNavigation } from '@/composables/useNavigation'

const { fetchConfig, fetchDepartments } = useApiData()
const { navigateToInstructorInfo } = useNavigation()

const handleFormSubmit = (formData: any) => {
  navigateToInstructorInfo(formData)
}

// Load initial data on mount
onMounted(() => {
  fetchConfig()
  fetchDepartments()
})
</script>

<template>
  <main class="min-h-screen bg-gray-900 py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold bg-gradient-to-r from-purple-500 to-purple-700 bg-clip-text text-transparent mb-4">
          Purple Eagle Syllabus Wizard
        </h1>
        <p class="text-xl text-gray-300 max-w-2xl mx-auto">
          Create professional syllabi with our easy-to-use wizard
        </p>
      </div>
      
      <!-- Course Selection Form -->
      <CourseSelectionForm @submit="handleFormSubmit" />
    </div>
  </main>
</template>
<script setup lang="ts">
import { computed, onMounted, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { Listbox, ListboxButton, ListboxOption, ListboxOptions } from '@headlessui/vue'
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/vue/20/solid'
import { useCourseSelection } from '@/composables/useCourseSelection'
import { useApiStore } from '@/stores/api'
import ProgressIndicator from './ProgressIndicator.vue'

interface Emits {
  (e: 'submit', formData: any): void
}

const emit = defineEmits<Emits>()

const { 
  selectedSemester,
  instructorName,
  selectedDepartment,
  selectedCourse,
  selectedOffering,
  canProceed,
  courses,
  offerings,
  getFormData
} = useCourseSelection()

// Access store directly with proper reactivity
const store = useApiStore()
const { departments, semesters, loading } = storeToRefs(store)
const { fetchDepartments, fetchCourses, fetchOfferings } = store

// Ensure departments are fetched when component mounts
onMounted(async () => {
  console.log('Fetching departments on mount...')
  
  // Wait for next tick to ensure Pinia store is installed
  await nextTick()
  
  await fetchDepartments()
  console.log('Departments after mount:', departments.value?.length || 0)
  
  // If still 0, try again after a short delay
  if (!departments.value || departments.value.length === 0) {
    console.log('Store not ready, trying again...')
    setTimeout(async () => {
      await fetchDepartments()
      console.log('Departments after retry:', departments.value?.length || 0)
    }, 100)
  }
})

const handleSubmit = () => {
  if (canProceed.value) {
    emit('submit', getFormData())
  }
}

// Filter offerings by selected course
const filteredOfferings = computed(() => {
  if (!selectedCourse.value || !offerings.value) return []
  
  const filtered = offerings.value.filter(offering => {
    const courseNumber = selectedCourse.value
    return offering.course_number === courseNumber
  })
  
  console.log('Filtering offerings:', {
    selectedCourse: selectedCourse.value,
    totalOfferings: offerings.value.length,
    filteredCount: filtered.length
  })
  
  return filtered
})
</script>

<template>
  <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
    <div class="mb-8">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">Create New Syllabus</h2>
      <p class="text-gray-600">Enter your information to get started with your professional syllabus</p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-6">
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
            class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
          />
        </div>
      </div>

      <!-- Semester Selection -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Semester <span class="text-red-500">*</span>
        </label>
        <Listbox v-model="selectedSemester" :disabled="loading">
          <div class="relative">
            <ListboxButton
              class="relative w-full cursor-default rounded-lg bg-white py-3 pl-4 pr-10 text-left border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition duration-200 disabled:opacity-50"
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
                      active ? 'bg-purple-100 text-purple-900' : 'text-gray-900',
                      'relative cursor-default select-none py-3 pl-10 pr-4',
                    ]"
                  >
                    <span :class="[selected ? 'font-medium' : 'font-normal', 'block truncate']">
                      {{ semester.display }}
                    </span>
                    <span
                      v-if="selected"
                      class="absolute inset-y-0 left-0 flex items-center pl-3 text-purple-600"
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

      <!-- Department Selection -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Department <span class="text-red-500">*</span>
        </label>
        <Listbox v-model="selectedDepartment" :disabled="!selectedSemester || loading">
          <div class="relative">
            <ListboxButton
              class="relative w-full cursor-default rounded-lg bg-white py-3 pl-4 pr-10 text-left border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition duration-200 disabled:opacity-50"
            >
              <span class="block truncate text-gray-900">
                {{ selectedDepartment ? `${selectedDepartment} - ${departments.find(d => d.code === selectedDepartment)?.name}` : (selectedSemester ? 'Select a department' : 'Select semester first') }}
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
                      active ? 'bg-purple-100 text-purple-900' : 'text-gray-900',
                      'relative cursor-default select-none py-3 pl-10 pr-4',
                    ]"
                  >
                    <span :class="[selected ? 'font-medium' : 'font-normal', 'block truncate']">
                      {{ dept.code }} - {{ dept.name }}
                    </span>
                    <span
                      v-if="selected"
                      class="absolute inset-y-0 left-0 flex items-center pl-3 text-purple-600"
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
              class="relative w-full cursor-default rounded-lg bg-white py-3 pl-4 pr-10 text-left border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition duration-200 disabled:opacity-50"
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
                      active ? 'bg-purple-100 text-purple-900' : 'text-gray-900',
                      'relative cursor-default select-none py-3 pl-10 pr-4',
                    ]"
                  >
                    <span :class="[selected ? 'font-medium' : 'font-normal', 'block truncate']">
                      {{ selectedDepartment }} {{ course.number }} - {{ course.title }}
                    </span>
                    <span
                      v-if="selected"
                      class="absolute inset-y-0 left-0 flex items-center pl-3 text-purple-600"
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
        <Listbox v-model="selectedOffering" :disabled="!selectedCourse || loading || filteredOfferings.length === 0">
          <div class="relative">
            <ListboxButton
              class="relative w-full cursor-default rounded-lg bg-white py-3 pl-4 pr-10 text-left border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition duration-200 disabled:opacity-50"
            >
              <span class="block truncate text-gray-900">
                {{ selectedOffering ? 
                  `${filteredOfferings.find(o => o.number === selectedOffering)?.section || selectedOffering.substring(selectedOffering.length - 1)} - ${filteredOfferings.find(o => o.number === selectedOffering)?.days && filteredOfferings.find(o => o.number === selectedOffering)?.start_time ? 
                    `${filteredOfferings.find(o => o.number === selectedOffering)?.days} ${filteredOfferings.find(o => o.number === selectedOffering)?.start_time}-${filteredOfferings.find(o => o.number === selectedOffering)?.end_time}` : 
                    `${filteredOfferings.find(o => o.number === selectedOffering)?.name} (${filteredOfferings.find(o => o.number === selectedOffering)?.credits} credits)`}`
                  : (selectedCourse ? (filteredOfferings.length > 0 ? 'Select a section' : 'No sections available') : 'Select course first') }}
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
                  v-for="offering in filteredOfferings"
                  :key="offering.number"
                  :value="offering.number"
                  as="template"
                >
                  <li
                    :class="[
                      active ? 'bg-purple-100 text-purple-900' : 'text-gray-900',
                      'relative cursor-default select-none py-3 pl-10 pr-4',
                    ]"
                  >
                    <span :class="[selected ? 'font-medium' : 'font-normal', 'block truncate']">
                      {{ offering.section || offering.number.substring(offering.number.length - 1) }} - 
                      {{ offering.days && offering.start_time ? `${offering.days} ${offering.start_time}-${offering.end_time}` : `${offering.name} (${offering.credits} credits)` }}
                    </span>
                    <span
                      v-if="selected"
                      class="absolute inset-y-0 left-0 flex items-center pl-3 text-purple-600"
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
      <ProgressIndicator 
        :current-step="1" 
        :total-steps="4" 
        step-label="Basic Information" 
      />

      <!-- Continue Button -->
      <button
        type="submit"
        :disabled="!canProceed || loading"
        class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-base font-medium rounded-lg text-white transition duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
        :class="canProceed && !loading
          ? 'bg-gradient-to-r from-purple-500 to-purple-700 hover:from-purple-600 hover:to-purple-800 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5' 
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
</template>
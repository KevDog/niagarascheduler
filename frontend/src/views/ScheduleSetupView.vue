<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Listbox, ListboxButton, ListboxOption, ListboxOptions } from '@headlessui/vue'
import { CheckIcon, ChevronUpDownIcon, ClockIcon, CalendarIcon } from '@heroicons/vue/20/solid'

const route = useRoute()
const router = useRouter()

// Get data from query parameters (passed from Step 1)
const wizardData = ref({
  semester: route.query.semester as string || '',
  instructor: route.query.instructor as string || '',
  department: route.query.department as string || '',
  course: route.query.course as string || '',
  offering: route.query.offering as string || '',
})

// Schedule building data
const scheduleData = ref({
  meetingTimes: '',
  location: '',
  officeHours: '',
  finalExamDate: '',
  holidays: [] as string[],
  importantDates: [] as { date: string, description: string }[]
})

const loading = ref(false)
const selectedHolidays = ref<string[]>([])

// Available holidays for the semester
const availableHolidays = ref([
  'Labor Day',
  'Indigenous Peoples Day',
  'Thanksgiving Break',
  'Winter Break',
  'Martin Luther King Jr. Day',
  'Presidents Day',
  'Spring Break',
  'Good Friday',
  'Memorial Day'
])

// Important dates for the academic year
const importantDates = ref([
  { date: '2024-09-02', description: 'Labor Day - No Classes' },
  { date: '2024-10-14', description: 'Indigenous Peoples Day - No Classes' },
  { date: '2024-11-28', description: 'Thanksgiving Break Begins' },
  { date: '2024-12-02', description: 'Classes Resume' },
  { date: '2024-12-16', description: 'Final Exams Begin' },
  { date: '2025-01-13', description: 'Spring Semester Begins' },
  { date: '2025-03-10', description: 'Spring Break Begins' },
  { date: '2025-03-17', description: 'Classes Resume' },
  { date: '2025-04-18', description: 'Good Friday - No Classes' },
  { date: '2025-05-12', description: 'Final Exams Begin' }
])

// Computed properties
const canProceed = computed(() => {
  return scheduleData.value.meetingTimes && scheduleData.value.location
})

// Methods
const generateSchedule = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/generate-schedule', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...wizardData.value,
        ...scheduleData.value,
        holidays: selectedHolidays.value,
        importantDates: scheduleData.value.importantDates
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      console.log('Schedule generated:', data)
      // Navigate to next step (syllabus content)
      router.push({
        name: 'syllabus-content',
        query: {
          ...wizardData.value,
          ...scheduleData.value,
          scheduleId: data.scheduleId
        }
      })
    }
  } catch (error) {
    console.error('Error generating schedule:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push({ name: 'home' })
}

const addImportantDate = () => {
  scheduleData.value.importantDates.push({ date: '', description: '' })
}

const removeImportantDate = (index: number) => {
  scheduleData.value.importantDates.splice(index, 1)
}

onMounted(() => {
  // If no wizard data, redirect to home
  if (!wizardData.value.semester || !wizardData.value.instructor) {
    router.push({ name: 'home' })
  }
})
</script>

<template>
  <main class="min-h-screen bg-gray-900 py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold bg-gradient-to-r from-purple-500 to-purple-700 bg-clip-text text-transparent mb-4">
          Schedule Setup
        </h1>
        <p class="text-xl text-gray-300 max-w-2xl mx-auto">
          Configure your course schedule and important dates
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
      
      <!-- Schedule Configuration Form -->
      <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Schedule Configuration</h2>
          <p class="text-gray-300">Set up your course schedule and important dates</p>
        </div>

        <form @submit.prevent="generateSchedule" class="space-y-6">
          <!-- Meeting Times -->
          <div>
            <label for="meetingTimes" class="block text-sm font-medium text-gray-700 mb-2">
              <ClockIcon class="inline w-4 h-4 mr-2" />
              Meeting Times <span class="text-red-500">*</span>
            </label>
            <input
              id="meetingTimes"
              v-model="scheduleData.meetingTimes"
              type="text"
              required
              placeholder="e.g., MW 10:30AM-11:50AM"
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            />
          </div>

          <!-- Location -->
          <div>
            <label for="location" class="block text-sm font-medium text-gray-700 mb-2">
              Location <span class="text-red-500">*</span>
            </label>
            <input
              id="location"
              v-model="scheduleData.location"
              type="text"
              required
              placeholder="e.g., Dunleavy Hall 201"
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            />
          </div>

          <!-- Office Hours -->
          <div>
            <label for="officeHours" class="block text-sm font-medium text-gray-700 mb-2">
              Office Hours
            </label>
            <input
              id="officeHours"
              v-model="scheduleData.officeHours"
              type="text"
              placeholder="e.g., TTH 2:00PM-4:00PM"
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            />
          </div>

          <!-- Final Exam Date -->
          <div>
            <label for="finalExamDate" class="block text-sm font-medium text-gray-700 mb-2">
              <CalendarIcon class="inline w-4 h-4 mr-2" />
              Final Exam Date
            </label>
            <input
              id="finalExamDate"
              v-model="scheduleData.finalExamDate"
              type="date"
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
            />
          </div>

          <!-- Holiday Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Holidays (No Classes)
            </label>
            <Listbox v-model="selectedHolidays" multiple>
              <div class="relative">
                <ListboxButton
                  class="relative w-full cursor-default rounded-lg bg-white py-3 pl-4 pr-10 text-left border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition duration-200"
                >
                  <span class="block truncate text-gray-900">
                    {{ selectedHolidays.length > 0 ? `${selectedHolidays.length} holidays selected` : 'Select holidays' }}
                  </span>
                  <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <ChevronUpDownIcon class="h-5 w-5 text-gray-400" />
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
                      v-for="holiday in availableHolidays"
                      :key="holiday"
                      :value="holiday"
                      as="template"
                    >
                      <li
                        :class="[
                          active ? 'bg-purple-100 text-purple-900' : 'text-gray-900',
                          'relative cursor-default select-none py-3 pl-10 pr-4',
                        ]"
                      >
                        <span :class="[selected ? 'font-medium' : 'font-normal', 'block truncate']">
                          {{ holiday }}
                        </span>
                        <span
                          v-if="selected"
                          class="absolute inset-y-0 left-0 flex items-center pl-3 text-purple-600"
                        >
                          <CheckIcon class="h-5 w-5" />
                        </span>
                      </li>
                    </ListboxOption>
                  </ListboxOptions>
                </transition>
              </div>
            </Listbox>
          </div>

          <!-- Important Dates -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Additional Important Dates
            </label>
            <div class="space-y-3">
              <div
                v-for="(date, index) in scheduleData.importantDates"
                :key="index"
                class="flex gap-3 items-center"
              >
                <input
                  v-model="date.date"
                  type="date"
                  class="flex-1 rounded-lg border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-purple-600"
                />
                <input
                  v-model="date.description"
                  type="text"
                  placeholder="Description"
                  class="flex-2 rounded-lg border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-purple-600"
                />
                <button
                  type="button"
                  @click="removeImportantDate(index)"
                  class="text-red-600 hover:text-red-800"
                >
                  Remove
                </button>
              </div>
              <button
                type="button"
                @click="addImportantDate"
                class="text-purple-600 hover:text-blue-800 font-medium"
              >
                + Add Important Date
              </button>
            </div>
          </div>

          <!-- Progress Indicator -->
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
            <div class="flex items-center justify-between text-sm font-medium text-gray-700 mb-3">
              <span class="text-purple-600">Step 2 of 4</span>
              <span>Schedule Setup</span>
            </div>
            <div class="w-full bg-purple-100 rounded-full h-2.5 shadow-inner">
              <div class="bg-gradient-to-r from-purple-400 to-purple-600 h-2.5 rounded-full w-1/2 shadow-sm transition-all duration-300"></div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-4 pt-6">
            <button
              type="button"
              @click="goBack"
              class="flex-1 py-3 px-4 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-900 transition duration-200"
            >
              Back
            </button>
            <button
              type="submit"
              :disabled="!canProceed || loading"
              class="flex-1 group relative flex justify-center py-3 px-4 border border-transparent text-base font-medium rounded-lg text-white transition duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
              :class="canProceed && !loading
                ? 'bg-gradient-to-r from-purple-500 to-purple-700 hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5' 
                : 'bg-gray-300 cursor-not-allowed'"
            >
              <span v-if="loading" class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating Schedule...
              </span>
              <span v-else class="flex items-center">
                Generate Schedule
                <svg class="ml-2 -mr-1 w-5 h-5 transition-transform group-hover:translate-x-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </main>
</template>
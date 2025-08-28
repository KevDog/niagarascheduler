<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ClockIcon, CalendarIcon } from '@heroicons/vue/20/solid'
import { useApiStore } from '@/stores/api'
import { useScheduleStore } from '@/stores/schedule'
import { storeToRefs } from 'pinia'

const route = useRoute()
const router = useRouter()

// Access Pinia stores
const apiStore = useApiStore()
const scheduleStore = useScheduleStore()
const { offerings } = storeToRefs(apiStore)
const { 
  scheduleItems, 
  classDates, 
  academicEvents, 
  calendarLoading, 
  dateNotes,
  selectedDate,
  showNotesModal,
  tempNote,
  characterCount,
  characterLimit,
  isOverLimit,
  charactersRemaining,
  characterCountText,
  characterCountColor,
  userImportantDates,
  cancelledClasses
} = storeToRefs(scheduleStore)

// Get data from query parameters (passed from Step 1)
const wizardData = ref({
  semester: route.query.semester as string || '',
  instructor: route.query.instructor as string || '',
  department: route.query.department as string || '',
  course: route.query.course as string || '',
  offering: route.query.offering as string || '',
})

// Find the selected offering from the store
const selectedOffering = computed(() => {
  if (!wizardData.value.offering || !offerings.value.length) return null
  return offerings.value.find(offering => offering.number === wizardData.value.offering)
})

// Schedule building data - will be populated from offering data
const scheduleData = ref({
  meetingDays: [] as string[],
  startTime: '',
  endTime: '',
  location: '',
  officeHours: '',
  finalExamDate: '',
  importantDates: [] as { date: string, description: string, type: 'class' | 'holiday' | 'event' | 'other' }[]
})

// Available meeting days
const meetingDayOptions = [
  { value: 'M', label: 'Monday (M)' },
  { value: 'T', label: 'Tuesday (T)' },
  { value: 'W', label: 'Wednesday (W)' },
  { value: 'R', label: 'Thursday (Th)' },
  { value: 'F', label: 'Friday (F)' }
]

// Available types for important dates
const dateTypes = [
  { value: 'class', label: 'Class Meeting', color: 'bg-purple-50 text-purple-800 border-purple-200' },
  { value: 'holiday', label: 'Holiday', color: 'bg-red-50 text-red-800 border-red-200' },
  { value: 'event', label: 'Academic Event', color: 'bg-amber-50 text-amber-800 border-amber-200' },
  { value: 'other', label: 'Other', color: 'bg-gray-50 text-gray-800 border-gray-200' }
]


const loading = ref(false)

// Computed properties
const canProceed = computed(() => {
  return scheduleData.value.meetingDays.length > 0 && 
         scheduleData.value.startTime && 
         scheduleData.value.endTime && 
         scheduleData.value.location
})

const formattedMeetingTimes = computed(() => {
  if (scheduleData.value.meetingDays.length > 0 && scheduleData.value.startTime && scheduleData.value.endTime) {
    // Format days string properly (convert R to Th for display)
    let daysString = scheduleData.value.meetingDays
      .map(day => day === 'R' ? 'Th' : day)
      .join('')
    
    // Convert times back to 12-hour format for display
    const formatTime = (time24: string) => {
      const [hours, minutes] = time24.split(':')
      const hour24 = parseInt(hours, 10)
      const hour12 = hour24 === 0 ? 12 : hour24 > 12 ? hour24 - 12 : hour24
      const ampm = hour24 >= 12 ? 'PM' : 'AM'
      return `${hour12}:${minutes}${ampm}`
    }
    
    const startTime12 = formatTime(scheduleData.value.startTime)
    const endTime12 = formatTime(scheduleData.value.endTime)
    
    return `${daysString} ${startTime12} - ${endTime12}`
  }
  return ''
})

const validImportantDatesCount = computed(() => {
  return scheduleData.value.importantDates.filter(date => 
    date.date && date.type && date.description.trim()
  ).length
})

// Generate class meeting dates based on schedule
const generateClassDates = async () => {
  if (!wizardData.value.semester || scheduleData.value.meetingDays.length === 0) {
    return
  }
  
  const meetingDays = scheduleData.value.meetingDays.join('')
  await scheduleStore.generateClassDates(wizardData.value.semester, meetingDays)
}

// Watch for changes in meeting days to regenerate class dates
watch(() => scheduleData.value.meetingDays, (newValue) => {
  if (newValue.length > 0) {
    generateClassDates()
  }
}, { immediate: false, deep: true })

// Initialize meeting data from the selected offering
const initializeFromOffering = async () => {
  if (selectedOffering.value && selectedOffering.value.days && selectedOffering.value.start_time && selectedOffering.value.end_time) {
    const offering = selectedOffering.value
    
    // Parse meeting days from offering.days (e.g., "TTH" -> ["T", "R"])
    const daysString = offering.days
    const parsedDays: string[] = []
    
    for (let i = 0; i < daysString.length; i++) {
      const char = daysString[i]
      if (char === 'T' && i < daysString.length - 1 && daysString[i + 1] === 'H') {
        parsedDays.push('R') // Thursday
        i++ // Skip the H
      } else if (char === 'M') {
        parsedDays.push('M')
      } else if (char === 'T') {
        parsedDays.push('T')
      } else if (char === 'W') {
        parsedDays.push('W')
      } else if (char === 'R') {
        parsedDays.push('R')
      } else if (char === 'F') {
        parsedDays.push('F')
      }
    }
    
    scheduleData.value.meetingDays = parsedDays
    scheduleData.value.startTime = convertTo24Hour(offering.start_time)
    scheduleData.value.endTime = convertTo24Hour(offering.end_time)
    
    // Generate class dates immediately after setting meeting data
    await generateClassDates()
  }
}

// Watch for selectedOffering to become available and initialize
watch(selectedOffering, async (newOffering) => {
  if (newOffering && !scheduleData.value.meetingDays.length) {
    await initializeFromOffering()
  }
}, { immediate: true })

// Methods
const saveScheduleData = async () => {
  loading.value = true
  try {
    // Store schedule data locally (already managed by Pinia store)
    console.log('Schedule data configured:', scheduleData.value)
    
    // Navigate to next step (course content)
    router.push({
      name: 'course-content',
      query: wizardData.value
    })
  } catch (error) {
    console.error('Error navigating to policies:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push({ name: 'home' })
}

const addImportantDate = () => {
  scheduleData.value.importantDates.push({ date: '', description: '', type: 'class' })
}

const removeImportantDate = (index: number) => {
  scheduleData.value.importantDates.splice(index, 1)
}

// Helper function to convert 12-hour time format to 24-hour format
const convertTo24Hour = (time12h: string): string => {
  const [time, modifier] = time12h.split(/([AP]M)/)
  let [hours, minutes] = time.split(':')
  
  if (hours === '12') {
    hours = '00'
  }
  
  if (modifier === 'PM') {
    hours = String(parseInt(hours, 10) + 12)
  }
  
  return `${hours.padStart(2, '0')}:${minutes || '00'}`
}

const saveImportantDatesToSchedule = () => {
  // Filter out incomplete entries - must have date, type, AND description
  const validDates = scheduleData.value.importantDates.filter(date => 
    date.date && date.type && date.description.trim()
  )
  
  if (validDates.length > 0) {
    // Save to the schedule store
    scheduleStore.setUserImportantDates(validDates)
    console.log('Saved important dates to schedule:', validDates)
    
    // Clear the form by removing all entries
    scheduleData.value.importantDates = []
    
    // Optional: Show success feedback (you could add a toast notification here)
    console.log(`Successfully saved ${validDates.length} important date(s) to schedule`)
  } else {
    console.log('No complete important dates to save (missing date, type, or description)')
  }
}

// Date notes functionality - using store actions
const toggleDateNotes = (date: string) => {
  scheduleStore.openNotesModal(date)
}

const saveNotes = () => {
  scheduleStore.saveNote(
    wizardData.value.semester,
    wizardData.value.department,
    wizardData.value.course
  )
}

const cancelNotes = () => {
  scheduleStore.closeNotesModal()
}

const deleteScheduleDate = (dateToDelete: string, event: Event) => {
  // Stop the click event from bubbling up to the parent (which would open the notes modal)
  event.stopPropagation()
  
  // Remove from user important dates
  scheduleStore.removeUserImportantDate(dateToDelete)
  console.log('Removed date from schedule:', dateToDelete)
}

const toggleClassCancellation = (date: string, event: Event) => {
  // Stop the click event from bubbling up to the parent (which would open the notes modal)
  event.stopPropagation()
  
  // Toggle the cancellation status
  scheduleStore.toggleClassCancellation(date)
  const isCancelled = scheduleStore.isClassCancelled(date)
  console.log(`Class on ${date} is now ${isCancelled ? 'cancelled' : 'scheduled'}`)
}

onMounted(async () => {
  // If no wizard data, redirect to home
  if (!wizardData.value.semester || !wizardData.value.instructor) {
    router.push({ name: 'home' })
    return
  }
  
  // Fetch offerings if not already loaded
  if (!offerings.value.length && wizardData.value.semester && wizardData.value.department) {
    console.log('Fetching offerings for schedule setup:', wizardData.value.semester, wizardData.value.department)
    await apiStore.fetchOfferings(wizardData.value.semester, wizardData.value.department)
  }
  
  // Load notes from storage
  if (wizardData.value.semester && wizardData.value.department && wizardData.value.course) {
    scheduleStore.loadNotesFromStorage(
      wizardData.value.semester,
      wizardData.value.department, 
      wizardData.value.course
    )
  }
  
  // Initialize meeting data from offering (after API data loads)
  initializeFromOffering()
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

        <form @submit.prevent="saveScheduleData" class="space-y-6">
          <!-- Meeting Schedule -->
          <div class="space-y-4">
            <h3 class="text-lg font-medium text-gray-900 flex items-center">
              <ClockIcon class="inline w-5 h-5 mr-2 text-purple-600" />
              Meeting Schedule <span class="text-red-500">*</span>
              <span v-if="selectedOffering" class="text-xs text-gray-500 ml-2">(from selected section)</span>
            </h3>

            <!-- Meeting Days -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-3">
                Meeting Days <span class="text-red-500">*</span>
              </label>
              <div class="grid grid-cols-5 gap-2">
                <label
                  v-for="day in meetingDayOptions"
                  :key="day.value"
                  class="flex items-center justify-center p-3 border rounded-lg cursor-pointer transition-all"
                  :class="{
                    'border-purple-300 bg-purple-50 text-purple-700 font-medium': scheduleData.meetingDays.includes(day.value),
                    'border-gray-300 bg-white text-gray-700 hover:border-purple-200 hover:bg-purple-25': !scheduleData.meetingDays.includes(day.value)
                  }"
                >
                  <input
                    type="checkbox"
                    :value="day.value"
                    v-model="scheduleData.meetingDays"
                    class="sr-only"
                  />
                  <span class="text-sm">{{ day.label }}</span>
                </label>
              </div>
            </div>

            <!-- Start and End Times -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="startTime" class="block text-sm font-medium text-gray-700 mb-2">
                  Start Time <span class="text-red-500">*</span>
                </label>
                <input
                  id="startTime"
                  v-model="scheduleData.startTime"
                  type="time"
                  required
                  class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
                />
              </div>
              <div>
                <label for="endTime" class="block text-sm font-medium text-gray-700 mb-2">
                  End Time <span class="text-red-500">*</span>
                </label>
                <input
                  id="endTime"
                  v-model="scheduleData.endTime"
                  type="time"
                  required
                  class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 transition duration-200"
                />
              </div>
            </div>

            <!-- Meeting Times Preview -->
            <div v-if="formattedMeetingTimes" class="p-3 bg-gray-50 rounded-lg">
              <p class="text-sm text-gray-600">
                <strong>Preview:</strong> {{ formattedMeetingTimes }}
              </p>
            </div>
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


          <!-- Important Dates -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Additional Important Dates
              <span class="text-xs text-gray-500 ml-2">(will appear in your class schedule)</span>
            </label>
            <p class="text-xs text-gray-600 mb-3">
              Fill out all fields (date, type, and description) before saving to schedule.
            </p>
            <div class="space-y-4">
              <div class="flex gap-2">
                <button
                  type="button"
                  @click="addImportantDate"
                  class="text-purple-600 hover:text-purple-800 font-medium px-3 py-2 border border-purple-300 rounded-lg hover:bg-purple-50 transition-colors"
                >
                  + Add Important Date
                </button>
                
                <button
                  v-if="scheduleData.importantDates.length > 0"
                  type="button"
                  @click="saveImportantDatesToSchedule"
                  :disabled="validImportantDatesCount === 0"
                  :class="{
                    'bg-purple-600 text-white hover:bg-purple-700': validImportantDatesCount > 0,
                    'bg-gray-400 text-gray-200 cursor-not-allowed': validImportantDatesCount === 0
                  }"
                  class="font-medium px-4 py-2 rounded-lg transition-colors"
                >
                  Save to Schedule
                  <span v-if="validImportantDatesCount > 0" class="ml-1 text-xs bg-purple-500 px-2 py-1 rounded-full">
                    {{ validImportantDatesCount }}
                  </span>
                </button>
              </div>
              
              <div
                v-for="(date, index) in scheduleData.importantDates"
                :key="index"
                class="flex gap-2 items-center bg-gray-50 p-3 rounded-lg"
              >
                <input
                  v-model="date.date"
                  type="date"
                  class="flex-1 rounded-lg border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-purple-600"
                />
                <select
                  v-model="date.type"
                  class="flex-1 rounded-lg border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-purple-600"
                >
                  <option v-for="type in dateTypes" :key="type.value" :value="type.value">
                    {{ type.label }}
                  </option>
                </select>
                <input
                  v-model="date.description"
                  type="text"
                  placeholder="Description"
                  class="flex-2 rounded-lg border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-purple-600"
                />
                <button
                  type="button"
                  @click="removeImportantDate(index)"
                  class="text-red-600 hover:text-red-800 px-2 py-1"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>

          <!-- Class Schedule with Holidays -->
          <div v-if="scheduleItems.length > 0 || calendarLoading" class="space-y-6">
            <!-- Class Meeting Dates with Holidays -->
            <div v-if="!calendarLoading && scheduleItems.length > 0" class="bg-white rounded-xl p-6 border border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">
                <CalendarIcon class="inline w-5 h-5 mr-2 text-purple-600" />
                Class Schedule ({{ classDates.length }} classes, {{ scheduleItems.filter(item => item.type === 'holiday').length }} holidays)
              </h3>
              <div class="space-y-3 max-h-80 overflow-y-auto">
                <div
                  v-for="item in scheduleItems" 
                  :key="`${item.date}-${item.type}`"
                  :class="{
                    'bg-purple-50 text-purple-800 border border-purple-200': item.type === 'class' && !scheduleStore.isClassCancelled(item.date),
                    'bg-gray-100 text-gray-500 border border-gray-300 opacity-75': item.type === 'class' && scheduleStore.isClassCancelled(item.date),
                    'bg-red-50 text-red-800 border border-red-200': item.type === 'holiday',
                    'bg-amber-50 text-amber-800 border border-amber-200': item.type === 'event',
                    'bg-gray-50 text-gray-800 border border-gray-200': item.type === 'other'
                  }"
                  class="flex items-center justify-between px-4 py-3 rounded-lg w-full cursor-pointer hover:opacity-80 transition-opacity"
                  @click="toggleDateNotes(item.date)"
                >
                  <div class="flex items-center space-x-3">
                    <div class="text-base font-medium">
                      {{ scheduleStore.parseDate(item.date).toLocaleDateString('en-US', { 
                        weekday: 'short', 
                        month: 'short', 
                        day: 'numeric' 
                      }) }}
                    </div>
                    <div class="text-sm opacity-75">
                      <span v-if="item.type === 'class'">
                        <span v-if="scheduleStore.isClassCancelled(item.date)" class="line-through">Class Meeting</span>
                        <span v-else>Class Meeting</span>
                        <span v-if="scheduleStore.isClassCancelled(item.date)" class="ml-2 text-red-600 font-medium">CANCELLED</span>
                      </span>
                      <span v-else-if="item.type === 'holiday'">🎉 {{ item.name || 'Holiday' }}</span>
                      <span v-else-if="item.type === 'event'">📅 {{ item.name }}</span>
                      <span v-else-if="item.type === 'other'">📌 {{ item.name }}</span>
                      <span v-else>{{ item.name }}</span>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <div v-if="scheduleStore.hasNoteForDate(item.date)" class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      📝 Notes
                    </div>
                    <!-- Cancel/Uncancel button for class meetings -->
                    <button
                      type="button"
                      v-if="item.type === 'class'"
                      @click="toggleClassCancellation(item.date, $event)"
                      :class="{
                        'text-red-500 hover:text-red-700 hover:bg-red-50 border-red-200': !scheduleStore.isClassCancelled(item.date),
                        'text-green-500 hover:text-green-700 hover:bg-green-50 border-green-200': scheduleStore.isClassCancelled(item.date)
                      }"
                      class="flex items-center space-x-1 px-2 py-1 rounded border text-xs font-medium transition-colors"
                      :title="scheduleStore.isClassCancelled(item.date) ? 'Restore class' : 'Cancel class'"
                    >
                      <svg v-if="!scheduleStore.isClassCancelled(item.date)" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                      <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                      </svg>
                      <span v-if="!scheduleStore.isClassCancelled(item.date)">Cancel</span>
                      <span v-else>Restore</span>
                    </button>
                    <!-- Delete button for user-added important dates only -->
                    <button
                      type="button"
                      v-if="item.eventType === 'user_defined'"
                      @click="deleteScheduleDate(item.date, $event)"
                      class="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50 transition-colors"
                      title="Delete this date"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1-1H9a1 1 0 00-1 1v3M4 7h16"></path>
                      </svg>
                    </button>
                    <div class="text-xs text-gray-400">
                      Click to add notes
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Summary -->
              <div class="mt-4 flex flex-wrap gap-4 text-sm">
                <div class="flex items-center">
                  <div class="w-3 h-3 bg-purple-200 rounded-full mr-2"></div>
                  <span class="text-gray-600">
                    Class meetings ({{ classDates.length }})
                    <span v-if="cancelledClasses.size > 0" class="ml-2 text-red-600 text-xs">
                      - {{ cancelledClasses.size }} cancelled
                    </span>
                  </span>
                </div>
                <div class="flex items-center" v-if="scheduleItems.filter(item => item.type === 'holiday').length > 0">
                  <div class="w-3 h-3 bg-red-200 rounded-full mr-2"></div>
                  <span class="text-gray-600">Holidays ({{ scheduleItems.filter(item => item.type === 'holiday').length }})</span>
                </div>
                <div class="flex items-center" v-if="scheduleItems.filter(item => item.type === 'event').length > 0">
                  <div class="w-3 h-3 bg-amber-200 rounded-full mr-2"></div>
                  <span class="text-gray-600">Academic events ({{ scheduleItems.filter(item => item.type === 'event').length }})</span>
                </div>
                <div class="flex items-center" v-if="scheduleItems.filter(item => item.type === 'other').length > 0">
                  <div class="w-3 h-3 bg-gray-200 rounded-full mr-2"></div>
                  <span class="text-gray-600">Other important dates ({{ scheduleItems.filter(item => item.type === 'other').length }})</span>
                </div>
                <div class="flex items-center" v-if="scheduleItems.filter(item => item.eventType === 'user_defined').length > 0">
                  <div class="w-3 h-3 bg-blue-200 rounded-full mr-2"></div>
                  <span class="text-gray-600">User-added dates ({{ scheduleItems.filter(item => item.eventType === 'user_defined').length }}) 
                    <span class="text-xs text-gray-400 ml-1">- click 🗑️ to delete</span>
                  </span>
                </div>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="calendarLoading" class="bg-white rounded-xl p-6 border border-gray-200 text-center">
              <div class="animate-spin h-6 w-6 border-2 border-purple-600 border-t-transparent rounded-full mx-auto mb-2"></div>
              <p class="text-gray-600">Generating class dates...</p>
            </div>
          </div>

          <!-- Progress Indicator -->
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
            <div class="flex items-center justify-between text-sm font-medium text-gray-700 mb-3">
              <span class="text-purple-600">Step 2 of 5</span>
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
                Saving Schedule...
              </span>
              <span v-else class="flex items-center">
                Course Content
                <svg class="ml-2 -mr-1 w-5 h-5 transition-transform group-hover:translate-x-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Notes Modal -->
    <div v-if="showNotesModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0 pointer-events-none">
        <div class="fixed inset-0 transition-opacity pointer-events-none" aria-hidden="true">
          <div class="absolute inset-0 bg-gray-500 opacity-75 pointer-events-auto" @click="cancelNotes"></div>
        </div>

        <!-- Modal content -->
        <div class="relative z-50 inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6 pointer-events-auto">
          <div>
            <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-purple-100">
              <svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
            </div>
            <div class="mt-3 text-center sm:mt-5">
              <h3 class="text-lg leading-6 font-medium text-gray-900">
                Add Notes for {{ scheduleStore.parseDate(selectedDate).toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  month: 'long', 
                  day: 'numeric' 
                }) }}
              </h3>
              <div class="mt-2">
                <p class="text-sm text-gray-500">
                  Add assignments, deadlines, or other important information for this date.
                </p>
              </div>
            </div>
          </div>
          
          <div class="mt-5 sm:mt-6">
            <textarea
              v-model="tempNote"
              rows="4"
              :maxlength="characterLimit"
              :class="{
                'ring-red-500 border-red-500': isOverLimit,
                'ring-gray-300': !isOverLimit
              }"
              class="block w-full rounded-lg border-0 py-3 px-4 text-gray-900 ring-1 ring-inset placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 resize-none"
              placeholder="e.g., Assignment 1 due, Quiz on Chapter 3, Guest speaker presentation..."
              autofocus
            ></textarea>
            
            <!-- Character Count Display -->
            <div class="flex justify-between items-center mt-2">
              <div class="text-xs text-gray-500">
                Supports Unicode characters (mathematical symbols, international languages)
              </div>
              <div :class="characterCountColor" class="text-sm font-medium">
                {{ characterCountText }}
                <span v-if="charactersRemaining < 50" class="text-red-600">
                  ({{ charactersRemaining }} remaining)
                </span>
              </div>
            </div>
            
            <!-- Over Limit Warning -->
            <div v-if="isOverLimit" class="mt-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">
              <span class="font-medium">Character limit exceeded!</span> 
              Note will be truncated to {{ characterLimit }} characters when saved.
            </div>
          </div>

          <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
            <button
              type="button"
              @click="saveNotes"
              class="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-purple-600 text-base font-medium text-white hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 sm:col-start-2 sm:text-sm transition duration-200"
            >
              Save Notes
            </button>
            <button
              type="button"
              @click="cancelNotes"
              class="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 sm:mt-0 sm:col-start-1 sm:text-sm transition duration-200"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
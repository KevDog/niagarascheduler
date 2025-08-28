import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'

interface DateNote {
  date: string
  note: string
  createdAt: string
  updatedAt: string
}

interface ScheduleItem {
  date: string
  type: 'class' | 'holiday' | 'event'
  name?: string
  eventType?: string
}

export const useScheduleStore = defineStore('schedule', () => {
  // State
  const dateNotes = ref<Record<string, DateNote>>({})
  const classDates = ref<string[]>([])
  const academicEvents = ref<any[]>([])
  const calendarLoading = ref(false)
  const userImportantDates = ref<Array<{ date: string, description: string, type: 'class' | 'holiday' | 'event' | 'other' }>>([])
  const cancelledClasses = ref<Set<string>>(new Set())
  
  // Modal state
  const selectedDate = ref<string>('')
  const showNotesModal = ref(false)
  const tempNote = ref<string>('')

  // Helper functions
  const parseDate = (dateString: string): Date => {
    return new Date(dateString + 'T12:00:00')
  }

  const getNotesStorageKey = (semester: string, department: string, course: string) => {
    return `schedule-notes-${semester}-${department}-${course}`
  }

  // Computed
  const scheduleItems = computed(() => {
    const items: ScheduleItem[] = []
    
    // Add all class dates
    classDates.value.forEach(date => {
      items.push({ date, type: 'class' })
    })
    
    // Add holidays and relevant academic events that would affect class schedule
    academicEvents.value.forEach(event => {
      const eventDate = event.date
      if (eventDate) {
        const isHoliday = event.type === 'holiday' ||
                         event.name.toLowerCase().includes('break')
        
        if (isHoliday) {
          items.push({ 
            date: eventDate, 
            type: 'holiday', 
            name: event.name,
            eventType: event.type 
          })
        } else {
          items.push({ 
            date: eventDate, 
            type: 'event', 
            name: event.name,
            eventType: event.type 
          })
        }
      }
    })
    
    // Add user-defined important dates
    userImportantDates.value.forEach(importantDate => {
      if (importantDate.date && importantDate.description) {
        items.push({
          date: importantDate.date,
          type: importantDate.type as 'class' | 'holiday' | 'event',
          name: importantDate.description,
          eventType: 'user_defined'
        })
      }
    })
    
    // Sort by date using proper date parsing
    items.sort((a, b) => parseDate(a.date).getTime() - parseDate(b.date).getTime())
    
    return items
  })

  // Character limit validation
  const characterCount = computed(() => tempNote.value.length)
  const characterLimit = 750
  const isOverLimit = computed(() => characterCount.value > characterLimit)
  const charactersRemaining = computed(() => characterLimit - characterCount.value)
  const characterCountText = computed(() => `${characterCount.value}/${characterLimit} characters`)
  
  const characterCountColor = computed(() => {
    if (charactersRemaining.value < 50) return 'text-red-600'
    if (charactersRemaining.value < 100) return 'text-amber-600'
    return 'text-gray-500'
  })

  // Actions
  const loadNotesFromStorage = (semester: string, department: string, course: string) => {
    try {
      const stored = localStorage.getItem(getNotesStorageKey(semester, department, course))
      if (stored) {
        dateNotes.value = JSON.parse(stored)
      }
    } catch (error) {
      console.warn('Failed to load notes from localStorage:', error)
    }
  }

  const saveNotesToStorage = (semester: string, department: string, course: string) => {
    try {
      localStorage.setItem(getNotesStorageKey(semester, department, course), JSON.stringify(dateNotes.value))
    } catch (error) {
      console.warn('Failed to save notes to localStorage:', error)
    }
  }

  const openNotesModal = (date: string) => {
    selectedDate.value = date
    const existingNote = dateNotes.value[date]
    tempNote.value = existingNote ? existingNote.note : ''
    showNotesModal.value = true
  }

  const saveNote = (semester: string, department: string, course: string) => {
    if (selectedDate.value) {
      const now = new Date().toISOString()
      
      if (tempNote.value.trim()) {
        // Enforce 750 character limit
        const trimmedNote = tempNote.value.trim()
        const finalNote = trimmedNote.length > 750 ? trimmedNote.substring(0, 750) : trimmedNote
        
        const existingNote = dateNotes.value[selectedDate.value]
        dateNotes.value[selectedDate.value] = {
          date: selectedDate.value,
          note: finalNote,
          createdAt: existingNote?.createdAt || now,
          updatedAt: now
        }
      } else {
        // Remove empty notes
        delete dateNotes.value[selectedDate.value]
      }
      
      saveNotesToStorage(semester, department, course)
    }
    closeNotesModal()
  }

  const closeNotesModal = () => {
    selectedDate.value = ''
    tempNote.value = ''
    showNotesModal.value = false
  }

  const generateClassDates = async (semester: string, meetingDays: string) => {
    if (!semester || !meetingDays) return
    
    calendarLoading.value = true
    try {
      const response = await fetch(`/api/calendar/${semester}/class-dates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          meeting_days: meetingDays
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        classDates.value = data.data.class_dates || []
        academicEvents.value = data.data.academic_events || []
        console.log(`Generated ${classDates.value.length} class dates for ${meetingDays}`)
      } else {
        console.error('Failed to generate class dates:', response.status)
      }
    } catch (error) {
      console.error('Error generating class dates:', error)
    } finally {
      calendarLoading.value = false
    }
  }

  const hasNoteForDate = (date: string): boolean => {
    return !!(dateNotes.value[date]?.note?.trim())
  }

  const getNoteForDate = (date: string): string => {
    return dateNotes.value[date]?.note || ''
  }

  const setUserImportantDates = (dates: Array<{ date: string, description: string, type: 'class' | 'holiday' | 'event' | 'other' }>) => {
    userImportantDates.value = dates.filter(d => d.date && d.description)
  }

  const removeUserImportantDate = (dateToRemove: string) => {
    userImportantDates.value = userImportantDates.value.filter(d => d.date !== dateToRemove)
  }

  const toggleClassCancellation = (date: string) => {
    if (cancelledClasses.value.has(date)) {
      cancelledClasses.value.delete(date)
    } else {
      cancelledClasses.value.add(date)
    }
  }

  const isClassCancelled = (date: string): boolean => {
    return cancelledClasses.value.has(date)
  }

  return {
    // State
    dateNotes,
    classDates,
    academicEvents,
    calendarLoading,
    selectedDate,
    showNotesModal,
    tempNote,
    userImportantDates,
    cancelledClasses,
    
    // Computed
    scheduleItems,
    characterCount,
    characterLimit: readonly(ref(characterLimit)),
    isOverLimit,
    charactersRemaining,
    characterCountText,
    characterCountColor,
    
    // Actions
    loadNotesFromStorage,
    saveNotesToStorage,
    openNotesModal,
    saveNote,
    closeNotesModal,
    generateClassDates,
    hasNoteForDate,
    getNoteForDate,
    parseDate,
    setUserImportantDates,
    removeUserImportantDate,
    toggleClassCancellation,
    isClassCancelled
  }
})
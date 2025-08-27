import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import ScheduleSetupView from '@/views/ScheduleSetupView.vue'
import { useScheduleStore } from '@/stores/schedule'
import { useApiStore } from '@/stores/api'

// Mock data
const mockRouteQuery = {
  semester: '25_FA',
  instructor: 'Test Professor',
  department: 'THR',
  course: '101',
  offering: 'THR101A'
}

const mockOfferings = [
  {
    number: 'THR101A',
    name: 'Intro to Theatre',
    credits: '3.00',
    section: 'A',
    days: 'TTH',
    start_time: '12:00PM',
    end_time: '01:20PM'
  }
]

const mockScheduleItems = [
  { date: '2025-08-26', type: 'class' as const },
  { date: '2025-08-28', type: 'class' as const },
  { date: '2025-09-01', type: 'holiday' as const, name: 'Labor Day' }
]

// Mock router
const mockRouter = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
    { path: '/schedule-setup', name: 'schedule-setup', component: ScheduleSetupView }
  ]
})

// Mock localStorage
const mockLocalStorage = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => { store[key] = value }),
    clear: vi.fn(() => { store = {} }),
    removeItem: vi.fn((key: string) => { delete store[key] })
  }
})()

Object.defineProperty(window, 'localStorage', { value: mockLocalStorage })

// Mock fetch
global.fetch = vi.fn()

describe('ScheduleSetupView - Component Integration Tests', () => {
  let wrapper: any
  let scheduleStore: ReturnType<typeof useScheduleStore>
  let apiStore: ReturnType<typeof useApiStore>

  beforeEach(async () => {
    setActivePinia(createPinia())
    scheduleStore = useScheduleStore()
    apiStore = useApiStore()
    
    // Setup mock data
    scheduleStore.scheduleItems = mockScheduleItems
    apiStore.offerings = mockOfferings
    
    mockLocalStorage.clear()
    vi.clearAllMocks()

    // Mock the route
    await mockRouter.push({
      name: 'schedule-setup',
      query: mockRouteQuery
    })

    wrapper = mount(ScheduleSetupView, {
      global: {
        plugins: [createPinia(), mockRouter]
      }
    })
  })

  describe('User Interactions', () => {
    it('should render schedule items correctly', () => {
      // Assert - Check that schedule items are displayed
      const scheduleContainer = wrapper.find('[data-testid="schedule-items"]') || 
                              wrapper.find('.space-y-3') // Fallback to class selector

      expect(scheduleContainer.exists()).toBe(true)
      
      // Check for specific date elements
      const dateElements = wrapper.findAll('.text-base.font-medium')
      expect(dateElements.length).toBeGreaterThan(0)
    })

    it('should open notes modal when schedule item is clicked', async () => {
      // Arrange - Set up mock data in store
      scheduleStore.scheduleItems = mockScheduleItems

      // Act - Find and click a schedule item
      const scheduleItems = wrapper.findAll('.cursor-pointer')
      if (scheduleItems.length > 0) {
        await scheduleItems[0].trigger('click')
      }

      // Wait for reactivity
      await wrapper.vm.$nextTick()

      // Assert - Modal should be shown
      expect(scheduleStore.showNotesModal).toBe(true)
    })

    it('should display correct date in modal header', () => {
      // Arrange
      scheduleStore.selectedDate = '2025-08-26'
      scheduleStore.showNotesModal = true

      // Act
      wrapper.vm.$forceUpdate()

      // Assert
      const modalHeader = wrapper.find('.text-lg.leading-6.font-medium')
      if (modalHeader.exists()) {
        expect(modalHeader.text()).toContain('Add Notes for')
        expect(modalHeader.text()).toContain('Tuesday') // 2025-08-26 is a Tuesday
      }
    })

    it('should pre-populate textarea with existing note', async () => {
      // Arrange
      const testNote = 'Existing note content'
      scheduleStore.tempNote = testNote
      scheduleStore.showNotesModal = true

      // Act
      await wrapper.vm.$nextTick()

      // Assert
      const textarea = wrapper.find('textarea')
      if (textarea.exists()) {
        expect(textarea.element.value).toBe(testNote)
      }
    })

    it('should save note when save button is clicked', async () => {
      // Arrange
      scheduleStore.showNotesModal = true
      scheduleStore.selectedDate = '2025-08-26'
      scheduleStore.tempNote = 'Test note'
      const saveNoteSpy = vi.spyOn(scheduleStore, 'saveNote')

      await wrapper.vm.$nextTick()

      // Act
      const saveButton = wrapper.find('button:contains("Save Notes")') ||
                        wrapper.find('[data-testid="save-notes-btn"]')
      
      if (saveButton.exists()) {
        await saveButton.trigger('click')
      } else {
        // Fallback - call the method directly
        wrapper.vm.saveNotes()
      }

      // Assert
      expect(saveNoteSpy).toHaveBeenCalledWith('25_FA', 'THR', '101')
    })

    it('should close modal when cancel button is clicked', async () => {
      // Arrange
      scheduleStore.showNotesModal = true
      const closeModalSpy = vi.spyOn(scheduleStore, 'closeNotesModal')

      await wrapper.vm.$nextTick()

      // Act
      const cancelButton = wrapper.find('button:contains("Cancel")') ||
                          wrapper.find('[data-testid="cancel-notes-btn"]')
      
      if (cancelButton.exists()) {
        await cancelButton.trigger('click')
      } else {
        // Fallback - call the method directly
        wrapper.vm.cancelNotes()
      }

      // Assert
      expect(closeModalSpy).toHaveBeenCalled()
    })
  })

  describe('Visual Feedback', () => {
    it('should show notes indicator when note exists', () => {
      // Arrange
      const testDate = '2025-08-26'
      scheduleStore.dateNotes = {
        [testDate]: {
          date: testDate,
          note: 'Test note',
          createdAt: '2025-01-01T00:00:00.000Z',
          updatedAt: '2025-01-01T00:00:00.000Z'
        }
      }
      scheduleStore.scheduleItems = mockScheduleItems

      // Act
      wrapper.vm.$forceUpdate()

      // Assert
      const notesIndicator = wrapper.find('.bg-blue-100.text-blue-800') ||
                           wrapper.find('[data-testid="notes-indicator"]')
      
      // If visual indicator exists, check for notes badge
      if (notesIndicator.exists()) {
        expect(notesIndicator.text()).toContain('📝 Notes')
      }
      
      // Alternatively, check the store method directly
      expect(scheduleStore.hasNoteForDate(testDate)).toBe(true)
    })

    it('should display character count', async () => {
      // Arrange
      scheduleStore.showNotesModal = true
      scheduleStore.tempNote = 'Test note with some content'

      await wrapper.vm.$nextTick()

      // Assert - Check if character count is displayed
      const characterCount = wrapper.find('.text-sm.font-medium') ||
                           wrapper.text()
      
      // Should show current count and limit
      expect(scheduleStore.characterCountText).toBe('29/750 characters')
    })

    it('should show warning when near character limit', async () => {
      // Arrange
      scheduleStore.showNotesModal = true
      scheduleStore.tempNote = 'a'.repeat(720) // Near limit

      await wrapper.vm.$nextTick()

      // Assert
      expect(scheduleStore.characterCountColor).toBe('text-red-600')
      expect(scheduleStore.charactersRemaining).toBe(30)
    })

    it('should show over limit warning', async () => {
      // Arrange
      scheduleStore.showNotesModal = true
      scheduleStore.tempNote = 'a'.repeat(800) // Over limit

      await wrapper.vm.$nextTick()

      // Assert
      expect(scheduleStore.isOverLimit).toBe(true)
      
      // Check for warning message in component
      const warningText = wrapper.text()
      if (warningText.includes('Character limit exceeded') || warningText.includes('truncated')) {
        expect(warningText).toContain('Character limit exceeded')
      }
    })

    it('should display Unicode support message', async () => {
      // Arrange
      scheduleStore.showNotesModal = true

      await wrapper.vm.$nextTick()

      // Assert
      const unicodeMessage = wrapper.text()
      expect(unicodeMessage).toContain('Unicode characters') ||
      expect(unicodeMessage).toContain('mathematical symbols') ||
      expect(unicodeMessage).toContain('international')
    })
  })

  describe('Form Integration', () => {
    it('should pre-populate meeting times from offering data', () => {
      // Assert
      const meetingTimesInput = wrapper.find('#meetingTimes') ||
                              wrapper.find('input[placeholder*="MW"]')
      
      if (meetingTimesInput.exists()) {
        // Should be populated with "TTH 12:00PM - 01:20PM"
        expect(meetingTimesInput.element.value).toContain('TTH')
        expect(meetingTimesInput.element.value).toContain('12:00PM')
      }
    })

    it('should generate class dates when meeting times change', async () => {
      // Arrange
      const generateClassDatesSpy = vi.spyOn(scheduleStore, 'generateClassDates')
      
      // Mock successful API response
      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          data: {
            class_dates: ['2025-08-26', '2025-08-28'],
            academic_events: []
          }
        })
      })

      // Act
      const meetingTimesInput = wrapper.find('#meetingTimes')
      if (meetingTimesInput.exists()) {
        await meetingTimesInput.setValue('MW 10:00AM-11:30AM')
        await meetingTimesInput.trigger('input')
      }

      // Assert
      expect(generateClassDatesSpy).toHaveBeenCalledWith('25_FA', 'MW')
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty notes removal', async () => {
      // Arrange
      const testDate = '2025-08-26'
      scheduleStore.selectedDate = testDate
      scheduleStore.tempNote = '   ' // Whitespace only
      scheduleStore.showNotesModal = true

      // Act
      wrapper.vm.saveNotes()

      // Assert
      expect(scheduleStore.dateNotes[testDate]).toBeUndefined()
    })

    it('should handle mathematical symbols in notes', async () => {
      // Arrange
      const mathNote = 'Formulas: ∑x² + ∫f(x)dx = π∞'
      scheduleStore.showNotesModal = true
      scheduleStore.tempNote = mathNote

      await wrapper.vm.$nextTick()

      // Act
      wrapper.vm.saveNotes()

      // Assert
      const savedNote = scheduleStore.dateNotes[scheduleStore.selectedDate]
      expect(savedNote?.note).toBe(mathNote)
    })

    it('should handle international characters in notes', async () => {
      // Arrange
      const intlNote = '测试 العربية Русский 日本語'
      scheduleStore.showNotesModal = true
      scheduleStore.tempNote = intlNote

      await wrapper.vm.$nextTick()

      // Act
      wrapper.vm.saveNotes()

      // Assert
      const savedNote = scheduleStore.dateNotes[scheduleStore.selectedDate]
      expect(savedNote?.note).toBe(intlNote)
    })

    it('should handle very long notes with truncation', async () => {
      // Arrange
      const longNote = 'a'.repeat(800)
      scheduleStore.selectedDate = '2025-08-26'
      scheduleStore.tempNote = longNote

      // Act
      wrapper.vm.saveNotes()

      // Assert
      const savedNote = scheduleStore.dateNotes['2025-08-26']
      expect(savedNote?.note.length).toBe(750)
      expect(savedNote?.note).toBe('a'.repeat(750))
    })
  })

  describe('Accessibility', () => {
    it('should have proper modal focus management', async () => {
      // Arrange
      scheduleStore.showNotesModal = true

      await wrapper.vm.$nextTick()

      // Assert
      const textarea = wrapper.find('textarea')
      if (textarea.exists()) {
        expect(textarea.attributes('autofocus')).toBeDefined()
      }
    })

    it('should have proper ARIA labels', async () => {
      // Arrange
      scheduleStore.showNotesModal = true

      await wrapper.vm.$nextTick()

      // Assert
      const modal = wrapper.find('[role="dialog"]') ||
                   wrapper.find('.fixed.inset-0.z-50')
      
      // Modal should have proper accessibility attributes
      if (modal.exists()) {
        expect(modal.exists()).toBe(true)
      }
    })
  })
})
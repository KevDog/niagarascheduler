import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useScheduleStore } from '@/stores/schedule'

// Mock data as defined in CLAUDE.md
const mockWizardData = {
  semester: '25_FA',
  department: 'THR', 
  course: '101',
  instructor: 'Test Professor'
}

const mockScheduleItems = [
  { date: '2025-08-26', type: 'class' },
  { date: '2025-09-01', type: 'holiday', name: 'Labor Day' },
  { date: '2025-08-28', type: 'class' }
]

const mockNotes = {
  '2025-08-26': 'Assignment 1 due - Mathematical proofs (∑, ∫)',
  '2025-08-28': 'Quiz on Chapter 1 中文测试'
}

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

// Mock fetch for API calls
global.fetch = vi.fn()

describe('useScheduleStore - Pinia Store Tests', () => {
  let scheduleStore: ReturnType<typeof useScheduleStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    scheduleStore = useScheduleStore()
    mockLocalStorage.clear()
    vi.clearAllMocks()
  })

  describe('Core Functionality', () => {
    it('should open notes modal with correct data', () => {
      // Arrange
      const testDate = '2025-08-26'
      scheduleStore.dateNotes[testDate] = {
        date: testDate,
        note: 'Existing note',
        createdAt: '2025-01-01T00:00:00.000Z',
        updatedAt: '2025-01-01T00:00:00.000Z'
      }

      // Act
      scheduleStore.openNotesModal(testDate)

      // Assert
      expect(scheduleStore.selectedDate).toBe(testDate)
      expect(scheduleStore.tempNote).toBe('Existing note')
      expect(scheduleStore.showNotesModal).toBe(true)
    })

    it('should open notes modal with empty note for new date', () => {
      // Arrange
      const testDate = '2025-08-30'

      // Act
      scheduleStore.openNotesModal(testDate)

      // Assert
      expect(scheduleStore.selectedDate).toBe(testDate)
      expect(scheduleStore.tempNote).toBe('')
      expect(scheduleStore.showNotesModal).toBe(true)
    })

    it('should save note and close modal', () => {
      // Arrange
      const testDate = '2025-08-26'
      scheduleStore.selectedDate = testDate
      scheduleStore.tempNote = 'Test note'
      scheduleStore.showNotesModal = true

      // Act
      scheduleStore.saveNote(mockWizardData.semester, mockWizardData.department, mockWizardData.course)

      // Assert
      expect(scheduleStore.dateNotes[testDate]).toBeDefined()
      expect(scheduleStore.dateNotes[testDate].note).toBe('Test note')
      expect(scheduleStore.showNotesModal).toBe(false)
      expect(scheduleStore.selectedDate).toBe('')
      expect(scheduleStore.tempNote).toBe('')
    })

    it('should close modal without saving', () => {
      // Arrange
      scheduleStore.selectedDate = '2025-08-26'
      scheduleStore.tempNote = 'Unsaved note'
      scheduleStore.showNotesModal = true

      // Act
      scheduleStore.closeNotesModal()

      // Assert
      expect(scheduleStore.showNotesModal).toBe(false)
      expect(scheduleStore.selectedDate).toBe('')
      expect(scheduleStore.tempNote).toBe('')
    })

    it('should return correct note existence status', () => {
      // Arrange
      const testDate = '2025-08-26'
      scheduleStore.dateNotes[testDate] = {
        date: testDate,
        note: 'Test note',
        createdAt: '2025-01-01T00:00:00.000Z',
        updatedAt: '2025-01-01T00:00:00.000Z'
      }

      // Act & Assert
      expect(scheduleStore.hasNoteForDate(testDate)).toBe(true)
      expect(scheduleStore.hasNoteForDate('2025-08-30')).toBe(false)
    })

    it('should return correct note text', () => {
      // Arrange
      const testDate = '2025-08-26'
      const noteText = 'Test note'
      scheduleStore.dateNotes[testDate] = {
        date: testDate,
        note: noteText,
        createdAt: '2025-01-01T00:00:00.000Z',
        updatedAt: '2025-01-01T00:00:00.000Z'
      }

      // Act & Assert
      expect(scheduleStore.getNoteForDate(testDate)).toBe(noteText)
      expect(scheduleStore.getNoteForDate('2025-08-30')).toBe('')
    })
  })

  describe('Character Limits & Unicode Support', () => {
    it('should enforce 750 character limit', () => {
      // Arrange
      const longNote = 'a'.repeat(800) // 800 characters
      const testDate = '2025-08-26'
      scheduleStore.selectedDate = testDate
      scheduleStore.tempNote = longNote

      // Act
      scheduleStore.saveNote(mockWizardData.semester, mockWizardData.department, mockWizardData.course)

      // Assert
      expect(scheduleStore.dateNotes[testDate].note).toBe('a'.repeat(750))
      expect(scheduleStore.dateNotes[testDate].note.length).toBe(750)
    })

    it('should handle mathematical symbols correctly', () => {
      // Arrange
      const mathNote = 'Mathematical symbols: ∑, ∫, π, ∞, α, β, γ'
      const testDate = '2025-08-26'
      scheduleStore.selectedDate = testDate
      scheduleStore.tempNote = mathNote

      // Act
      scheduleStore.saveNote(mockWizardData.semester, mockWizardData.department, mockWizardData.course)

      // Assert
      expect(scheduleStore.dateNotes[testDate].note).toBe(mathNote)
    })

    it('should handle international characters correctly', () => {
      // Arrange
      const intlNote = 'International: 中文测试, العربية, Русский, 日本語'
      const testDate = '2025-08-26'
      scheduleStore.selectedDate = testDate
      scheduleStore.tempNote = intlNote

      // Act
      scheduleStore.saveNote(mockWizardData.semester, mockWizardData.department, mockWizardData.course)

      // Assert
      expect(scheduleStore.dateNotes[testDate].note).toBe(intlNote)
    })

    it('should remove empty notes', () => {
      // Arrange
      const testDate = '2025-08-26'
      scheduleStore.dateNotes[testDate] = {
        date: testDate,
        note: 'Existing note',
        createdAt: '2025-01-01T00:00:00.000Z',
        updatedAt: '2025-01-01T00:00:00.000Z'
      }
      scheduleStore.selectedDate = testDate
      scheduleStore.tempNote = '   ' // Whitespace only

      // Act
      scheduleStore.saveNote(mockWizardData.semester, mockWizardData.department, mockWizardData.course)

      // Assert
      expect(scheduleStore.dateNotes[testDate]).toBeUndefined()
    })

    it('should calculate character count correctly', () => {
      // Act
      scheduleStore.tempNote = 'Test note'

      // Assert
      expect(scheduleStore.characterCount).toBe(9)
      expect(scheduleStore.charactersRemaining).toBe(741)
      expect(scheduleStore.isOverLimit).toBe(false)
    })

    it('should detect over limit state', () => {
      // Act
      scheduleStore.tempNote = 'a'.repeat(800)

      // Assert
      expect(scheduleStore.characterCount).toBe(800)
      expect(scheduleStore.charactersRemaining).toBe(-50)
      expect(scheduleStore.isOverLimit).toBe(true)
    })

    it('should return correct character count color', () => {
      // Test green/gray (normal)
      scheduleStore.tempNote = 'a'.repeat(500)
      expect(scheduleStore.characterCountColor).toBe('text-gray-500')

      // Test amber (warning)
      scheduleStore.tempNote = 'a'.repeat(680)
      expect(scheduleStore.characterCountColor).toBe('text-amber-600')

      // Test red (danger)
      scheduleStore.tempNote = 'a'.repeat(720)
      expect(scheduleStore.characterCountColor).toBe('text-red-600')
    })
  })

  describe('Persistence Tests', () => {
    it('should generate correct storage key', () => {
      // Act
      scheduleStore.saveNotesToStorage(
        mockWizardData.semester, 
        mockWizardData.department, 
        mockWizardData.course
      )

      // Assert
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'schedule-notes-25_FA-THR-101',
        expect.any(String)
      )
    })

    it('should save notes to localStorage', () => {
      // Arrange
      const testDate = '2025-08-26'
      scheduleStore.dateNotes[testDate] = {
        date: testDate,
        note: 'Test note',
        createdAt: '2025-01-01T00:00:00.000Z',
        updatedAt: '2025-01-01T00:00:00.000Z'
      }

      // Act
      scheduleStore.saveNotesToStorage(
        mockWizardData.semester, 
        mockWizardData.department, 
        mockWizardData.course
      )

      // Assert
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'schedule-notes-25_FA-THR-101',
        JSON.stringify(scheduleStore.dateNotes)
      )
    })

    it('should load notes from localStorage', () => {
      // Arrange
      const storedNotes = { '2025-08-26': { date: '2025-08-26', note: 'Stored note', createdAt: '2025-01-01T00:00:00.000Z', updatedAt: '2025-01-01T00:00:00.000Z' } }
      mockLocalStorage.setItem('schedule-notes-25_FA-THR-101', JSON.stringify(storedNotes))

      // Act
      scheduleStore.loadNotesFromStorage(
        mockWizardData.semester, 
        mockWizardData.department, 
        mockWizardData.course
      )

      // Assert
      expect(scheduleStore.dateNotes).toEqual(storedNotes)
    })

    it('should handle invalid JSON in localStorage gracefully', () => {
      // Arrange
      mockLocalStorage.setItem('schedule-notes-25_FA-THR-101', 'invalid json')
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      // Act
      scheduleStore.loadNotesFromStorage(
        mockWizardData.semester, 
        mockWizardData.department, 
        mockWizardData.course
      )

      // Assert
      expect(consoleSpy).toHaveBeenCalledWith('Failed to load notes from localStorage:', expect.any(Error))
      expect(scheduleStore.dateNotes).toEqual({})
      
      consoleSpy.mockRestore()
    })

    it('should isolate notes by course', () => {
      // Arrange
      const course1Key = 'schedule-notes-25_FA-THR-101'
      const course2Key = 'schedule-notes-25_FA-THR-102'
      
      mockLocalStorage.setItem(course1Key, JSON.stringify({ '2025-08-26': { note: 'Course 1 note' } }))
      mockLocalStorage.setItem(course2Key, JSON.stringify({ '2025-08-26': { note: 'Course 2 note' } }))

      // Act - Load course 1 notes
      scheduleStore.loadNotesFromStorage('25_FA', 'THR', '101')

      // Assert
      expect(scheduleStore.dateNotes['2025-08-26']).toEqual({ note: 'Course 1 note' })
    })
  })

  describe('API Integration', () => {
    it('should generate class dates successfully', async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          data: {
            class_dates: ['2025-08-26', '2025-08-28'],
            academic_events: [{ date: '2025-09-01', name: 'Labor Day', type: 'holiday' }]
          }
        })
      }
      ;(global.fetch as any).mockResolvedValue(mockResponse)

      // Act
      await scheduleStore.generateClassDates('25_FA', 'TTH')

      // Assert
      expect(global.fetch).toHaveBeenCalledWith('/api/calendar/25_FA/class-dates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meeting_days: 'TTH' })
      })
      expect(scheduleStore.classDates).toEqual(['2025-08-26', '2025-08-28'])
      expect(scheduleStore.academicEvents).toHaveLength(1)
      expect(scheduleStore.calendarLoading).toBe(false)
    })

    it('should handle API errors gracefully', async () => {
      // Arrange
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      ;(global.fetch as any).mockResolvedValue({ ok: false, status: 500 })

      // Act
      await scheduleStore.generateClassDates('25_FA', 'TTH')

      // Assert
      expect(consoleSpy).toHaveBeenCalledWith('Failed to generate class dates:', 500)
      expect(scheduleStore.calendarLoading).toBe(false)
      
      consoleSpy.mockRestore()
    })
  })

  describe('Date Parsing', () => {
    it('should parse dates correctly to avoid timezone issues', () => {
      // Act
      const parsedDate = scheduleStore.parseDate('2025-09-01')

      // Assert
      expect(parsedDate.getFullYear()).toBe(2025)
      expect(parsedDate.getMonth()).toBe(8) // September is month 8 (0-based)
      expect(parsedDate.getDate()).toBe(1)
      expect(parsedDate.getHours()).toBe(12) // Should be noon to avoid timezone issues
    })
  })
})
import { ref, computed, watch } from 'vue'
import { useApiData } from './useApiData'

export function useCourseSelection() {
  // Get API data composable
  const { courses, offerings, fetchCourses, fetchOfferings } = useApiData()

  // Form state
  const selectedSemester = ref('')
  const instructorName = ref('')
  const selectedDepartment = ref('')
  const selectedCourse = ref('')
  const selectedOffering = ref('')

  // Computed properties
  const canProceed = computed(() => {
    return selectedSemester.value && 
           instructorName.value.trim() && 
           selectedDepartment.value && 
           selectedCourse.value && 
           selectedOffering.value
  })

  // Watchers for cascading updates
  watch(selectedDepartment, async (newDept) => {
    selectedCourse.value = ''
    selectedOffering.value = ''
    if (newDept) {
      console.log('Fetching courses for department:', newDept)
      await fetchCourses(newDept)
      console.log('Courses after fetch:', courses.value?.length || 0)
    }
  })

  watch([selectedSemester, selectedDepartment], async ([newSemester, newDept]) => {
    selectedOffering.value = ''
    if (newSemester && newDept) {
      console.log('Fetching offerings for:', newSemester, newDept)
      await fetchOfferings(newSemester, newDept)
      console.log('Offerings after fetch:', offerings.value?.length || 0, offerings.value)
    }
  })

  watch(selectedCourse, () => {
    selectedOffering.value = ''
  })

  // Reset form
  const resetForm = () => {
    selectedSemester.value = ''
    instructorName.value = ''
    selectedDepartment.value = ''
    selectedCourse.value = ''
    selectedOffering.value = ''
  }

  // Get form data
  const getFormData = () => ({
    semester: selectedSemester.value,
    instructor: instructorName.value,
    department: selectedDepartment.value,
    course: selectedCourse.value,
    offering: selectedOffering.value
  })

  return {
    // Form state
    selectedSemester,
    instructorName,
    selectedDepartment,
    selectedCourse,
    selectedOffering,

    // Computed
    canProceed,

    // Data from API composable
    courses,
    offerings,

    // Methods
    resetForm,
    getFormData
  }
}
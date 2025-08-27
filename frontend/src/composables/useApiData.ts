import { storeToRefs } from 'pinia'
import { useApiStore } from '@/stores/api'

export function useApiData() {
  const store = useApiStore()
  const { config, departments, courses, offerings, loading, semesters } = storeToRefs(store)
  
  return {
    // State from Pinia store (reactive refs)
    config,
    departments,
    courses,
    offerings,
    loading,
    semesters,
    
    // Actions from Pinia store
    fetchConfig: store.fetchConfig,
    fetchDepartments: store.fetchDepartments,
    fetchCourses: store.fetchCourses,
    fetchOfferings: store.fetchOfferings,
    
    // Getters from Pinia store
    getDepartmentByCode: store.getDepartmentByCode,
    getCourseByNumber: store.getCourseByNumber,
    getOfferingsByCourse: store.getOfferingsByCourse
  }
}
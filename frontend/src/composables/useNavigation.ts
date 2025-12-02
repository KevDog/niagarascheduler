import { useRouter } from 'vue-router'

export function useNavigation() {
  const router = useRouter()

  const navigateToInstructorInfo = (formData: {
    semester: string
    department: string
    course: string
    offering: string
  }) => {
    console.log('Proceeding to instructor info with:', formData)
    
    router.push({
      name: 'instructor-info',
      query: formData
    })
  }

  const navigateToScheduleSetup = (formData: {
    semester: string
    instructor: string
    department: string
    course: string
    offering: string
  }) => {
    console.log('Proceeding to schedule setup with:', formData)
    
    router.push({
      name: 'schedule-setup',
      query: formData
    })
  }

  const navigateToHome = () => {
    router.push({ name: 'home' })
  }

  const navigateToSupport = () => {
    router.push({ name: 'support' })
  }

  return {
    navigateToInstructorInfo,
    navigateToScheduleSetup,
    navigateToHome,
    navigateToSupport
  }
}
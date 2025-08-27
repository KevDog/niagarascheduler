import { useRouter } from 'vue-router'

export function useNavigation() {
  const router = useRouter()

  const navigateToScheduleSetup = (formData: {
    semester: string
    instructor: string
    department: string
    course: string
    offering: string
  }) => {
    console.log('Proceeding with:', formData)
    
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
    navigateToScheduleSetup,
    navigateToHome,
    navigateToSupport
  }
}
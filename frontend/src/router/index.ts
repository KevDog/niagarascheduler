import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/instructor-info',
      name: 'instructor-info',
      component: () => import('../views/InstructorInfoView.vue'),
    },
    {
      path: '/schedule-setup',
      name: 'schedule-setup',
      component: () => import('../views/ScheduleSetupView.vue'),
    },
    {
      path: '/course-content',
      name: 'course-content',
      component: () => import('../views/CourseContentView.vue'),
    },
    {
      path: '/policies-grading',
      name: 'policies-grading',
      component: () => import('../views/PoliciesGradingView.vue'),
    },
    {
      path: '/class-policies',
      name: 'class-policies',
      component: () => import('../views/ClassPoliciesView.vue'),
    },
    {
      path: '/syllabus-preview',
      name: 'syllabus-preview',
      component: () => import('../views/SyllabusPreviewView.vue'),
    },
    {
      path: '/support',
      name: 'support',
      // route level code-splitting
      // this generates a separate chunk (Support.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/SupportView.vue'),
    },
  ],
})

export default router

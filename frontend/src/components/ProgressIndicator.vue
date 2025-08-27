<script setup lang="ts">
interface Props {
  currentStep: number
  totalSteps: number
  stepLabel: string
}

const props = withDefaults(defineProps<Props>(), {
  currentStep: 1,
  totalSteps: 4,
  stepLabel: 'Basic Information'
})

const progressPercentage = (props.currentStep / props.totalSteps) * 100
</script>

<template>
  <div class="bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-100">
    <div class="flex items-center justify-between text-sm font-medium text-gray-700 mb-3">
      <span class="text-purple-600">Step {{ currentStep }} of {{ totalSteps }}</span>
      <span>{{ stepLabel }}</span>
    </div>
    <div class="w-full bg-purple-100 rounded-full h-2.5 shadow-inner">
      <div 
        class="bg-gradient-to-r from-purple-400 to-purple-600 h-2.5 rounded-full shadow-sm transition-all duration-300"
        :style="{ width: `${progressPercentage}%` }"
      ></div>
    </div>
  </div>
</template>
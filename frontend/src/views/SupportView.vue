<script setup lang="ts">
import { ref } from 'vue'

const form = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const isSubmitting = ref(false)
const submitStatus = ref<'idle' | 'success' | 'error'>('idle')
const errorMessage = ref('')

const submitForm = async () => {
  if (!form.value.name || !form.value.email || !form.value.subject || !form.value.message) {
    errorMessage.value = 'Please fill in all fields'
    submitStatus.value = 'error'
    return
  }

  isSubmitting.value = true
  submitStatus.value = 'idle'

  try {
    // Create mailto link with form data
    const subject = encodeURIComponent(`[NU Scheduler Support] ${form.value.subject}`)
    const body = encodeURIComponent(
      `From: ${form.value.name} (${form.value.email})\n\n${form.value.message}`
    )
    const mailtoLink = `mailto:kcstevens@mac.com?subject=${subject}&body=${body}`
    
    // Open default email client
    window.location.href = mailtoLink
    
    submitStatus.value = 'success'
    
    // Reset form after successful submission
    setTimeout(() => {
      form.value = { name: '', email: '', subject: '', message: '' }
      submitStatus.value = 'idle'
    }, 3000)
    
  } catch (error) {
    console.error('Error submitting form:', error)
    errorMessage.value = 'Failed to open email client. Please try again.'
    submitStatus.value = 'error'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="support">
    <div class="max-w-2xl mx-auto p-6">
      <h1 class="text-3xl font-bold text-center mb-8">Support</h1>
      
      <!-- Disclaimer -->
      <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
        <div class="flex">
          <div class="ml-3">
            <p class="text-sm text-yellow-700">
              <strong>Important Notice:</strong> This is an <strong>unofficial application</strong> created independently for Niagara University faculty and staff. 
              It is not officially endorsed by or affiliated with Niagara University. 
              Please <strong>do not contact NU IT staff</strong> for support with this application - they cannot assist with unofficial tools.
            </p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold mb-4">Need help with the Niagara University Scheduler?</h2>
        
        <p class="text-gray-600 mb-6">
          Send us a message and we'll get back to you as soon as possible. 
          Please include as much detail as possible about your issue or question.
        </p>

        <form @submit.prevent="submitForm" class="space-y-4">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
              Name *
            </label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Your full name"
            />
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
              Email *
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="your.email@example.com"
            />
          </div>

          <div>
            <label for="subject" class="block text-sm font-medium text-gray-700 mb-1">
              Subject *
            </label>
            <input
              id="subject"
              v-model="form.subject"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Brief description of your issue"
            />
          </div>

          <div>
            <label for="message" class="block text-sm font-medium text-gray-700 mb-1">
              Message *
            </label>
            <textarea
              id="message"
              v-model="form.message"
              required
              rows="5"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Please describe your issue or question in detail..."
            ></textarea>
          </div>

          <button
            type="submit"
            :disabled="isSubmitting"
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ isSubmitting ? 'Opening Email Client...' : 'Send Message' }}
          </button>
        </form>

        <!-- Status Messages -->
        <div v-if="submitStatus === 'success'" class="mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
          Your email client should have opened with a pre-filled message. If it didn't, you can manually email us at kcstevens@mac.com
        </div>

        <div v-if="submitStatus === 'error'" class="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {{ errorMessage }}
        </div>
      </div>

      <!-- Additional Support Information -->
      <div class="mt-8 bg-gray-50 rounded-lg p-6">
        <h3 class="text-lg font-semibold mb-3">Other Ways to Get Help</h3>
        <ul class="space-y-2 text-gray-600">
          <li>• Check the <RouterLink to="/" class="text-blue-600 hover:underline">Home page</RouterLink> for getting started guides</li>
          <li>• Email us directly: <a href="mailto:kcstevens@mac.com" class="text-blue-600 hover:underline">kcstevens@mac.com</a></li>
          <li>• For technical issues, please include your browser version and operating system</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.support {
  min-height: 100vh;
  background-color: #f9fafb;
  padding: 2rem 1rem;
}

@media (min-width: 1024px) {
  .support {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>

<template>
  <div class="flex flex-col gap-12">
    <!-- Validation Errors -->
    <div v-if="store.validationErrors.length > 0" class="bg-red-50 border border-red-200 rounded-xl p-4">
      <div class="flex items-start gap-3">
        <svg class="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <div class="flex-1">
          <h4 class="font-semibold text-red-800 mb-1">Registration Error</h4>
          <ul class="text-sm text-red-700 space-y-1">
            <li v-for="(error, index) in store.validationErrors" :key="index">{{ error }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Header Section -->
    <div class="flex flex-col gap-4">
      <h1 class="text-[24px] font-normal text-black leading-normal tracking-[-0.4px]">
        Registration Confirmation
      </h1>
      <p class="text-[14px] font-normal text-[#969696] leading-[20px] tracking-[-0.4px]">
        Please review your registration details for {{ store.event?.title || 'Lafiye Unveils' }}, including your selected arrival date and time. Kindly ensure all information is accurate before proceeding. Terms & Conditions apply.
      </p>
    </div>

    <!-- Guest Detail Section -->
    <div class="flex flex-col gap-4">
      <h3 class="text-[16px] font-normal text-black tracking-[-0.4px]">Guest Detail</h3>
      <div class="flex flex-col gap-3.5">
        <div 
          v-for="(participant, index) in store.participants" 
          :key="index"
          class="bg-[#F4F4F4] rounded-[10px] px-7 py-4 flex items-start justify-start"
        >
          <p class="text-[16px] font-normal text-black text-left tracking-[-0.4px]">
            {{ participant.full_name }}
          </p>
        </div>
      </div>
    </div>

    <!-- Arrival Date Section -->
    <div class="flex flex-col gap-4">
      <h3 class="text-[16px] font-normal text-black tracking-[-0.4px]">Arrival Date</h3>
      <div v-if="store.selectedDate" class="bg-[#F4F4F4] rounded-[10px] px-7 py-4 flex items-start justify-start">
        <span class="font-bold">{{ store.selectedDate.title }}</span>
        <span class="font-normal"> - {{ formatSelectedDate(store.selectedDate.date) }}</span>
      </div>
    </div>

    <!-- Arrival Time Section -->
    <div v-if="selectedScheduleDetails.length > 0" class="flex flex-col gap-4">
      <h3 class="text-[16px] font-normal text-black tracking-[-0.4px]">Arrival Time</h3>
      <div class="flex flex-col gap-3">
        <div 
          v-for="schedule in selectedScheduleDetails" 
          :key="schedule.name"
          class="bg-[#F4F4F4] rounded-[10px] px-5 py-4 flex flex-col gap-0 justify-center"
        >
          <p class="text-[16px] font-semibold text-black text-left tracking-[-0.4px]">
            {{ formatTime(schedule.start_time) }} - {{ formatTime(schedule.end_time) }}
          </p>
          <p class="text-[12px] font-normal text-black text-left tracking-[-0.4px]">
            Last Entry: {{ calculateLastEntry(schedule.end_time) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Captcha Widget -->
    <div id="recaptcha-widget" class="min-h-[65px]"></div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRegistrationStore } from '@/stores/registration'


const store = useRegistrationStore()

const dateStr = computed(() => {
    if (!store.selectedDate) return ''
    return new Intl.DateTimeFormat('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }).format(new Date(store.selectedDate.date))
})

const selectedScheduleDetails = computed(() => {
    if (!store.selectedSchedules || !store.schedulesResource.data) return []
    return store.schedulesResource.data.filter((s: any) => store.selectedSchedules.includes(s.name))
})

function getInitials(name: string) {
    if (!name) return '?'
    return name.split(' ').map((n) => n[0]).join('').substring(0, 2).toUpperCase()
}

function formatTime(timeStr: string) {
  if (!timeStr) return ''
  // Assume timeStr is HH:mm:ss
  const [hours, minutes] = timeStr.split(':')
  return `${hours}:${minutes}`
}

function calculateLastEntry(endTimeStr: string) {
  if (!endTimeStr) return ''
  const parts = endTimeStr.split(':')
  if (parts.length < 2) return ''
  
  const hours = Number(parts[0])
  const minutes = Number(parts[1])
  
  const date = new Date()
  date.setHours(hours, minutes, 0)
  // Subtract 20 minutes
  date.setMinutes(date.getMinutes() - 20)
  
  const h = date.getHours().toString().padStart(2, '0')
  const m = date.getMinutes().toString().padStart(2, '0')
  return `${h}:${m}`
}

function formatSelectedDate(dateStr: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'long', year: 'numeric' }).format(date)
}

// reCAPTCHA

onMounted(() => {
  if (store.recaptchaSiteKey) {
    loadRecaptcha(store.recaptchaSiteKey)
  }
})

watch(() => store.recaptchaSiteKey, (newVal) => {
  if (newVal) {
    loadRecaptcha(newVal)
  }
})

function loadRecaptcha(siteKey: string) {
  if (window.grecaptcha) {
    renderWidget(siteKey)
    return
  }

  const script = document.createElement('script')
  script.src = 'https://www.google.com/recaptcha/api.js?render=explicit'
  script.async = true
  script.defer = true
  script.onload = () => renderWidget(siteKey)
  document.head.appendChild(script)
}

function renderWidget(siteKey: string) {
  setTimeout(() => {
    if (document.getElementById('recaptcha-widget')) {
      window.grecaptcha.render('recaptcha-widget', {
        sitekey: siteKey,
        callback: (token: string) => {
          store.captchaToken = token
        },
        'expired-callback': () => {
          store.captchaToken = null
        }
      })
    }
  }, 100)
}
</script>

<script lang="ts">
declare global {
  interface Window {
    grecaptcha: any;
  }
}
</script>

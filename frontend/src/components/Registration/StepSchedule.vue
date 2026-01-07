<template>
  <div class="flex flex-col gap-6 pb-6">
    <!-- Event Header -->
    <div class="flex flex-col gap-1">
      <h1 class="text-3xl font-normal text-black leading-tight">
        {{ store.event?.title || 'Lafiye Unveils 2026' }}
      </h1>
      <p class="text-gray-500 text-lg">
        {{ formatDateRange(store.event?.starts_on, store.event?.ends_on) }}
      </p>
    </div>

    <!-- Section Header -->
    <div class="mt-4">
      <h3 class="text-lg font-medium text-black mb-2">Pilih slot sesuai waktu kedatangan yang diinginkan.</h3>
      <p class="text-black text-sm mt-1">Setiap akun (WhatsApp & email) hanya dapat mendaftar maksimal 2 slot dalam 1,
        untuk slot tambahan silahkan lakukan registrasi ulang dengan waktu berbeda
        hari.</p>
    </div>

    <div v-if="!store.selectedDate" class="text-gray-500">
      Please select a date in the previous step.
    </div>

    <div v-else class="grid grid-cols-1 gap-3">
      <div v-for="schedule in availableSchedules" :key="schedule.name"
        class="rounded-[16px] px-6 py-5 flex justify-between items-center transition-all cursor-pointer border relative"
        :class="[
          isFull(schedule) ? 'opacity-50 cursor-not-allowed bg-[#F3F4F6] border-transparent' : '',
          isSelected(schedule.name) ? 'bg-[#F9FAFB] border-gray-900 shadow-sm' : 'bg-[#F9FAFB] border-transparent hover:border-gray-200',
        ]" @click="toggleSchedule(schedule)">
        <div class="flex flex-col gap-1">
          <div class="text-[17px] font-bold text-gray-900 tracking-tight">
            {{ formatTime(schedule.start_time) }} - {{ formatTime(schedule.end_time) }}
          </div>
          <div class="text-[13px] text-gray-500 font-normal">
            Last Entry: {{ calculateLastEntry(schedule.end_time) }}
          </div>
        </div>

        <div v-if="isFull(schedule) && !isSelected(schedule.name)" class="text-[#DC2626] text-sm font-bold">
          Unavailable
        </div>
        <div v-else class="text-gray-900 text-sm font-bold">
          {{ isSelected(schedule.name) ? 'Selected' : 'Available' }}
        </div>
      </div>

      <div v-if="availableSchedules.length === 0" class="text-gray-500 py-4">
        No schedules available for this date.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRegistrationStore } from '@/stores/registration'

const store = useRegistrationStore()

const availableSchedules = computed(() => {
  if (!store.schedulesResource.data || !store.selectedDate) return []
  return store.schedulesResource.data.filter((s: any) => s.date === store.selectedDate.date)
})

function isFull(schedule: any) {
  if (schedule.max_capacity === 0) return false
  return schedule.enrolled_count >= schedule.max_capacity
}

function isSelected(scheduleName: string) {
  return store.selectedSchedules.includes(scheduleName)
}

function toggleSchedule(schedule: any) {
  if (isFull(schedule) && !isSelected(schedule.name)) return

  const index = store.selectedSchedules.indexOf(schedule.name)
  if (index === -1) {
    // Single select mode: Replace if exists
    store.selectedSchedules = [schedule.name]
  } else {
    store.selectedSchedules.splice(index, 1)
  }
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

function formatDateRange(start: string, end: string) {
  if (!start) return '23-25 January 2026'

  const startDate = new Date(start)
  const endDate = end ? new Date(end) : null

  // Format: "23-25 January 2026"
  const startDay = startDate.getDate()
  const month = startDate.toLocaleString('default', { month: 'long' })
  const year = startDate.getFullYear()

  if (endDate) {
    const endDay = endDate.getDate()
    if (startDate.getMonth() === endDate.getMonth()) {
      return `${startDay}-${endDay} ${month} ${year}`
    }
  }
  return `${startDate.toLocaleDateString()}`
}
</script>

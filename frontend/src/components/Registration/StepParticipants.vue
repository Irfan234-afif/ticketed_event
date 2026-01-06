<template>
  <div class="flex flex-col gap-8 pb-8">
    <!-- Participants Section -->
    <div>
      <h3 class="text-[16px] font-semibold text-gray-900 mb-3">Guest details</h3>

      <div class="space-y-3">
        <!-- Existing Participants (Not explicitly shown in empty state design but needed for logic) -->
        <div v-for="(participant, index) in store.participants" :key="index"
          class="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100">
          <div class="flex items-center gap-3">
            <!-- Simple Avatar -->
            <div
              class="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center text-xs text-gray-600 font-medium">
              {{ getInitials(participant.full_name) }}
            </div>
            <div class="flex flex-col">
              <span class="font-medium text-gray-900 text-sm">{{ participant.full_name || 'Guest ' + (index + 1)
                }}</span>
              <span class="text-gray-500 text-xs">{{ participant.email }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <Button icon="edit" variant="ghost" class="text-gray-400 h-7 w-7" @click="editParticipant(index)" />
            <Button v-if="store.participants.length > 1" @click="store.removeParticipant(index)" variant="ghost"
              class="text-gray-400 hover:text-red-500 !p-0">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M12 21C16.9706 21 21 16.9706 21 12C21 7.02944 16.9706 3 12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21Z"
                  fill="black" fill-opacity="0.25" />
                <path d="M16 12H8" stroke="black" stroke-width="1.2" stroke-linecap="square" stroke-linejoin="round" />
              </svg>
            </Button>
          </div>
        </div>

        <!-- Add Guest Button -->
        <button v-if="store.participants.length < 3" @click="openAddModal"
          class="w-full text-left p-4 bg-gray-50 rounded-xl flex justify-start text-gray-900 font-semibold text-[15px] hover:bg-gray-100 transition-colors">
          Add guest
        </button>
      </div>

      <p class="mt-4 text-[13px] leading-relaxed text-dark">
        Setiap akun yang digunakan untuk registrasi kedatangan dapat mendaftarkan maksimal 3 peserta.
      </p>
    </div>

    <!-- Date Selection Section -->
    <div>
      <h3 class="text-[16px] font-semibold text-gray-900 mb-3">Select your arrival date</h3>

      <div v-if="store.schedulesResource.loading" class="flex justify-center p-4">
        <LoadingIndicator />
      </div>
      <div v-else-if="uniqueDates.length === 0" class="text-gray-500 text-sm py-2">
        No dates available.
      </div>

      <!-- Date List (Vertical) -->
      <div v-else class="flex flex-col gap-3">
        <button v-for="(date, index) in uniqueDates" :key="String(date)"
          class="bg-gray-50 w-full py-4 px-6 rounded-xl text-left transition-all text-[15px]" :class="[
            store.selectedDate?.date === date.date
              ? 'shadow-xl border-[0.5px] border-black'
              : 'text-gray-900 hover:bg-gray-100'
          ]" @click="selectDate(date)">
          <span class="font-bold">{{ date.title }}</span>
          <span class="font-normal"> - {{ formatDate(date.date) }}</span>
        </button>
      </div>
    </div>

    <!-- Modal -->
    <AddParticipantModal v-model:show="showModal" :participant="editingParticipant" :is-edit="editingIndex !== -1"
      @save="handleSave" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useRegistrationStore } from '@/stores/registration'
import { Button, LoadingIndicator } from 'frappe-ui'
import AddParticipantModal from './AddParticipantModal.vue'

const store = useRegistrationStore()
const showModal = ref(false)
const editingIndex = ref(-1)
const editingParticipant = ref<any>(null)

const uniqueDates = computed(() => {
  if (!store.schedulesResource.data) return []
  const dates = store.schedulesResource.data.map((s: any) => {
    return { date: s.date, title: s.title }
  })
  return dates.filter((date: any, index: number, self: any[]) =>
    index === self.findIndex((t: any) => (
      t.date === date.date
    ))
  )
})

function selectDate(date: any) {
  store.selectedDate = date
  store.selectedSchedules = []
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'long', year: 'numeric' }).format(date)
}

function getInitials(name: string) {
  if (!name) return '?'
  return name.split(' ').map((n) => n[0]).join('').substring(0, 2).toUpperCase()
}

function openAddModal() {
  editingIndex.value = -1
  editingParticipant.value = null
  showModal.value = true
}

function editParticipant(index: number) {
  editingIndex.value = index
  editingParticipant.value = { ...store.participants[index] }
  showModal.value = true
}

function handleSave(participant: any) {
  if (editingIndex.value === -1) {
    store.participants.push(participant)
  } else {
    store.participants[editingIndex.value] = participant
  }
}

onMounted(() => {
  if (store.participants.length === 0) {
    store.addUserAsParticipant()
  }
})
</script>

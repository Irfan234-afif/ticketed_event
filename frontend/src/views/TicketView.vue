<template>
  <div class="max-w-lg mx-auto p-6 min-h-screen bg-white flex flex-col" v-if="registration.data">
    <!-- Header -->
    <div class="mb-8 mt-4">
      <h1 class="text-[24px] leading-tight font-normal text-black mb-4">Thank You for Registering</h1>
      <p class="text-[#969696] text-[14px] leading-[20px]">
        Your registration for {{ registration.data.event }} has been successfully submitted. Your arrival barcode will be sent to your email. Please present it upon arrival.
      </p>
    </div>

    <!-- Tickets List -->
    <div class="mb-8">
      <h2 class="text-[16px] mb-4">Your e-ticket.</h2>
      <div 
        v-for="p in participants" 
        :key="p.name"
        @click="openQR(p)"
        class="bg-[#F4F4F4] rounded-[10px] p-4 mb-3 flex flex-col justify-center cursor-pointer hover:bg-gray-200 transition-colors"
      >
        <div class="font-semibold text-[16px] text-black">{{ p.full_name }}</div>
        <div class="text-[12px] text-black mt-1">View or download</div>
      </div>
    </div>

    <!-- Important Notice -->
    <div class="text-[12px] leading-[20px] text-black">
      <p class="font-semibold mb-0">Important notice:</p>
      <p class="mb-0">Harap mematuhi Syarat & Ketentuan yang berlaku.</p>
      <p class="mb-0">Datang sesuai waktu yang telah dipilih.</p>
      <p class="mb-0">Batas masuk venue adalah 20 menit sebelum slot berakhir.</p>
    </div>
    <!-- Back to Home Button -->
    <div class="mb-4 mt-auto">
      <button 
        @click="router.push('/')" 
        class="w-full bg-black text-white py-4 rounded-full text-[16px] font-medium"
      >
        Back to Home
      </button>
    </div>
  </div>
  <div v-else class="flex h-screen items-center justify-center">
    <LoadingIndicator />
  </div>
  <!-- QR Modal -->
  <BottomSheet :show="showQR" @update:show="showQR = $event" @close="closeQR">
    <template #header>
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
         <div class="font-bold text-lg">E-ticket | {{ schedule?.title || 'Event' }}</div>
         <button @click="closeQR" class="text-sm text-black font-medium">Cancel</button>
      </div>
    </template>
    
    <div class="p-6 flex flex-col items-center text-center">
      <p class="text-[16px] text-black mb-6 w-full max-w-[280px] leading-snug">
        Show this QR to our staff to enter our exhibition.
      </p>

      <!-- QR Code -->
      <div class="border rounded-xl p-4 shadow-sm mb-6 bg-white">
         <img 
            v-if="selectedParticipant?.qr_code_id"
            :src="getQRUrl(selectedParticipant.qr_code_id)" 
            alt="QR Code" 
            class="w-48 h-48 block"
         />
      </div>

      <h3 class="font-bold text-[18px] mb-1">{{ selectedParticipant?.full_name }}</h3>
      <p class="text-[14px] text-gray-500 mb-8" v-if="schedule">
          {{ formatSchedule(schedule) }}
      </p>

      <button class="w-full bg-black text-white py-4 rounded-full text-[16px] font-medium" @click="downloadQR">
          Save to your phone
      </button>
    </div>
  </BottomSheet>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource, Button, LoadingIndicator } from 'frappe-ui'
import BottomSheet from '@/components/Common/BottomSheet.vue'

const route = useRoute()
const router = useRouter()
const registrationId = route.params.id as string

const registrationDetails = createResource({
  url: 'ticketed_event.api.get_registration_details',
  params: { name: registrationId },
  auto: true
})

const registration = computed(() => ({
    data: registrationDetails.data?.registration
}))

const participants = computed(() => registrationDetails.data?.participants || [])
const schedule = computed(() => registrationDetails.data?.schedule)

const showQR = ref(false)
const selectedParticipant = ref<any>(null)

function openQR(p: any) {
    selectedParticipant.value = p
    showQR.value = true
}

function closeQR() {
    showQR.value = false
    selectedParticipant.value = null
}

function getQRUrl(id: string) {
    if (!id) return ''
    return `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${id}`
}

function formatSchedule(s: any) {
    if (!s) return ''
    const start = s.start_time ? s.start_time.substring(0, 5) : ''
    const end = s.end_time ? s.end_time.substring(0, 5) : ''
    return `${start} - ${end}`
}

function downloadQR() {
    if (!selectedParticipant.value?.qr_code_id) return
    const url = getQRUrl(selectedParticipant.value.qr_code_id)
    
    // Create a link and click it to download
    // Since it's a cross-origin image, simple download attribute might not work without blob.
    // For now, just open in new tab or similar if download fails.
    // Actually api.qrserver.com returns an image.
    
    fetch(url)
      .then(response => response.blob())
      .then(blob => {
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `ticket-${selectedParticipant.value.full_name}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      })
      .catch(console.error);
}
</script>

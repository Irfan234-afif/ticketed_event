<template>
  <div class="flex flex-col h-full bg-white relative">
    <!-- Header (Hidden on Step 1) -->
    <header v-if="store.currentStep > 1" class="bg-white border-b px-6 py-4 flex items-center justify-between sticky top-0 z-10 shrink-0">
      <div class="font-bold text-xl text-black">Event Registration</div>
      <div class="text-sm text-gray-500">Step {{ store.currentStep }} of 5</div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 w-full mx-auto p-6 overflow-y-auto">
      <div class="h-full">
        <div v-if="loadingEvent" class="flex h-full items-center justify-center min-h-[200px]">
             <LoadingIndicator />
        </div>
        <div v-else>
            <Transition name="fade" mode="out-in">
                <component :is="currentStepComponent" />
            </Transition>
        </div>
      </div>
    </main>

    <!-- Footer Actions -->
    <footer class="bg-white border-t px-6 py-4 sticky bottom-0 z-10 shrink-0 mt-auto">
      <div class="w-full flex justify-between gap-3">
        <!-- Back Button (Hidden on Step 1) -->
        <Button 
          v-if="store.currentStep > 1" 
          variant="outline" 
          size="xl"
          @click="goBack"
          :disabled="store.submitRegistration.loading"
        >
          Back
        </Button>
        <div v-else class="hidden"></div> 

        <!-- Next / Register / Confirm Button -->
        <Button 
            v-if="store.currentStep < 5"
            variant="solid" 
            class="flex-1 !bg-black !text-white hover:!bg-gray-800"
            size="xl"
            @click="nextStep"
            :loading="store.submitRegistration.loading"
        >
          {{ store.currentStep === 1 ? 'Register' : 'Next' }}
        </Button>
        <Button 
            v-else
            variant="solid" 
            theme="gray"
            class="flex-1 !bg-black !text-white hover:!bg-gray-800"
            size="xl"
            @click="submit"
            :loading="store.submitRegistration.loading"
        >
          Confirm & Register
        </Button>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRegistrationStore } from '@/stores/registration'
import { createResource, Button, LoadingIndicator } from 'frappe-ui'

// Components
import StepInfo from '@/components/Registration/StepInfo.vue'
import StepUser from '@/components/Registration/StepUser.vue'
import StepParticipants from '@/components/Registration/StepParticipants.vue'
import StepSchedule from '@/components/Registration/StepSchedule.vue'
import StepConfirmation from '@/components/Registration/StepConfirmation.vue'

const route = useRoute()
const router = useRouter()
const store = useRegistrationStore()

const props = defineProps<{
  eventId?: string
}>()

const emit = defineEmits(['close'])

const loadingEvent = ref(true)

const currentStepComponent = computed(() => {
  switch (store.currentStep) {
    case 1: return StepInfo
    case 2: return StepUser
    case 3: return StepParticipants
    case 4: return StepSchedule
    case 5: return StepConfirmation
    default: return StepInfo
  }
})

// Fetch Event Details
const eventResource = createResource({
    url: 'ticketed_event.api.get_event_details',
    params: {
        name: props.eventId
    },
    onSuccess(data: any) {
        if (props.eventId) {
            store.setEvent(props.eventId, data)
            loadingEvent.value = false
        }
    }
})

onMounted(() => {
    store.reset()
    if (props.eventId) {
        eventResource.fetch()
    }
})

function validateStep() {
    if (store.currentStep === 2) {
        if (!store.user.full_name || !store.user.email || !store.user.phone) {
            // Using alert for now, could be better UI
            alert('Please fill in all fields')
            return false
        }
    }
    if (store.currentStep === 3) {
         if (store.participants.length === 0) {
            alert('Please add at least one participant')
            return false
        }
        if (!store.participants.every((p: any) => p.full_name && p.email && p.phone)) {
            alert('Please fill details for all participants')
            return false
        }
    }
    if (store.currentStep === 4) {
         // Step 4 logic depending on design changes? 
         // Assuming schedule selection logic stays same for now
         if (!store.selectedDate) {
             alert('Please select a date')
             return false
        }
        if (store.selectedSchedules.length === 0) {
            alert('Please select at least one time slot')
            return false
        }
    }
    return true
}

function goBack() {
    store.clearErrors()
    store.currentStep--
}

function nextStep() {
    if (validateStep()) {
        store.currentStep++
    }
}

function submit() {
    store.submitRegistration.submit({}, {
        onSuccess(data: any) {
            if (data.registration && data.registration.length > 0) {
                 // Close the sheet? Navigate?
                 // Design might want a success screen inside the sheet or redirect.
                 // Show first registration in URL for now, or maybe a summary page?
                 // Let's assume TicketRequest view can handle list or we just show the first one.
                 // The backend returns a list of registration names: ["REG-...", "REG-..."]
                 // If we go to TicketRequest with just one ID, the user sees one.
                 // Maybe we should update the router to show a success page for the batch?
                 // For now, let's just pick the first one which is safe as a fallback.
                 const regId = Array.isArray(data.registration) ? data.registration[0] : data.registration
                 router.push({ name: 'TicketRequest', params: { id: regId } })
                 emit('close')
            }
        },
        onError(err: any) {
            console.error(err)
            const message = err.messages ? err.messages.join('\n') : err.message
            alert(message || 'Registration failed')
        }
    })
}
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

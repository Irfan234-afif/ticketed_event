<template>
  <div class="relative h-screen w-full overflow-hidden bg-gray-50">
    <!-- Loading State -->
    <div v-if="events.loading" class="flex h-full items-center justify-center">
      <LoadingIndicator />
    </div>

    <!-- Error/No Events -->
    <div v-else-if="!events.data || events.data.length === 0" class="flex h-full items-center justify-center flex-col gap-4 text-center p-6">
        <h1 class="text-2xl font-bold text-gray-500">No Active Events</h1>
        <p class="text-gray-400">Please check back later.</p>
    </div>

    <!-- Landing Content -->
    <div v-else class="h-full relative flex flex-col">
        <!-- Background Image (Placeholder or Event Image) -->
        <div class="absolute inset-0 z-0">
             <img 
                :src="events.data[0].image || 'https://placehold.co/600x800'" 
                class="w-full h-full object-cover"
                alt="Event Background"
            />
            <div class="absolute inset-0 bg-black/10"></div>
        </div>

        <!-- Content Overlay -->
        <div class="relative z-10 flex flex-col h-full justify-end p-6 pb-12">

            <!-- Bottom Section -->
            <div class="flex flex-col gap-6 mb-24">
                 <div>
                     <h1 class="text-[32px] leading-tight font-normal text-dark mb-2">
                        {{ events.data[0].title }}
                     </h1>
                 </div>
                 
                 <button 
                    @click="openRegistration"
                    class="py-4 px-20 bg-black text-white rounded-full text-lg font-medium shadow-lg hover:bg-gray-900 transition-colors w-fit"
                >
                    Register Now
                 </button>
            </div>
        </div>
    </div>

    <!-- Bottom Sheet / Wizard -->
    <BottomSheet v-model:show="showWizard" full-height @close="closeRegistration">
        <RegistrationWizard 
            v-if="events.data && events.data[0]"
            :event-id="events.data[0].name" 
            @close="closeRegistration"
         />
    </BottomSheet>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createListResource, createResource, LoadingIndicator } from 'frappe-ui'
import RegistrationWizard from './RegistrationWizard.vue'
import BottomSheet from '../components/Common/BottomSheet.vue'

const showWizard = ref(false)

const events = createResource({
  url: 'ticketed_event.api.get_published_events',
  auto: true
})

function openRegistration() {
    showWizard.value = true
}

function closeRegistration() {
    showWizard.value = false
}
</script>

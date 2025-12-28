<template>
    <div class="relative h-screen w-full overflow-hidden bg-gray-50">
        <!-- Loading State -->
        <div v-if="events.loading" class="flex h-full items-center justify-center">
            <LoadingIndicator />
        </div>

        <!-- Error/No Events -->
        <div v-else-if="!events.data || events.data.length === 0"
            class="flex h-full items-center justify-center flex-col gap-4 text-center p-6">
            <h1 class="text-2xl font-bold text-gray-500">No Active Events</h1>
            <p class="text-gray-400">Please check back later.</p>
        </div>

        <!-- Landing Content -->
        <div v-else class="h-full relative flex flex-col">
            <div class="absolute inset-0 z-0">
                <!-- Desktop View (md+) -->
                <div class="hidden md:block w-full h-full">
                    <video v-if="events.data[0].video_landscape || events.data[0].video_portrait" playsinline autoplay
                        loop muted preload="metadata" class="w-full h-full object-cover"
                        :poster="events.data[0].image || 'https://placehold.co/600x800'">
                        <source :src="events.data[0].video_landscape || events.data[0].video_portrait" type="video/mp4">
                        <img :src="events.data[0].image || 'https://placehold.co/600x800'" alt="Event Background">
                    </video>
                    <img v-else :src="events.data[0].image || 'https://placehold.co/600x800'"
                        class="w-full h-full object-cover" alt="Event Background" />
                </div>

                <!-- Mobile View (Default) -->
                <div class="block md:hidden w-full h-full">
                    <video v-if="events.data[0].video_portrait || events.data[0].video_landscape" playsinline autoplay
                        loop muted preload="metadata" class="w-full h-full object-cover"
                        :poster="events.data[0].image || 'https://placehold.co/600x800'">
                        <source :src="events.data[0].video_portrait || events.data[0].video_landscape" type="video/mp4">
                        <img :src="events.data[0].image || 'https://placehold.co/600x800'" alt="Event Background">
                    </video>
                    <img v-else :src="events.data[0].image || 'https://placehold.co/600x800'"
                        class="w-full h-full object-cover" alt="Event Background" />
                </div>

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

                    <button @click="openRegistration"
                        class="py-4 px-20 bg-black text-white rounded-full text-lg font-medium shadow-lg hover:bg-gray-900 transition-colors w-fit">
                        Register Now
                    </button>

                    <button @click="openCheckTicket"
                        class="text-black text-left font-medium text-[15px] underline hover:text-gray-700 transition-colors">
                        Already have a ticket?
                    </button>
                </div>
            </div>
        </div>

        <!-- Bottom Sheet / Wizard -->
        <BottomSheet v-model:show="showWizard" full-height @close="closeRegistration">
            <RegistrationWizard v-if="events.data && events.data[0]" :event-id="events.data[0].name"
                @close="closeRegistration" />
        </BottomSheet>

        <!-- Check Ticket Modal -->
        <BottomSheet v-model:show="showCheckTicket" @close="closeCheckTicket">
            <div class="p-6 flex flex-col gap-5">
                <div>
                    <h2 class="text-xl font-bold mb-1">Check Ticket</h2>
                    <p class="text-sm text-gray-500">Enter your Registration ID and Email to access your ticket.</p>
                </div>

                <div class="flex flex-col gap-4">
                    <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-semibold uppercase text-gray-500 tracking-wider">Registration
                            ID</label>
                        <input v-model="checkTicketForm.registrationId" type="text" placeholder="e.g. LFY-XH59A"
                            class="bg-gray-50 border border-gray-200 rounded-lg p-3 w-full text-base focus:outline-none focus:border-black transition-colors placeholder:text-gray-400" />
                    </div>
                    <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-semibold uppercase text-gray-500 tracking-wider">Email</label>
                        <input v-model="checkTicketForm.email" type="email" placeholder="email@example.com"
                            class="bg-gray-50 border border-gray-200 rounded-lg p-3 w-full text-base focus:outline-none focus:border-black transition-colors placeholder:text-gray-400" />
                    </div>
                </div>

                <div v-if="checkTicketError"
                    class="bg-red-50 text-red-600 text-sm p-3 rounded-lg flex items-start gap-2">
                    <span>{{ checkTicketError }}</span>
                </div>

                <Button :loading="checkTicketResource.loading" @click="submitCheckTicket" variant="solid"
                    class="w-full !bg-black !text-white !h-12 !text-base !rounded-full mt-2">
                    Find Ticket
                </Button>
            </div>
        </BottomSheet>

    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { createListResource, createResource, LoadingIndicator, Button } from 'frappe-ui'
import { useRouter } from 'vue-router'
import RegistrationWizard from './RegistrationWizard.vue'
import BottomSheet from '../components/Common/BottomSheet.vue'

const router = useRouter()

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

// Check Ticket Logic
const showCheckTicket = ref(false)
const checkTicketForm = reactive({
    registrationId: '',
    email: ''
})
const checkTicketError = ref('')

const checkTicketResource = createResource({
    url: 'ticketed_event.api.verify_ticket_access',
    makeParams() {
        return {
            registration_id: checkTicketForm.registrationId,
            email: checkTicketForm.email
        }
    },
    onSuccess(data: any) {
        if (data.access) {
            router.push({
                name: 'TicketRequest',
                params: { id: checkTicketForm.registrationId }
            })
            closeCheckTicket()
        }
    },
    onError(err: any) {
        checkTicketError.value = err.messages ? err.messages.join('\n') : err.message
    }
})

function openCheckTicket() {
    showCheckTicket.value = true
    checkTicketForm.registrationId = ''
    checkTicketForm.email = ''
    checkTicketError.value = ''
}

function closeCheckTicket() {
    showCheckTicket.value = false
}

function submitCheckTicket() {
    checkTicketError.value = ''
    if (!checkTicketForm.registrationId || !checkTicketForm.email) {
        checkTicketError.value = 'Please fill in all fields'
        return
    }
    checkTicketResource.submit()
}
</script>

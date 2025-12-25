<template>
  <BottomSheet 
    :show="show" 
    @update:show="$emit('update:show', $event)"
  >
    <template #header>
        <div class="flex items-center justify-between px-6 py-5 border-b border-gray-100/50">
          <h3 class="text-[17px] font-bold text-gray-900">
            Enter your details
          </h3>
          <button 
            class="text-[15px] text-gray-900 font-normal hover:opacity-70 transition-opacity"
            @click="$emit('update:show', false)"
          >
            Cancel
          </button>
        </div>
    </template>

    <div class="px-5 py-6">
      <div class="flex flex-col gap-3">
        <!-- Full Name -->
        <div class="group">
          <input
            type="text"
            v-model="localParticipant.full_name"
            class="w-full bg-[#F5F5F5] text-gray-900 placeholder:text-gray-500 rounded-xl px-4 py-3.5 text-[15px] focus:outline-none focus:ring-1 focus:ring-gray-300 transition-all font-medium"
            placeholder="Full Name"
          />
        </div>

        <!-- Email -->
        <div class="group">
          <input
            type="email"
            v-model="localParticipant.email"
            class="w-full bg-[#F5F5F5] text-gray-900 placeholder:text-gray-500 rounded-xl px-4 py-3.5 text-[15px] focus:outline-none focus:ring-1 focus:ring-gray-300 transition-all font-medium"
            placeholder="Email address"
          />
        </div>

        <!-- Phone -->
        <div class="group">
          <input
            type="tel"
            v-model="localParticipant.phone"
            class="w-full bg-[#F5F5F5] text-gray-900 placeholder:text-gray-500 rounded-xl px-4 py-3.5 text-[15px] focus:outline-none focus:ring-1 focus:ring-gray-300 transition-all font-medium"
            placeholder="WhatsApp Number"
          />
        </div>

        <!-- Instagram -->
        <div class="group">
          <input
            type="text"
            v-model="localParticipant.instagram"
            class="w-full bg-[#F5F5F5] text-gray-900 placeholder:text-gray-500 rounded-xl px-4 py-3.5 text-[15px] focus:outline-none focus:ring-1 focus:ring-gray-300 transition-all font-medium"
            placeholder="Instagram (Optional)"
          />
        </div>

        <!-- Save Button -->
        <div class="mt-4">
          <button 
            class="w-full py-3.5 rounded-full text-white font-medium text-[16px] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            :class="isValid ? 'bg-black hover:bg-gray-800' : 'bg-[#B3B3B3]'"
            :disabled="!isValid"
            @click="save"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  </BottomSheet>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import BottomSheet from '../Common/BottomSheet.vue'

const props = defineProps<{
  show: boolean
  participant?: any
  isEdit?: boolean
}>()

const emit = defineEmits(['update:show', 'save'])

const localParticipant = ref({
  full_name: '',
  email: '',
  phone: '',
  instagram: ''
})

const isValid = computed(() => {
  return localParticipant.value.full_name && 
         localParticipant.value.email && 
         localParticipant.value.phone
})

watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.participant) {
      localParticipant.value = { ...props.participant }
    } else {
      localParticipant.value = { full_name: '', email: '', phone: '', instagram: '' }
    }
  }
})

function save() {
  if (!isValid.value) return
  emit('save', localParticipant.value)
  emit('update:show', false)
}
</script>

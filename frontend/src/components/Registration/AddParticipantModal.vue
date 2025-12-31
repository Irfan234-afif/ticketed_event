<template>
  <BottomSheet :show="show" @update:show="$emit('update:show', $event)">
    <template #header>
      <div class="flex items-center justify-between px-6 py-5 border-b border-gray-100/50">
        <h3 class="text-[17px] font-bold text-gray-900">
          Enter your details
        </h3>
        <button class="text-[15px] text-gray-900 font-normal hover:opacity-70 transition-opacity"
          @click="$emit('update:show', false)">
          Cancel
        </button>
      </div>
    </template>

    <div class="px-5 py-6">
      <div class="flex flex-col gap-3">
        <!-- Type -->
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-semibold uppercase text-gray-500 tracking-wider">Registration Type</label>
          <div class="relative">
            <select v-model="localParticipant.type"
              class="bg-gray-50 border border-gray-200 rounded-lg p-3 w-full text-base focus:outline-none focus:border-black transition-colors placeholder:text-gray-400 appearance-none">
              <option value="Personal">Personal</option>
              <option value="Jastiper">Jastiper</option>
            </select>
            <div class="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none text-gray-500">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Full Name -->
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-semibold uppercase text-gray-500 tracking-wider">Full Name</label>
          <input type="text" v-model="localParticipant.full_name"
            class="bg-gray-50 border border-gray-200 rounded-lg p-3 w-full text-base focus:outline-none focus:border-black transition-colors placeholder:text-gray-400"
            placeholder="e.g. John Doe" />
        </div>

        <!-- Email -->
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-semibold uppercase text-gray-500 tracking-wider">Email</label>
          <input type="email" v-model="localParticipant.email"
            class="bg-gray-50 border rounded-lg p-3 w-full text-base focus:outline-none transition-colors placeholder:text-gray-400"
            :class="errors.email ? 'border-red-500 focus:border-red-500' : 'border-gray-200 focus:border-black'"
            placeholder="email@example.com" @blur="validateField('email')" />
          <span v-if="errors.email" class="text-red-500 text-xs">{{ errors.email }}</span>
        </div>

        <!-- Phone -->
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-semibold uppercase text-gray-500 tracking-wider">Phone Number</label>
          <input type="tel" v-model="localParticipant.phone"
            class="bg-gray-50 border rounded-lg p-3 w-full text-base focus:outline-none transition-colors placeholder:text-gray-400"
            :class="errors.phone ? 'border-red-500 focus:border-red-500' : 'border-gray-200 focus:border-black'"
            placeholder="e.g. 08123456789" @blur="validateField('phone')" />
          <span v-if="errors.phone" class="text-red-500 text-xs">{{ errors.phone }}</span>
        </div>

        <!-- Instagram -->
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-semibold uppercase text-gray-500 tracking-wider">Instagram</label>
          <input type="text" v-model="localParticipant.instagram"
            class="bg-gray-50 border border-gray-200 rounded-lg p-3 w-full text-base focus:outline-none focus:border-black transition-colors placeholder:text-gray-400"
            placeholder="@username" />
        </div>

        <!-- Save Button -->
        <div class="mt-4">
          <button
            class="w-full py-3.5 rounded-full text-white font-medium text-[16px] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            :class="isValid ? 'bg-black hover:bg-gray-800' : 'bg-[#B3B3B3]'" :disabled="!isValid" @click="save">
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
import { validateEmail, validatePhone } from '@/utils/validators'

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
  instagram: '',
  type: 'Personal'
})

const errors = ref({
  email: '',
  phone: ''
})

const validateField = (field: 'email' | 'phone') => {
  if (field === 'email') {
    if (!localParticipant.value.email) {
      errors.value.email = 'Email is required'
    } else if (!validateEmail(localParticipant.value.email)) {
      errors.value.email = 'Invalid email format'
    } else {
      errors.value.email = ''
    }
  }

  if (field === 'phone') {
    if (!localParticipant.value.phone) {
      errors.value.phone = 'Phone number is required'
    } else if (!validatePhone(localParticipant.value.phone)) {
      errors.value.phone = 'Invalid phone number format'
    } else {
      errors.value.phone = ''
    }
  }
}

const isValid = computed(() => {
  const emailValid = validateEmail(localParticipant.value.email)
  const phoneValid = validatePhone(localParticipant.value.phone)

  return localParticipant.value.full_name &&
    localParticipant.value.email &&
    localParticipant.value.phone &&
    emailValid &&
    phoneValid
})

watch(() => props.show, (newVal) => {
  if (newVal) {
    errors.value = { email: '', phone: '' }
    if (props.participant) {
      localParticipant.value = { ...props.participant }
    } else {
      localParticipant.value = { full_name: '', email: '', phone: '', instagram: '', type: 'Personal' }
    }
  }
})

function save() {
  if (!isValid.value) return
  emit('save', localParticipant.value)
  emit('update:show', false)
}
</script>

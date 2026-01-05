<template>
  <div>
    <div class="flex items-center justify-between mb-5">
      <h3 class="text-[17px] font-bold text-gray-900">
        Your Information
      </h3>
    </div>

    <div class="flex flex-col gap-3">
      <!-- Type -->
      <div class="flex flex-col gap-1.5">
        <!-- <label class="text-xs font-semibold uppercase text-gray-500 tracking-wider">Registration Type</label> -->
        <div class="relative">
          <select v-model="store.user.type"
            class="bg-gray-50 border border-gray-200 rounded-lg p-3 w-full text-base focus:outline-none focus:border-black transition-colors placeholder:text-gray-400 appearance-none">
            <option value="Personal">Personal</option>
            <option value="Jastiper">Jastiper</option>
          </select>
          <!-- <div class="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none text-gray-500">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div> -->
        </div>
      </div>

      <!-- Full Name -->
      <div class="flex flex-col gap-1.5">
        <!-- <label class="text-xs font-semibold uppercase text-gray-500 tracking-wider">Full Name</label> -->
        <input type="text" v-model="store.user.full_name"
          class="bg-gray-50 border border-gray-200 rounded-lg p-3 w-full text-base focus:outline-none focus:border-black transition-colors placeholder:text-gray-400"
          placeholder="Full Name" required />
      </div>

      <!-- Email -->
      <div class="flex flex-col gap-1.5">
        <!-- <label class="text-xs font-semibold uppercase text-gray-500 tracking-wider">Email</label> -->
        <input type="email" v-model="store.user.email" @blur="validateField('email')"
          class="bg-gray-50 border rounded-lg p-3 w-full text-base focus:outline-none transition-colors placeholder:text-gray-400"
          :class="errors.email ? 'border-red-500 focus:border-red-500' : 'border-gray-200 focus:border-black'"
          placeholder="Email" required />
        <span v-if="errors.email" class="text-red-500 text-xs">{{ errors.email }}</span>
      </div>

      <!-- Phone -->
      <div class="flex flex-col gap-1.5">
        <!-- <label class="text-xs font-semibold uppercase text-gray-500 tracking-wider">Phone Number</label> -->
        <input type="tel" v-model="store.user.phone" @blur="validateField('phone')"
          class="bg-gray-50 border rounded-lg p-3 w-full text-base focus:outline-none transition-colors placeholder:text-gray-400"
          :class="errors.phone ? 'border-red-500 focus:border-red-500' : 'border-gray-200 focus:border-black'"
          placeholder="Phone Number" required />
        <span v-if="errors.phone" class="text-red-500 text-xs">{{ errors.phone }}</span>
      </div>

      <!-- Instagram -->
      <div class="flex flex-col gap-1.5">
        <!-- <label class="text-xs font-semibold uppercase text-gray-500 tracking-wider">Instagram</label> -->
        <input type="text" v-model="store.user.instagram"
          class="bg-gray-50 border border-gray-200 rounded-lg p-3 w-full text-base focus:outline-none focus:border-black transition-colors placeholder:text-gray-400"
          placeholder="Instagram" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRegistrationStore } from '@/stores/registration'
import { ref } from 'vue'
import { validateEmail, validatePhone } from '@/utils/validators'

const store = useRegistrationStore()
const errors = ref({
  email: '',
  phone: ''
})

const validateField = (field: 'email' | 'phone') => {
  let isValid = true
  if (field === 'email') {
    if (!store.user.email) {
      errors.value.email = 'Email is required'
      isValid = false
    } else if (!validateEmail(store.user.email)) {
      errors.value.email = 'Invalid email format'
      isValid = false
    } else {
      errors.value.email = ''
    }
  }

  if (field === 'phone') {
    if (!store.user.phone) {
      errors.value.phone = 'Phone number is required'
      isValid = false
    } else if (!validatePhone(store.user.phone)) {
      errors.value.phone = 'Invalid phone number format'
      isValid = false
    } else {
      errors.value.phone = ''
    }
  }
  return isValid
}

const validate = () => {
  const isEmailValid = validateField('email')
  const isPhoneValid = validateField('phone')
  return isEmailValid && isPhoneValid && !!store.user.full_name
}

defineExpose({
  validate
})
</script>

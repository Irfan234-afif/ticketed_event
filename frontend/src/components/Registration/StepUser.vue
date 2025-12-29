<template>
  <div>
    <div class="flex items-center justify-between mb-5">
      <h3 class="text-[17px] font-bold text-gray-900">
        Your Information
      </h3>
    </div>

    <div class="flex flex-col gap-3">
      <!-- Type -->
      <div class="group">
        <select v-model="store.user.type"
          class="w-full bg-[#F5F5F5] text-gray-900 placeholder:text-gray-500 rounded-xl px-4 py-3.5 text-[15px] focus:outline-none focus:ring-1 focus:ring-gray-300 transition-all font-medium appearance-none">
          <option value="Personal">Personal</option>
          <option value="Jastiper">Jastiper</option>
        </select>
      </div>

      <!-- Full Name -->
      <div class="group">
        <input type="text" v-model="store.user.full_name"
          class="w-full bg-[#F5F5F5] text-gray-900 placeholder:text-gray-500 rounded-xl px-4 py-3.5 text-[15px] focus:outline-none focus:ring-1 focus:ring-gray-300 transition-all font-medium"
          placeholder="Full Name" required />
      </div>

      <!-- Email -->
      <div class="group">
        <input type="email" v-model="store.user.email"
          class="w-full bg-[#F5F5F5] text-gray-900 placeholder:text-gray-500 rounded-xl px-4 py-3.5 text-[15px] focus:outline-none focus:ring-1 focus:ring-gray-300 transition-all font-medium"
          placeholder="Email Address" required />
      </div>

      <!-- Phone -->
      <div class="group">
        <input type="tel" v-model="store.user.phone"
          class="w-full bg-[#F5F5F5] text-gray-900 placeholder:text-gray-500 rounded-xl px-4 py-3.5 text-[15px] focus:outline-none focus:ring-1 focus:ring-gray-300 transition-all font-medium"
          placeholder="Phone Number" required />
      </div>

      <!-- Instagram -->
      <div class="group">
        <input type="text" v-model="store.user.instagram"
          class="w-full bg-[#F5F5F5] text-gray-900 placeholder:text-gray-500 rounded-xl px-4 py-3.5 text-[15px] focus:outline-none focus:ring-1 focus:ring-gray-300 transition-all font-medium"
          placeholder="Instagram Account" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRegistrationStore } from '@/stores/registration'

const store = useRegistrationStore()
</script>

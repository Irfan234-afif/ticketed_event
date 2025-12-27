<template>
  <div class="h-full flex flex-col">
    <div class="flex items-center justify-between mb-5 shrink-0">
      <h3 class="text-[17px] font-bold text-gray-900">
        Terms & Conditions
      </h3>
    </div>

    <!-- Terms text container -->
    <div class="flex-1 bg-white border border-gray-200 rounded-xl p-4 overflow-y-auto mb-5 text-gray-600">
        <!-- Render HTML content safely -->
        <div class="prose prose-sm max-w-none" v-html="store.event?.terms_text || 'No terms and conditions provided.'"></div>
    </div>

    <!-- Checkbox -->
    <div class="shrink-0">
        <label class="flex items-start gap-3 p-4 bg-[#F5F5F5] rounded-xl cursor-pointer hover:bg-gray-100 transition-colors">
            <input 
                type="checkbox" 
                v-model="store.termsAccepted"
                class="mt-1 w-4 h-4 rounded text-black focus:ring-black border-gray-300 accent-black"
            />
            <span class="text-[15px] font-medium text-gray-900 select-none">
                I agree to the Terms & Conditions
            </span>
        </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRegistrationStore } from '@/stores/registration'

const store = useRegistrationStore()
</script>

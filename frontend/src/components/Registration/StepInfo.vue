<template>
  <div v-if="store.event" class="flex flex-col pt-2 pb-6">
    <!-- Header/Title Section -->
    <div class="flex flex-col gap-1 mb-6">
      <h2 class="text-2xl font-normal text-gray-900 tracking-tight">{{ store.event.title }}</h2>
      <div class="flex items-center gap-2">
         <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
         </span>
         <span class="text-xs font-medium text-gray-500 uppercase tracking-wide">Available</span>
      </div>
    </div>

    <!-- Scrollable Content -->
    <div class="flex-1 overflow-y-auto">
      <div class="prose prose-p:text-sm prose-p:text-gray-600 prose-headings:font-normal prose-a:text-black hover:prose-a:text-gray-700 max-w-none" 
           v-html="store.event.description">
      </div>
      
      <!-- Static info from design if not in description -->
      <div class="mt-8 space-y-4 text-sm text-gray-500 border-t pt-4">
          <p>
            <span class="block font-medium text-gray-900 mb-1">Entry Requirement</span>
            Please present your QR code at the entrance.
          </p>
          <p>
             <span class="block font-medium text-gray-900 mb-1">Last Entry</span>
             20 minutes before time slot ends.
          </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRegistrationStore } from '@/stores/registration'

const store = useRegistrationStore()
</script>

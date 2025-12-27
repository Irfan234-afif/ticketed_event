<template>
  <div class="flex-1 flex items-center justify-center p-4">
    <div class="w-full max-w-lg bg-white p-6 rounded-2xl shadow-xl border border-gray-100 flex flex-col max-h-[80vh]">
       <div class="flex justify-between items-center mb-6 border-b border-gray-100 pb-4">
          <h1 class="text-2xl font-bold text-gray-900">Select Schedule</h1>
          <button @click="$emit('logout')" class="text-sm font-medium text-gray-500 hover:text-black transition-colors">Logout</button>
       </div>

       <div v-if="loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-200 border-t-black"></div>
          <p class="mt-2 text-gray-500">Loading schedules...</p>
       </div>
       
       <div v-else-if="!schedules || schedules.length === 0" class="text-center py-12 text-gray-500 bg-gray-50 rounded-xl border border-dashed border-gray-200">
          No schedules found for today.
       </div>

       <div v-else class="flex-1 overflow-y-auto space-y-3 pr-1 custom-scrollbar">
          <div 
            v-for="s in schedules" 
            :key="s.name"
            @click="$emit('select', s)"
            class="group bg-gray-50 hover:bg-white p-5 rounded-xl cursor-pointer transition-all border border-gray-100 hover:border-black hover:shadow-md"
          >
             <h3 class="font-bold text-lg mb-1 text-gray-900 group-hover:text-black">{{ s.title }}</h3>
             <div class="flex justify-between text-sm text-gray-600">
                <span class="flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  {{ formatTime(s.start_time) }} - {{ formatTime(s.end_time) }}
                </span>
             </div>
             <div class="text-xs font-medium text-gray-400 mt-3 pt-3 border-t border-gray-200">
                Last Entry: {{ s.last_entry_time ? formatTime(s.last_entry_time) : 'None' }}
             </div>
          </div>
       </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  loading: Boolean,
  schedules: Array
});

defineEmits(['logout', 'select']);

function formatTime(t: string) {
    if (!t) return '';
    return t.substring(0, 5);
}
</script>

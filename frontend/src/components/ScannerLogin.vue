<template>
  <div class="flex-1 flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
      <h1 class="text-3xl font-bold mb-8 text-center text-gray-900 tracking-tight">Scanner Login</h1>
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div class="space-y-2">
          <label class="block text-sm font-semibold uppercase text-gray-500 tracking-wider">Email / Username</label>
          <input
            v-model="form.usr"
            type="text"
            class="w-full px-4 py-3 rounded-lg bg-gray-50 border border-gray-200 focus:outline-none focus:border-black focus:ring-1 focus:ring-black transition-all text-gray-900 placeholder-gray-400"
            placeholder="Enter username"
            required
          />
        </div>
        <div class="space-y-2">
          <label class="block text-sm font-semibold uppercase text-gray-500 tracking-wider">Password</label>
          <input
            v-model="form.pwd"
            type="password"
            class="w-full px-4 py-3 rounded-lg bg-gray-50 border border-gray-200 focus:outline-none focus:border-black focus:ring-1 focus:ring-black transition-all text-gray-900 placeholder-gray-400"
            placeholder="Enter password"
            required
          />
        </div>
        <div v-if="error" class="p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
          {{ error }}
        </div>
        <button
          type="submit"
          class="w-full bg-black hover:bg-gray-900 text-white font-medium py-3.5 px-4 rounded-full shadow-lg transform active:scale-95 transition-all duration-200"
          :disabled="loading"
        >
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue';

const props = defineProps({
  loading: Boolean,
  error: String
});

const emit = defineEmits(['login']);

const form = reactive({
  usr: '',
  pwd: ''
});

function handleSubmit() {
  emit('login', { ...form });
}
</script>

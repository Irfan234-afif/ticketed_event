<template>
  <div class="h-screen w-screen bg-gray-50 text-gray-900 flex flex-col overflow-hidden font-sans">
    
    <!-- State 1: Login -->
    <ScannerLogin 
      v-if="viewState === 'login'"
      :loading="loginResource.loading"
      :error="loginError"
      @login="handleLogin"
    />

    <!-- State 2: Select Schedule -->
    <ScannerScheduleList 
      v-else-if="viewState === 'select_schedule'"
      :loading="schedulesResource.loading"
      :schedules="schedules"
      @logout="logout"
      @select="selectSchedule"
    />

    <!-- State 3: Scanning -->
    <ScannerActive 
      v-else-if="viewState === 'scanning'"
      :schedule="currentSchedule"
      :history="scanHistory"
      :result="currentResult"
      :showResultModal="showResultModal"
      :autoCloseTimer="autoCloseTimer"
      :loading="checkinResource.loading"
      @logout="logout"
      @changeSchedule="changeSchedule"
      @scan="onScanSuccess"
      @closeResult="closeResultModal"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { createResource } from 'frappe-ui';
import ScannerLogin from '@/components/ScannerLogin.vue';
import ScannerScheduleList from '@/components/ScannerScheduleList.vue';
import ScannerActive from '@/components/ScannerActive.vue';

// View State Management
const viewState = ref<'login' | 'select_schedule' | 'scanning'>('login');
const loginError = ref('');

// Current Session State
const currentSchedule = ref<any>(null);

interface ScanResult {
  status: 'success' | 'error';
  participant?: string;
  schedule?: string;
  message?: string;
  time: string;
}

const scanHistory = ref<ScanResult[]>([]);
const currentResult = ref<ScanResult | null>(null);
const showResultModal = ref(false);
const autoCloseTimer = ref(0);
let autoCloseInterval: any = null;

// Resources
const userResource = createResource({
  url: 'frappe.auth.get_logged_user',
  auto: false,
  onSuccess(data: any) {
    checkRoles(typeof data === 'string' ? data : data.message);
  },
  onError() {
    viewState.value = 'login';
  }
});

const rolesResource = createResource({
  url: 'frappe.core.doctype.user.user.get_roles',
  auto: false,
  onSuccess(data: any) {
    if (data && (data.includes('Scanner') || data.includes('System Manager') || data.includes('Administrator'))) {
       // Authenticated and Authorized
       // Go to Schedule Selection
       viewState.value = 'select_schedule';
       schedulesResource.fetch();
    } else {
       // Not authorized
       loginError.value = "Access Denied: You do not have 'Scanner' role.";
       viewState.value = 'login';
    }
  }
});

const schedulesResource = createResource({
    url: 'ticketed_event.api.get_scanner_schedules',
    auto: false
})
const schedules = computed(() => schedulesResource.data || [])


const loginResource = createResource({
  url: 'login',
  onSuccess(data: any) {
    loginError.value = '';
    userResource.fetch(); 
  },
  onError(error: any) {
    loginError.value = error.message || 'Login failed';
  }
});

// Check-in Resource
const checkinResource = createResource({
  url: 'ticketed_event.ticketed_event.doctype.event_registration.event_registration.check_in_participant',
  makeParams(qr_code_id: string) {
    return {
      qr_code_id: qr_code_id,
      schedule: currentSchedule.value?.name 
    }
  },
  onSuccess(data: any) {
    handleResult({
      status: 'success',
      participant: data.participant,
      schedule: data.schedule,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });
  },
  onError(error: any) {
    handleResult({
      status: 'error',
      message: error.messages?.[0] || error.message || 'Unknown Error',
      participant: 'Unknown User',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });
  }
});

function handleLogin(creds: any) {
  loginResource.submit({
    usr: creds.usr,
    pwd: creds.pwd
  });
}

function checkRoles(uid: string) {
    rolesResource.fetch({ uid: uid || 'Administrator' });
}

function logout() {
  fetch('/api/method/logout').then(() => {
      viewState.value = 'login';
      currentSchedule.value = null;
      window.location.reload(); 
  });
}

function selectSchedule(s: any) {
    currentSchedule.value = s;
    viewState.value = 'scanning';
}

function changeSchedule() {
    viewState.value = 'select_schedule';
    currentSchedule.value = null;
}

function onScanSuccess(decodedText: string) {
  if (checkinResource.loading || showResultModal.value) return;
  checkinResource.submit(decodedText);
}

function handleResult(result: ScanResult) {
    currentResult.value = result;
    scanHistory.value.unshift(result);
    showResultModal.value = true;
    
    // Auto close timer
    autoCloseTimer.value = 2; // 2 seconds
    clearInterval(autoCloseInterval);
    autoCloseInterval = setInterval(() => {
        autoCloseTimer.value--;
        if (autoCloseTimer.value <= 0) {
            closeResultModal();
        }
    }, 1000);
}

function closeResultModal() {
    clearInterval(autoCloseInterval);
    showResultModal.value = false;
    currentResult.value = null;
    // Scanner resuming is handled within ScannerActive via watcher
}

onMounted(() => {
  // Try to resume session
  userResource.fetch();
});
</script>

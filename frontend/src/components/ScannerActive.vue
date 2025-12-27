<template>
  <div class="flex flex-col h-full relative bg-gray-100">
    <!-- Navbar -->
    <div class="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200 shadow-sm z-20">
      <div>
         <div class="flex items-center gap-2">
             <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
             <h1 class="text-lg font-bold text-gray-900">Scanner Active</h1>
         </div>
         <p class="text-sm text-gray-500 cursor-pointer hover:text-black transition-colors flex items-center gap-1" @click="$emit('changeSchedule')">
            {{ schedule?.title }} ({{ formatTime(schedule?.start_time) }}) 
            <span class="bg-gray-100 px-1.5 py-0.5 rounded text-xs">Switch</span>
         </p>
      </div>
      <button @click="$emit('logout')" class="text-sm font-medium text-gray-500 hover:text-red-600 hover:bg-red-50 px-4 py-2 rounded-lg transition-colors">Logout</button>
    </div>

    <div class="flex-1 flex flex-col md:flex-row overflow-hidden relative">
      <!-- Left Panel: Camera -->
      <div class="flex-1 bg-gray-100 flex flex-col items-center justify-center p-4 relative">
        <div class="w-full max-w-2xl bg-white p-4 rounded-3xl shadow-xl border border-gray-200">
           <div class="relative rounded-2xl overflow-hidden bg-black aspect-square md:aspect-video mb-4 group">
               <div id="qr-reader" class="w-full h-full"></div>
               <!-- Scanner Overlay Guide -->
               <div class="absolute inset-0 border-[40px] border-black/50 pointer-events-none z-10">
                  <div class="w-full h-full border-2 border-white/50 rounded-lg relative shadow-[0_0_0_9999px_rgba(0,0,0,0.5)]">
                      <div class="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-white rounded-tl-lg"></div>
                      <div class="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-white rounded-tr-lg"></div>
                      <div class="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-white rounded-bl-lg"></div>
                      <div class="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-white rounded-br-lg"></div>
                  </div>
               </div>
           </div>
           <p class="text-center text-gray-500 text-sm font-medium">
              Scanning for <span class="text-black font-bold">{{ schedule?.title }}
               <span v-if="schedule?.start_time" class="text-gray-400 font-normal">({{ formatTime(schedule.start_time) }})</span>
              </span>
           </p>
        </div>
      </div>

      <!-- Right Panel: History (for Tablet/Desktop) -->
      <div class="w-full md:w-[380px] lg:w-[420px] bg-white border-l border-gray-200 flex flex-col shadow-xl z-10">
         <div class="p-5 bg-white border-b border-gray-100 flex justify-between items-center">
           <h2 class="font-bold text-lg text-gray-900">Recent Scans</h2>
           <span class="text-xs font-medium bg-gray-100 px-2 py-1 rounded text-gray-600">{{ history.length }} scans</span>
         </div>
         
         <div class="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar bg-gray-50/50">
           <div v-if="history.length === 0" class="flex flex-col items-center justify-center h-48 text-gray-400">
             <svg class="w-12 h-12 mb-3 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"></path></svg>
             <p class="text-sm">Ready to scan tickets</p>
           </div>
           
           <div 
              v-for="(scan, index) in history" 
              :key="index"
              :class="[
                'p-4 rounded-xl border shadow-sm flex flex-col relative transition-all',
                scan.status === 'success' ? 'bg-white border-green-200 hover:border-green-300' : 'bg-red-50 border-red-100'
              ]"
            >
              <div class="flex justify-between items-start mb-2">
                 <div class="font-bold text-gray-900">{{ scan.participant || 'Unknown Participant' }}</div>
                 <div class="text-xs font-medium text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">{{ scan.time }}</div>
              </div>
              
              <div v-if="scan.status === 'success'" class="flex items-center gap-1.5 text-xs font-bold text-green-600 uppercase tracking-wide">
                <span class="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                Checked In Successfully
              </div>
              <div v-else class="flex items-center gap-1.5 text-xs font-bold text-red-600 uppercase tracking-wide">
                 <span class="w-1.5 h-1.5 rounded-full bg-red-500"></span>
                 {{ scan.message }}
              </div>
           </div>
         </div>
      </div>
      
      <!-- Result Modal / Overlay -->
      <div v-if="showResultModal" class="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
           <div 
              class="bg-white p-8 rounded-3xl shadow-2xl max-w-sm w-full text-center transform transition-all scale-100 border border-gray-100"
              @click="$emit('closeResult')"
           >
              <div class="mb-6 flex justify-center">
                  <div v-if="result?.status === 'success'" class="w-24 h-24 rounded-full bg-green-100 flex items-center justify-center animate-bounce-in">
                      <svg class="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
                  </div>
                  <div v-else class="w-24 h-24 rounded-full bg-red-100 flex items-center justify-center animate-shake">
                       <svg class="w-12 h-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12"></path></svg>
                  </div>
              </div>
              
              <h2 
                :class="[
                  'text-3xl font-bold mb-3 tracking-tight',
                  result?.status === 'success' ? 'text-green-600' : 'text-red-600'
                ]"
              >
                {{ result?.status === 'success' ? 'Checked In!' : 'Check In Failed' }}
              </h2>
              
              <div v-if="result?.status === 'success'" class="bg-gray-50 rounded-xl p-4 mb-2">
                 <p class="text-xl text-gray-900 font-bold mb-1">{{ result?.participant }}</p>
                 <p class="text-sm text-gray-500 font-medium uppercase tracking-wide">{{ result?.schedule || 'Event Access' }}</p>
              </div>
              <div v-else class="bg-red-50 rounded-xl p-4 mb-2">
                 <p class="text-red-800 font-medium">{{ result?.message }}</p>
              </div>

              <div class="mt-8">
                 <button 
                   @click="$emit('closeResult')"
                   class="w-full bg-black hover:bg-gray-800 text-white font-bold py-4 px-6 rounded-full transition-all shadow-lg active:scale-95 flex items-center justify-center gap-2"
                 >
                   <span>Tap to Scan Next</span>
                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                 </button>
                 <div class="mt-4 flex items-center justify-center gap-2">
                      <div class="h-1 bg-gray-200 rounded-full w-24 overflow-hidden">
                          <div class="h-full bg-gray-400 transition-all duration-1000 ease-linear" :style="{ width: (autoCloseTimer/2)*100 + '%' }"></div>
                      </div>
                 </div>
              </div>
           </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, type PropType } from 'vue';
import { Html5Qrcode } from 'html5-qrcode';

interface ScanResult {
  status: 'success' | 'error';
  participant?: string;
  schedule?: string;
  message?: string;
  time: string;
}

const props = defineProps({
  schedule: Object as PropType<any>, // Using any for schedule for now as per previous code
  history: {
    type: Array as PropType<ScanResult[]>,
    default: () => []
  },
  result: Object as PropType<ScanResult | null>,
  showResultModal: Boolean,
  autoCloseTimer: Number,
  loading: Boolean
});

const emit = defineEmits(['logout', 'changeSchedule', 'scan', 'closeResult']);

const scanner = ref<Html5Qrcode | null>(null);

function formatTime(t: string) {
    if (!t) return '';
    return t.substring(0, 5);
}

function initScanner() {
  nextTick(() => {
    if (scanner.value) return;
    
    // Use Html5Qrcode directly for better UI control (no default dashboard)
    const html5QrCode = new Html5Qrcode("qr-reader");
    
    const config = { 
        fps: 10, 
        aspectRatio: 1.0
    };

    // Attempt to find back camera
    Html5Qrcode.getCameras().then(cameras => {
        let cameraIdOrConfig: string | { facingMode: string } = { facingMode: "environment" };

        if (cameras && cameras.length) {
            const backCamera = cameras.find(camera => 
                camera.label.toLowerCase().includes('back') || 
                camera.label.toLowerCase().includes('rear')
            );
            
            if (backCamera) {
                cameraIdOrConfig = backCamera.id;
            }
        }

        return html5QrCode.start(
            cameraIdOrConfig, 
            config, 
            (decodedText) => {
                if(!props.loading && !props.showResultModal) {
                     scanner.value?.pause();
                     emit('scan', decodedText);
                }
            },
            (error) => {
                // ignore
            }
        );
    }).catch(err => {
        console.error("Error starting scanner", err);
    });

    scanner.value = html5QrCode;
  });
}

function stopScanner() {
    if (scanner.value) {
        scanner.value.stop().then(() => {
            scanner.value?.clear();
        }).catch(console.error);
    }
}

function resumeScanner() {
    if(scanner.value) {
        scanner.value.resume();
    }
}

// Watchers or methods to resume scanner if modal closes
// Since props are reactive, we can watch props.showResultModal
import { watch } from 'vue';

watch(() => props.showResultModal, (newVal) => {
    if (!newVal && scanner.value) {
        scanner.value.resume();
    }
});

onMounted(() => {
    initScanner();
});

onUnmounted(() => {
    stopScanner();
});

</script>

<style scoped>
:deep(#qr-reader video) {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
    border-radius: 1rem;
}

/* Animations */
@keyframes bounce-in {
  0% { transform: scale(0.3); opacity: 0; }
  50% { transform: scale(1.05); }
  70% { transform: scale(0.9); }
  100% { transform: scale(1); opacity: 1; }
}
.animate-bounce-in {
  animation: bounce-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}
.animate-shake {
  animation: shake 0.5s ease-in-out;
}
</style>

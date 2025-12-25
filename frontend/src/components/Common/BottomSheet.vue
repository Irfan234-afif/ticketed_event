<template>
  <Teleport to="body">
    <transition name="bottom-sheet">
      <div v-if="show" class="fixed inset-0 z-[100] flex items-end justify-center pointer-events-none">
        
        <!-- Backdrop -->
        <div 
          class="absolute inset-0 bg-black/40 pointer-events-auto backdrop" 
          @click="close"
        ></div>
        
        <!-- Sheet -->
        <div 
          ref="sheetRef"
          :class="[
            'bg-white w-full max-w-lg rounded-t-[30px] shadow-2xl overflow-hidden pointer-events-auto flex flex-col sheet relative z-10',
            fullHeight ? 'h-[90vh]' : 'max-h-[90vh]'
          ]"
          :style="sheetStyle"
          @touchstart="onTouchStart"
          @touchmove="onTouchMove"
          @touchend="onTouchEnd"
          @mousedown="onMouseDown" 
          @mousemove="onMouseMove" 
          @mouseup="onMouseUp"
          @mouseleave="onMouseUp"
        >
          <!-- Handle -->
          <div class="w-full flex justify-center py-3 bg-white shrink-0 cursor-grab active:cursor-grabbing touch-none">
            <div class="w-12 h-1.5 bg-gray-300 rounded-full"></div>
          </div>

          <!-- Header Slot -->
          <div v-if="$slots.header" class="shrink-0">
             <slot name="header"></slot>
          </div>

          <!-- Content -->
          <div 
            class="flex-1 overflow-y-auto bg-white overscroll-contain"
            ref="contentRef"
            @touchstart.stop
            @mousedown.stop
          >
            <slot></slot>
          </div>
        </div>

      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  show: boolean
  dragThreshold?: number
  fullHeight?: boolean
}>()

const emit = defineEmits(['update:show', 'close'])

const sheetRef = ref<HTMLElement | null>(null)
const contentRef = ref<HTMLElement | null>(null)

// Drag State
const isDragging = ref(false)
const isClosing = ref(false)
const startY = ref(0)
const currentY = ref(0)
const translateY = ref(0)

const DRAG_THRESHOLD = props.dragThreshold || 120

// Computed Style for Sheet
const sheetStyle = computed(() => {
  if (isDragging.value) {
    return {
      transform: `translateY(${translateY.value}px)`,
      transition: 'none'
    }
  }
  
  // If closing or returning to 0, use CSS transition (removing 'transition: none')
  // We explicitly set transform if we have value, otherwise let CSS take over (for entering/leaving via v-if)
  if (isClosing.value || translateY.value > 0) {
      return {
          transform: `translateY(${translateY.value}px)`
      }
  }

  return {}
})

function close() {
  emit('update:show', false)
  emit('close')
}

// Ensure clean state on open
watch(() => props.show, (val) => {
  if (val) {
    translateY.value = 0
    isDragging.value = false
    isClosing.value = false
  }
})

// --- Touch Handling ---

function onTouchStart(e: TouchEvent) {
  if (e.touches.length === 0) return
  isDragging.value = true
  const touch = e.touches[0]
  if (touch) {
      startY.value = touch.clientY
      currentY.value = startY.value
      translateY.value = 0
  }
}

function onTouchMove(e: TouchEvent) {
  if (!isDragging.value || e.touches.length === 0) return
  
  const touch = e.touches[0]
  if (!touch) return

  const touchY = touch.clientY
  const delta = touchY - startY.value
  
  // Only allow dragging down
  if (delta > 0) {
    translateY.value = delta
    if (e.cancelable) e.preventDefault() 
  } else {
    translateY.value = 0
  }
  currentY.value = touchY
}

function onTouchEnd() {
  if (!isDragging.value) return
  isDragging.value = false
  
  if (translateY.value > DRAG_THRESHOLD) {
    handleDragClose()
  } else {
    // Snap back to 0
    translateY.value = 0
  }
}

// --- Mouse Handling ---
function onMouseDown(e: MouseEvent) {
    isDragging.value = true
    startY.value = e.clientY
    currentY.value = startY.value
    translateY.value = 0
}

function onMouseMove(e: MouseEvent) {
    if (!isDragging.value) return
    const touchY = e.clientY
    const delta = touchY - startY.value
    if (delta > 0) {
        translateY.value = delta
    } else {
        translateY.value = 0
    }
}

function onMouseUp() {
    if (!isDragging.value) return
    isDragging.value = false
    if (translateY.value > DRAG_THRESHOLD) {
        handleDragClose()
    } else {
        translateY.value = 0
    }
}

function handleDragClose() {
    isClosing.value = true
    // Animate to off-screen
    const height = sheetRef.value?.offsetHeight || window.innerHeight
    translateY.value = height
    
    // Wait for animation to finish (300ms matches CSS)
    setTimeout(() => {
        close()
        // Reset after a bit to ensure it doesn't jump back if parent delays unmount (though v-if should be immediate)
        // But if show=false, v-if removes it. The state reset happens on next show=true via watch.
    }, 300)
}
</script>

<style scoped>
.bottom-sheet-enter-active,
.bottom-sheet-leave-active {
  transition: opacity 0.3s ease;
}

.bottom-sheet-enter-active .sheet,
.bottom-sheet-leave-active .sheet {
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
}

.bottom-sheet-enter-from .backdrop,
.bottom-sheet-leave-to .backdrop {
  opacity: 0;
}

.bottom-sheet-enter-from .sheet,
.bottom-sheet-leave-to .sheet {
  transform: translateY(100%);
}

.bottom-sheet-enter-active .backdrop,
.bottom-sheet-leave-active .backdrop {
    transition: opacity 0.3s ease;
}
</style>

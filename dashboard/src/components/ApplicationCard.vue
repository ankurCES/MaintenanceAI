<template>
  <button 
    @click="$emit('select')" 
    class="bg-slate-800 border border-slate-700 hover:border-indigo-500 rounded-xl p-6 flex flex-col items-start transition-all hover:shadow-[0_0_20px_rgba(99,102,241,0.15)] group w-full text-left"
  >
    <div class="flex justify-between items-start w-full mb-4">
      <div class="w-12 h-12 rounded-lg flex items-center justify-center text-xl font-bold" :class="colorClass">
        <svg v-if="app.icon === 'ecommerce'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
        <svg v-else-if="app.icon === 'payment'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
      </div>
      <div class="px-3 py-1 rounded-full text-xs font-semibold" :class="statusBadgeClass">
        {{ app.status }}
      </div>
    </div>
    
    <h3 class="text-xl font-bold text-slate-100 group-hover:text-indigo-400 transition-colors">{{ app.name }}</h3>
    <p class="text-sm text-slate-400 mt-2 line-clamp-2 h-10">{{ app.description }}</p>
    
    <div class="w-full h-px bg-slate-700 my-4"></div>
    
    <div class="grid grid-cols-2 gap-4 w-full">
      <div class="flex flex-col">
        <span class="text-xs text-slate-500 uppercase tracking-widest font-semibold mb-1">Active Incidents</span>
        <span class="text-lg font-mono text-slate-200">{{ app.incidentCount }}</span>
      </div>
      <div class="flex flex-col">
        <span class="text-xs text-slate-500 uppercase tracking-widest font-semibold mb-1">Avg AI Score</span>
        <span class="text-lg font-mono" :class="scoreColorClass">{{ app.avgConfidence || 'N/A' }}{{ app.avgConfidence ? '%' : '' }}</span>
      </div>
    </div>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  app: any
}>();

defineEmits(['select']);

const colorClass = computed(() => {
  const map: Record<string, string> = {
    ecommerce: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
    payment: 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30',
    internal: 'bg-amber-500/20 text-amber-400 border border-amber-500/30',
  };
  return map[props.app.icon] || 'bg-slate-500/20 text-slate-400 border border-slate-500/30';
});

const statusBadgeClass = computed(() => {
  if (props.app.status === 'Critical') return 'bg-rose-500/20 text-rose-400 border border-rose-500/30 animate-pulse';
  if (props.app.status === 'Warning') return 'bg-amber-500/20 text-amber-400 border border-amber-500/30';
  return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
});

const scoreColorClass = computed(() => {
  if (!props.app.avgConfidence) return 'text-slate-500';
  if (props.app.avgConfidence >= 90) return 'text-emerald-400';
  if (props.app.avgConfidence >= 75) return 'text-amber-400';
  return 'text-rose-400';
});
</script>

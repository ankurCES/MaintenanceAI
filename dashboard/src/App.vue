<template>
  <div class="h-screen w-screen bg-slate-900 text-slate-100 font-sans flex flex-col overflow-hidden relative">
    <header class="bg-slate-800 border-b border-slate-700 px-6 py-4 flex items-center justify-between shadow-lg z-20 flex-shrink-0">
      <div class="flex items-center gap-3">
        <button v-if="selectedAppId" @click="goHome" class="mr-2 p-2 hover:bg-slate-700 rounded-full transition-colors text-slate-400 hover:text-white">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        </button>
        <div class="w-10 h-10 bg-indigo-500 rounded flex items-center justify-center font-bold text-xl shadow-[0_0_15px_rgba(99,102,241,0.5)]">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        </div>
        <div>
          <h1 class="text-xl font-bold tracking-wide">
            <span v-if="!selectedAppId">Maintenance<span class="text-indigo-400">AI</span></span>
            <span v-else>{{ getSelectedAppName() }} <span class="text-slate-500 font-normal text-sm ml-2">App Details</span></span>
          </h1>
          <div class="text-xs text-slate-400">Enterprise AI Insights Engine</div>
        </div>
      </div>
    </header>

    <main class="flex-1 flex overflow-hidden">
      
      <div v-if="!selectedAppId" class="flex-1 p-8 overflow-y-auto bg-slate-900/50">
        <div class="max-w-7xl mx-auto">
          <h2 class="text-3xl font-bold text-slate-100 mb-2">Enterprise Application Portfolio</h2>
          <p class="text-slate-400 mb-8">Select an application to view live telemetry and AI root cause analysis across distributed domains.</p>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <ApplicationCard 
              v-for="app in applications" 
              :key="app.id" 
              :app="app"
              @select="selectApp(app.id)"
            />
          </div>
        </div>
      </div>

      <div v-else class="flex-1 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 overflow-hidden">
        
        <div class="lg:col-span-3 flex flex-col gap-4 h-full">
          <div class="flex justify-between items-center">
            <h2 class="text-sm font-semibold text-slate-400 flex items-center gap-2 uppercase tracking-wider">Live Log Stream</h2>
          </div>
          <div class="flex-1 bg-black rounded-xl border border-slate-700 shadow-inner overflow-y-auto p-4 font-mono text-xs flex flex-col gap-2">
            <div v-if="appLogs.length === 0" class="text-slate-600 text-center mt-10">Awaiting telemetry data...</div>
            <div v-for="(log, idx) in appLogs" :key="idx" class="border-b border-slate-800 pb-2 break-all">
              <span class="text-slate-500">[{{ formatTime(log.timestamp) }}]</span> 
              <span :class="getLogLevelColor(log.level)" class="mx-2 font-bold">{{ log.level }}</span>
              <span class="text-indigo-400">[{{ log.log_group_or_service || 'sys' }}]</span> 
              <span class="text-slate-300 ml-1">{{ log.message }}</span>
            </div>
          </div>
        </div>

        <div class="lg:col-span-3 flex flex-col gap-4 h-full">
          <div class="flex justify-between items-center">
            <h2 class="text-lg font-semibold text-slate-200 flex items-center gap-2">AI Incident Reports</h2>
          </div>
          <div class="flex-1 bg-slate-800 rounded-xl border border-slate-700 shadow-lg overflow-y-auto">
            <div v-if="appIncidents.length === 0" class="p-8 text-center text-slate-500 flex flex-col items-center justify-center h-full">
              <p>System stable.</p>
            </div>
            <div v-else class="flex flex-col">
              <button 
                v-for="incident in appIncidents" :key="incident.id"
                @click="selectedIncident = incident; isCopilotOpen = false"
                class="p-4 border-b border-slate-700 hover:bg-slate-750 transition-colors text-left focus:outline-none"
                :class="{'bg-slate-700 border-l-4 border-l-indigo-500': selectedIncident?.id === incident.id, 'border-l-4 border-l-transparent': selectedIncident?.id !== incident.id}"
              >
                <div class="flex justify-between items-start mb-2">
                  <span class="text-xs font-mono bg-rose-500/20 text-rose-400 px-2 py-0.5 rounded border border-rose-500/30">ERROR</span>
                  <span class="text-xs text-slate-400">{{ formatTime(incident.timestamp) }}</span>
                </div>
                <div class="font-medium text-slate-200 text-sm truncate mb-1">Service: <span class="text-indigo-300">{{ incident.service }}</span></div>
                <p class="text-xs text-slate-400 line-clamp-2">{{ incident.ai_analysis?.incident_summary }}</p>
              </button>
            </div>
          </div>
        </div>

        <div class="lg:col-span-6 flex flex-col gap-4 h-full">
          <div v-if="!selectedIncident" class="flex-1 bg-slate-800 rounded-xl border border-slate-700 shadow-lg flex items-center justify-center text-slate-500 p-8">
            Select an incident from the feed to view AI Insights
          </div>

          <div v-else class="flex-1 flex flex-col gap-4 h-full relative">
            <div class="flex justify-between items-center bg-slate-800 p-4 rounded-xl border border-slate-700 shadow-sm flex-shrink-0 relative">
              <div class="flex items-center gap-3">
                <div class="text-2xl font-bold" :class="getConfidenceColor(selectedIncident.ai_analysis?.confidence_score)">
                  {{ selectedIncident.ai_analysis?.confidence_score || '0' }}%
                </div>
                <div class="text-xs text-slate-400 leading-tight">AI Confidence<br/>Score</div>
              </div>
              <div class="flex gap-3">
                <button 
                  @click="isCopilotOpen = !isCopilotOpen"
                  class="bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-2 rounded text-sm font-medium transition-colors flex items-center gap-2 border border-slate-600 shadow-sm relative overflow-hidden group"
                  :class="{'ring-2 ring-indigo-500': isCopilotOpen}"
                >
                  <div class="absolute inset-0 bg-indigo-500/10 group-hover:bg-indigo-500/20 transition-colors"></div>
                  <span class="relative">Investigate with AI</span>
                </button>
              </div>
            </div>

            <div class="bg-slate-800 rounded-xl border border-slate-700 shadow-lg overflow-hidden flex-1 flex flex-col min-h-0">
              <div class="bg-slate-900/50 p-5 border-b border-slate-700 flex-shrink-0">
                <h3 class="text-xl font-bold text-slate-100 mb-2">AI Root Cause Analysis</h3>
                <p class="text-slate-300 text-sm leading-relaxed">{{ selectedIncident.ai_analysis?.incident_summary }}</p>
              </div>

              <div class="p-5 flex flex-col gap-6 overflow-y-auto flex-1">
                
                <!-- NEW TIMELINE COMPONENT -->
                <div v-if="selectedIncident.ai_analysis?.timeline_analysis" class="mb-2">
                  <h4 class="text-xs uppercase tracking-widest text-slate-500 font-bold mb-4">Cascading Event Timeline</h4>
                  <div class="relative border-l border-indigo-500/30 ml-3 space-y-6">
                    <div v-for="(event, idx) in selectedIncident.ai_analysis.timeline_analysis" :key="idx" class="relative pl-6">
                      <span class="absolute -left-1.5 top-1 w-3 h-3 rounded-full" :class="idx === selectedIncident.ai_analysis.timeline_analysis.length - 1 ? 'bg-rose-500 ring-4 ring-rose-500/20' : 'bg-indigo-500'"></span>
                      <div class="flex items-center gap-2 mb-1">
                        <span class="text-xs font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-700">{{ event.time }}</span>
                        <span class="text-xs font-semibold text-indigo-300">{{ event.service }}</span>
                      </div>
                      <p class="text-sm text-slate-300">{{ event.event }}</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 class="text-xs uppercase tracking-widest text-slate-500 font-bold mb-2">Probable Root Cause</h4>
                  <div class="bg-indigo-900/20 border border-indigo-500/30 p-4 rounded-lg text-indigo-100 text-sm leading-relaxed">
                    {{ selectedIncident.ai_analysis?.probable_root_cause }}
                  </div>
                </div>

                <div>
                  <h4 class="text-xs uppercase tracking-widest text-slate-500 font-bold mb-2">Recommended Actions</h4>
                  <ul class="space-y-2">
                    <li v-for="(action, idx) in selectedIncident.ai_analysis?.recommended_actions" :key="idx" class="flex gap-3 text-sm bg-slate-900/50 p-3 rounded border border-slate-700">
                      <span class="text-emerald-400 font-mono mt-0.5">[{{ idx + 1 }}]</span>
                      <span class="text-slate-300">{{ action }}</span>
                    </li>
                  </ul>
                </div>

              </div>
            </div>

            <Transition
              enter-active-class="transition duration-200 ease-out"
              enter-from-class="opacity-0"
              enter-to-class="opacity-100"
              leave-active-class="transition duration-150 ease-in"
              leave-from-class="opacity-100"
              leave-to-class="opacity-0"
            >
              <!-- Full Screen Backdrop -->
              <div v-if="isCopilotOpen" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 sm:p-8">
                <!-- Modal Container -->
                <div class="bg-slate-800 w-full max-w-5xl h-full max-h-[90vh] rounded-2xl border border-slate-600 shadow-2xl flex flex-col overflow-hidden relative" @click.stop>
                  <!-- Header -->
                  <div class="px-6 py-4 border-b border-slate-700 bg-slate-800/80 flex items-center justify-between flex-shrink-0">
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 rounded bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"/></svg>
                      </div>
                      <h3 class="font-bold text-lg text-slate-100">AI Investigation Copilot</h3>
                    </div>
                    <button @click="isCopilotOpen = false" class="text-slate-400 hover:text-white p-1 hover:bg-slate-700 rounded transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    </button>
                  </div>
                  <!-- Chat Area -->
                  <div class="flex-1 overflow-hidden relative">
                    <CopilotChat 
                      :isOpen="true" 
                      :contextIncident="selectedIncident" 
                      @close="isCopilotOpen = false" 
                      class="absolute inset-0 w-full h-full"
                    />
                  </div>
                </div>
              </div>
            </Transition>

          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import CopilotChat from './components/CopilotChat.vue';
import ApplicationCard from './components/ApplicationCard.vue';

interface Incident {
  id: string;
  timestamp: string;
  service: string;
  raw_log: any;
  ai_analysis: {
    incident_summary: string;
    probable_root_cause: string;
    confidence_score: number;
    affected_components: string[];
    recommended_actions: string[];
    timeline_analysis?: { time: string, event: string, service: string }[];
  }
}

const allIncidents = ref<Incident[]>([]);
const allLogs = ref<any[]>([]);

const selectedAppId = ref<string | null>(null);
const selectedIncident = ref<Incident | null>(null);
const isCopilotOpen = ref(false); 
const isLoading = ref(false);
let pollInterval: any = null;

const applications = ref([
  { id: "app-osint", name: "Global OSINT Dashboard", description: "Real-time global intelligence, CCTV vision analytics, and live API monitors.", icon: "ecommerce", filterServices: ["osint-dashboard"], status: "Healthy", incidentCount: 0, avgConfidence: 0 },
  { id: "app-ecommerce", name: "Global Storefront UI", description: "Main consumer web interface and edge CDN caching layers.", icon: "ecommerce", filterServices: ["storefront-web", "recommendation-engine", "cloudfront-edge"], status: "Healthy", incidentCount: 0, avgConfidence: 0 },
  { id: "app-payment", name: "FinTech & Payment Gateway", description: "Credit card auth holds, anti-fraud ML, and stripe integrations.", icon: "payment", filterServices: ["fintech-gateway", "fraud-detection-ml"], status: "Healthy", incidentCount: 0, avgConfidence: 0 },
  { id: "app-fulfillment", name: "Order Processing & Fulfillment", description: "Kafka routing, logistics optimization, and warehouse Kiva robotics.", icon: "internal", filterServices: ["fulfillment-router", "logistics-optimizer", "inventory-master-db", "kiva-control-plane"], status: "Healthy", incidentCount: 0, avgConfidence: 0 },
  { id: "app-zero", name: "Zero Systems (Ledger)", description: "Internal automated accounting reconciliation and general ledger batch jobs.", icon: "internal", filterServices: ["zero-ledger-batch", "zero-ledger-scheduler"], status: "Healthy", incidentCount: 0, avgConfidence: 0 },
  { id: "app-hr", name: "Corporate Apps (HR/SSO)", description: "Internal intranet, SSO proxies, and Workday directory sync.", icon: "internal", filterServices: ["corp-sso-proxy", "hr-intranet"], status: "Healthy", incidentCount: 0, avgConfidence: 0 }
]);

const activeAppConfig = computed(() => applications.value.find(a => a.id === selectedAppId.value));

const appLogs = computed(() => {
  if (!activeAppConfig.value) return [];
  const filters = activeAppConfig.value.filterServices;
  return allLogs.value.filter(log => filters.includes(log.log_group_or_service || ''));
});

const appIncidents = computed(() => {
  if (!activeAppConfig.value) return [];
  const filters = activeAppConfig.value.filterServices;
  return allIncidents.value.filter(inc => filters.includes(inc.service || ''));
});

const selectApp = (id: string) => {
  selectedAppId.value = id;
  isCopilotOpen.value = false;
  // Auto select first incident if any
  const incs = allIncidents.value.filter(inc => applications.value.find(a => a.id === id)?.filterServices.includes(inc.service));
  if (incs.length > 0) {
    selectedIncident.value = incs[0];
  } else {
    selectedIncident.value = null;
  }
};

const goHome = () => {
  selectedAppId.value = null;
  selectedIncident.value = null;
  isCopilotOpen.value = false;
};

const getSelectedAppName = () => activeAppConfig.value?.name || 'Application';

const getConfidenceColor = (score: number) => {
  if (score >= 90) return 'text-emerald-400';
  if (score >= 75) return 'text-amber-400';
  return 'text-rose-400';
};

const getLogLevelColor = (level: string) => {
  const l = (level || '').toUpperCase();
  if (l.includes('ERROR') || l.includes('FATAL')) return 'text-rose-400';
  if (l.includes('WARN')) return 'text-amber-400';
  if (l.includes('DEBUG')) return 'text-slate-400';
  return 'text-emerald-400';
}

const formatTime = (ts: string) => {
  try {
    return new Date(ts).toLocaleTimeString();
  } catch (e) {
    return ts;
  }
};

const fetchDashboardData = async () => {
  try {
    const incResp = await fetch(`http://${window.location.hostname}:8001/api/incidents`);
    if (incResp.ok) {
      const data = await incResp.json();
      allIncidents.value = data.incidents || [];
    }

    const logResp = await fetch(`http://${window.location.hostname}:8001/api/logs`);
    if (logResp.ok) {
      const data = await logResp.json();
      allLogs.value = data.logs || [];
    }

    applications.value.forEach(app => {
      const appIncs = allIncidents.value.filter(inc => app.filterServices.includes(inc.service));
      app.incidentCount = appIncs.length;
      if (appIncs.length > 0) {
        const totalScore = appIncs.reduce((sum, inc) => sum + (inc.ai_analysis?.confidence_score || 0), 0);
        app.avgConfidence = Math.round(totalScore / appIncs.length);
        app.status = appIncs.length > 2 ? 'Critical' : 'Warning';
      } else {
        app.avgConfidence = 0;
        app.status = 'Healthy';
      }
    });
  } catch (e) {
    console.error("Failed to fetch dashboard data", e);
  }
};

onMounted(() => {
  isLoading.value = true;
  fetchDashboardData().finally(() => isLoading.value = false);
  pollInterval = setInterval(fetchDashboardData, 3000);
});

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval);
});
</script>

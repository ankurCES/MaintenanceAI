<template>
  <div class="flex flex-col h-full bg-slate-800 border-l border-slate-700 w-96 flex-shrink-0 transition-all duration-300 shadow-[-5px_0_15px_rgba(0,0,0,0.2)]" :class="isOpen ? 'translate-x-0' : 'translate-x-full absolute right-0'">
    
    <!-- Header -->
    <div class="p-4 border-b border-slate-700 flex justify-between items-center bg-slate-900/50">
      <div class="flex items-center gap-2">
        <div class="w-6 h-6 bg-indigo-500 rounded flex items-center justify-center text-xs font-bold text-white shadow-[0_0_10px_rgba(99,102,241,0.5)]">AI</div>
        <h3 class="font-semibold text-slate-100">SRE Copilot</h3>
      </div>
      <button @click="$emit('close')" class="text-slate-400 hover:text-white transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <!-- Chat History -->
    <div class="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
      <div v-if="messages.length === 0" class="text-center text-slate-500 mt-10 text-sm">
        <p>Ask me to analyze the current incident, query logs, or graph metrics.</p>
        <div class="mt-4 flex flex-col gap-2">
          <button @click="setInput('Graph the latency for this service')" class="bg-slate-700/50 hover:bg-slate-700 text-left px-3 py-2 rounded text-xs transition-colors">"Graph the latency for this service"</button>
          <button @click="setInput('What port is failing?')" class="bg-slate-700/50 hover:bg-slate-700 text-left px-3 py-2 rounded text-xs transition-colors">"What port is failing?"</button>
        </div>
      </div>

      <div v-for="(msg, idx) in messages" :key="idx" class="flex flex-col" :class="msg.role === 'user' ? 'items-end' : 'items-start'">
        
        <!-- User Bubble -->
        <div v-if="msg.role === 'user'" class="bg-indigo-600 text-white px-4 py-2 rounded-2xl rounded-tr-sm text-sm max-w-[85%] shadow-md">
          {{ msg.content }}
        </div>
        
        <!-- AI Bubble -->
        <div v-else class="bg-slate-700 text-slate-200 px-4 py-3 rounded-2xl rounded-tl-sm text-sm max-w-[95%] shadow-md border border-slate-600">
          <div class="prose prose-invert prose-sm max-w-none" v-html="renderMarkdown(msg.text || msg.content)"></div>
          
          <!-- Render AG-UI Components -->
          <div v-if="msg.ag_ui" class="mt-4 p-3 bg-slate-900 rounded-lg border border-slate-800">
            <div class="text-xs text-slate-500 font-mono mb-2 uppercase tracking-wider flex items-center gap-1">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-indigo-400"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
              {{ msg.ag_ui.title || 'Data Visual' }}
            </div>
            
            <BarChart v-if="msg.ag_ui.type === 'BarChart'" :data="getChartData(msg.ag_ui)" :options="chartOptions" class="h-40" />
            <LineChart v-else-if="msg.ag_ui.type === 'LineChart'" :data="getChartData(msg.ag_ui)" :options="chartOptions" class="h-40" />
            <div v-else class="text-xs text-rose-400">Unsupported AG-UI Component: {{ msg.ag_ui.type }}</div>
          </div>
        </div>

      </div>

      <!-- Loading Spinner -->
      <div v-if="isTyping" class="flex items-start gap-2 text-slate-500 text-sm">
        <div class="w-6 h-6 bg-slate-700 rounded flex items-center justify-center text-xs font-bold text-slate-400">AI</div>
        <div class="bg-slate-700 px-4 py-2 rounded-2xl rounded-tl-sm flex items-center gap-1 h-9">
          <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
          <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
          <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="p-4 border-t border-slate-700 bg-slate-900/50">
      <form @submit.prevent="sendMessage" class="relative">
        <input 
          type="text" 
          v-model="inputText" 
          placeholder="Ask Copilot..." 
          class="w-full bg-slate-800 border border-slate-600 text-sm text-slate-200 rounded-full pl-4 pr-10 py-2.5 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
          :disabled="isTyping"
        >
        <button type="submit" class="absolute right-2 top-1.5 p-1 text-indigo-400 hover:text-indigo-300 disabled:text-slate-600 transition-colors" :disabled="!inputText.trim() || isTyping">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        </button>
      </form>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { Bar as BarChart, Line as LineChart } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement);

const props = defineProps<{
  isOpen: boolean,
  contextIncident: any
}>();

const emit = defineEmits(['close']);

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string; 
  text?: string;   
  ag_ui?: any;     
}

const messages = ref<ChatMessage[]>([]);
const inputText = ref('');
const isTyping = ref(false);

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
    x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
  }
};

const getChartData = (agUiData: any) => {
  // Graceful fallback if the LLM hallucinates the JSON structure slightly
  const labels = agUiData.labels || [];
  const datasets = agUiData.datasets || [];

  return {
    labels: labels,
    datasets: datasets.map((ds: any) => ({
      label: ds.label || 'Data',
      data: ds.data || [],
      backgroundColor: '#6366f1',
      borderColor: '#818cf8',
      borderWidth: 2,
      tension: 0.3
    }))
  };
};

const setInput = (txt: string) => {
  inputText.value = txt;
};

const renderMarkdown = (text: string) => {
  return DOMPurify.sanitize(marked(text || '') as string);
};

watch(() => props.contextIncident?.id, (newId, oldId) => {
  if (newId !== oldId && newId) {
    messages.value.push({
      role: 'assistant',
      content: `I see you switched to incident **${props.contextIncident.service}**. How can I help?`,
      text: `I see you switched to incident **${props.contextIncident.service}**. How can I help?`
    });
  }
});

const parseAGUI = (rawContent: string) => {
  let textPart = rawContent;
  let agUiPart = null;

  // Sometimes LLMs add an optional language tag to the json block, so we make it optional
  const regex = /```ag-ui\s*([\s\S]*?)\s*```/;
  const match = rawContent.match(regex);
  
  if (match) {
    try {
      agUiPart = JSON.parse(match[1].trim());
      textPart = rawContent.replace(match[0], '').trim();
    } catch (e) {
      console.error("Failed to parse AG-UI block:", e);
    }
  }

  return { text: textPart, ag_ui: agUiPart };
};

const sendMessage = async () => {
  if (!inputText.value.trim() || isTyping.value) return;

  const userMsg = inputText.value.trim();
  inputText.value = '';
  
  messages.value.push({ role: 'user', content: userMsg, text: userMsg });
  isTyping.value = true;

  try {
    const response = await fetch(`http://${window.location.hostname}:8001/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userMsg,
        incident_context: props.contextIncident,
        history: messages.value.slice(0, -1).map(m => ({ role: m.role, content: m.content }))
      })
    });

    if (!response.ok) {
      const err = await response.text();
      throw new Error(`API Error: ${response.status} ${err}`);
    }
    
    const data = await response.json();
    const rawReply = data.reply;
    
    const parsed = parseAGUI(rawReply);

    messages.value.push({
      role: 'assistant',
      content: rawReply,
      text: parsed.text,
      ag_ui: parsed.ag_ui
    });

  } catch (error: any) {
    console.error(error);
    messages.value.push({
      role: 'assistant',
      content: `Error: Could not connect to Copilot backend. (${error.message})`,
      text: `Error: Could not connect to Copilot backend. (${error.message})`
    });
  } finally {
    isTyping.value = false;
  }
};
</script>

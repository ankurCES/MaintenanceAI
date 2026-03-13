<template>
  <div class="h-screen w-screen flex flex-col bg-gray-950 text-gray-200 font-mono overflow-hidden">
    <!-- Top HUD Bar -->
    <header class="h-14 bg-gray-900 border-b border-cyan-900/50 shadow-md flex items-center justify-between px-6 z-50 shrink-0">
      <div class="flex items-center gap-3">
        <div class="w-3 h-3 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_#00ffff]"></div>
        <h1 class="text-xl font-bold tracking-widest text-cyan-400 drop-shadow-[0_0_8px_rgba(0,255,255,0.6)]">OSINT//NEXUS</h1>
        <div class="text-[10px] ml-4 text-gray-500 border border-gray-700 px-2 py-0.5 rounded">
          NEXT SWEEP: {{ Math.max(0, Math.floor(countdown)) }}s
        </div>
        <button @click="forceFullSweep" class="text-[10px] ml-2 bg-cyan-900/30 hover:bg-cyan-800 text-cyan-300 px-2 py-1 rounded transition-colors border border-cyan-800 cursor-pointer">
          FORCE SYNC
        </button>
      </div>
      <div class="flex gap-6 text-xs text-blue-300 tracking-widest uppercase">
        <div class="flex items-center gap-1"><span class="text-cyan-400 font-bold">{{ dotCams.length }}</span> CAMS</div>
        <div class="flex items-center gap-1"><span class="text-green-400 font-bold">{{ flights.length }}</span> FLIGHTS</div>
        <div class="flex items-center gap-1"><span class="text-orange-500 font-bold">{{ fires.length }}</span> FIRES</div>
        <div v-if="sansData" class="flex items-center gap-1 border-l border-gray-700 pl-4 ml-2">
          DEFCON: <span :class="{'text-green-500': sansData.status === 'green', 'text-yellow-500': sansData.status === 'yellow', 'text-red-500': sansData.status === 'red'}" class="font-bold animate-pulse">{{ sansData.status.toUpperCase() }}</span>
        </div>
      </div>
    </header>

    <!-- Main Grid Dashboard -->
    <div class="flex-1 grid grid-cols-12 grid-rows-12 gap-3 p-3 overflow-hidden">
      
      <!-- Central Heatmap Tile (Spans 6 cols, 6 rows) -->
      <div class="col-span-6 row-span-6 bg-black border border-cyan-900/50 rounded-xl relative overflow-hidden shadow-xl flex flex-col">
        <div class="bg-gray-900 border-b border-cyan-900/50 px-4 py-2 text-xs font-bold text-cyan-500 tracking-widest flex justify-between z-10">
          <span>GLOBAL CLUSTER MAP</span>
          <span>{{ heatmapPoints.length }} LIVE DATA POINTS</span>
        </div>
        <div id="map" class="absolute top-0 left-0 w-full h-full z-0"></div>
      </div>

      <!-- SANS Cyber Threats Table (Spans 3 cols, 3 rows) -->
      <div class="col-span-3 row-span-3 bg-gray-900/80 border border-gray-800 rounded-xl overflow-hidden flex flex-col">
        <div class="bg-gray-800/80 border-b border-gray-700 px-4 py-1.5 text-[10px] font-bold text-red-500 tracking-widest flex justify-between">
          <span>CYBER THREATS</span>
        </div>
        <div class="flex-1 overflow-auto">
          <table class="w-full text-left text-[10px] sm:text-xs">
            <thead class="bg-black/40 text-gray-500 sticky top-0">
              <tr>
                <th class="p-2 font-normal">PORT</th>
                <th class="p-2 font-normal text-right">RECORDS</th>
                <th class="p-2 font-normal text-right">TARGETS</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-800/50">
              <tr v-for="(port, i) in dshieldPorts" :key="i" class="hover:bg-gray-800/50">
                <td class="p-2 font-bold text-red-400">{{ port.targetport }}</td>
                <td class="p-2 text-gray-300 text-right">{{ Number(port.records).toLocaleString() }}</td>
                <td class="p-2 text-gray-400 text-right">{{ Number(port.targets).toLocaleString() }}</td>
              </tr>
              <tr v-if="dshieldPorts.length === 0"><td colspan="3" class="p-4 text-center text-gray-600">POLLING...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Orbital Assets (Spans 3 cols, 3 rows) -->
      <div class="col-span-3 row-span-3 bg-gray-900/80 border border-gray-800 rounded-xl overflow-hidden flex flex-col">
        <div class="bg-gray-800/80 border-b border-gray-700 px-4 py-1.5 text-[10px] font-bold text-blue-400 tracking-widest flex justify-between">
          <span>ORBITAL SATELLITES (ISS)</span>
          <span class="text-green-500">TRACKING</span>
        </div>
        <div class="flex-1 p-2 flex flex-col justify-center" v-if="issTracker">
           <div class="flex justify-between items-end mb-1 px-2">
             <div class="text-2xl font-bold text-white leading-none">{{ issTracker.velocity.toFixed(0) }} <span class="text-[10px] text-gray-500 font-normal">km/h</span></div>
             <div class="text-[9px] text-blue-400 bg-blue-900/20 px-1.5 py-0.5 rounded border border-blue-900/50">ZARYA/25544</div>
           </div>
           <div class="grid grid-cols-2 gap-2 text-center px-2">
             <div class="bg-black/50 p-1 rounded border border-gray-800">
               <div class="text-[8px] text-gray-500">ALTITUDE</div>
               <div class="text-xs text-blue-300">{{ issTracker.altitude.toFixed(1) }} km</div>
             </div>
             <div class="bg-black/50 p-1 rounded border border-gray-800 cursor-pointer hover:bg-gray-800/50" @click="focusMap(issTracker.latitude, issTracker.longitude)">
               <div class="text-[8px] text-gray-500">GPS LOCK</div>
               <div class="text-[10px] text-blue-300 mt-0.5">{{ issTracker.latitude.toFixed(2) }}, {{ issTracker.longitude.toFixed(2) }}</div>
             </div>
           </div>
        </div>
      </div>

      <!-- Fires Table (Spans 3 cols, 3 rows) -->
      <div class="col-span-3 row-span-3 bg-gray-900/80 border border-gray-800 rounded-xl overflow-hidden flex flex-col">
        <div class="bg-gray-800/80 border-b border-gray-700 px-4 py-1.5 text-[10px] font-bold text-orange-500 tracking-widest flex justify-between">
          <span>THERMAL ANOMALIES (FIRES)</span>
        </div>
        <div class="flex-1 overflow-auto">
          <table class="w-full text-left text-[10px] sm:text-xs">
            <thead class="bg-black/40 text-gray-500 sticky top-0">
              <tr>
                <th class="p-2 font-normal">LAT</th>
                <th class="p-2 font-normal">LNG</th>
                <th class="p-2 font-normal text-right">BRIGHTNESS</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-800/50">
              <tr v-for="(fire, i) in fires.slice(0, 15)" :key="i" class="hover:bg-gray-800/50 cursor-pointer" @click="focusMap(fire.latitude, fire.longitude)">
                <td class="p-2 text-white">{{ fire.latitude.toFixed(2) }}</td>
                <td class="p-2 text-gray-400">{{ fire.longitude.toFixed(2) }}</td>
                <td class="p-2 text-orange-300 text-right">{{ fire.brightness }}</td>
              </tr>
              <tr v-if="fires.length === 0"><td colspan="3" class="p-4 text-center text-gray-600">AWAITING SATELLITE DATA...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Earthquakes Table (Spans 3 cols, 3 rows) -->
      <div class="col-span-3 row-span-3 bg-gray-900/80 border border-gray-800 rounded-xl overflow-hidden flex flex-col">
        <div class="bg-gray-800/80 border-b border-gray-700 px-4 py-1.5 text-[10px] font-bold text-yellow-500 tracking-widest flex justify-between">
          <span>SEISMIC ACTIVITY</span>
        </div>
        <div class="flex-1 overflow-auto">
          <table class="w-full text-left text-[10px] sm:text-xs">
            <thead class="bg-black/40 text-gray-500 sticky top-0">
              <tr>
                <th class="p-2 font-normal">MAG</th>
                <th class="p-2 font-normal">LOCATION</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-800/50">
              <tr v-for="(quake, i) in earthquakes.slice(0, 15)" :key="i" class="hover:bg-gray-800/50 cursor-pointer" @click="focusMap(quake.latitude, quake.longitude)">
                <td class="p-2 font-bold text-yellow-400">{{ quake.magnitude.toFixed(1) }}</td>
                <td class="p-2 text-gray-300 truncate max-w-[120px]">{{ quake.title }}</td>
              </tr>
              <tr v-if="earthquakes.length === 0"><td colspan="2" class="p-4 text-center text-gray-600">NO RECENT QUAKES</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Crime Data Tile (Spans 3 cols, 6 rows) -->
      <div class="col-span-3 row-span-6 bg-gray-900/80 border border-gray-800 rounded-xl overflow-hidden flex flex-col">
        <div class="bg-gray-800/80 border-b border-gray-700 px-4 py-1.5 text-[10px] font-bold text-red-500 tracking-widest flex justify-between">
          <span>INCIDENT REPORTS (CRIME)</span>
        </div>
        <div class="flex-1 overflow-auto">
          <table class="w-full text-left text-[10px] sm:text-xs">
            <thead class="bg-black/40 text-gray-500 sticky top-0">
              <tr>
                <th class="p-2 font-normal">TYPE</th>
                <th class="p-2 font-normal">CITY</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-800/50">
              <tr v-for="(crime, i) in crimes.slice(0, 15)" :key="i" class="hover:bg-gray-800/50 cursor-pointer" @click="focusMap(crime.latitude, crime.longitude)">
                <td class="p-2 font-bold text-red-400 truncate max-w-[100px]">{{ crime.category }}</td>
                <td class="p-2 text-gray-500 truncate max-w-[100px]">{{ crime.city }}</td>
              </tr>
              <tr v-if="crimes.length === 0"><td colspan="2" class="p-4 text-center text-gray-600">NO INCIDENTS LOGGED</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Cameras List (Spans 3 cols, 6 rows) -->
      <div class="col-span-3 row-span-6 bg-gray-900/80 border border-gray-800 rounded-xl overflow-hidden flex flex-col">
        <div class="bg-gray-800/80 border-b border-gray-700 px-4 py-1.5 text-[10px] font-bold text-cyan-400 tracking-widest flex justify-between">
          <span>SURVEILLANCE NODES</span>
        </div>
        <div class="flex-1 overflow-auto">
          <table class="w-full text-left text-[10px] sm:text-xs">
            <thead class="bg-black/40 text-gray-500 sticky top-0">
              <tr>
                <th class="p-2 font-normal">ID</th>
                <th class="p-2 font-normal">LOCATION</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-800/50">
              <tr v-for="(cam, i) in dotCams.slice(0, 30)" :key="i" class="hover:bg-gray-800/50 cursor-pointer" @click="activeCamera = cam; focusMap(cam.latitude, cam.longitude)">
                <td class="p-2 font-bold text-cyan-500 truncate max-w-[80px]">{{ cam.name || cam.id || 'CAM' }}</td>
                <td class="p-2 text-gray-300 truncate max-w-[100px]">{{ cam.city || 'Unknown' }}, {{ cam.country || 'Unknown' }}</td>
              </tr>
              <tr v-if="dotCams.length === 0"><td colspan="2" class="p-4 text-center text-gray-600">NO CAMS FOUND</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Camera Feed Intercept (Spans 3 cols, 6 rows) -->
      <div class="col-span-3 row-span-6 bg-gray-900/80 border border-gray-800 rounded-xl overflow-hidden flex flex-col relative group">
        <div class="bg-gray-800/80 border-b border-gray-700 px-4 py-1.5 text-[10px] font-bold text-pink-500 tracking-widest flex justify-between z-10 relative">
          <div class="flex items-center gap-2">
            <span v-if="activeCamera" class="w-2 h-2 rounded-full bg-red-500 animate-pulse shadow-[0_0_5px_red]"></span>
            <span>SURVEILLANCE INTERCEPT</span>
          </div>
        </div>
        <div class="flex-1 bg-black flex flex-col items-center justify-center relative overflow-hidden">
          <div class="absolute inset-0 pointer-events-none opacity-20 z-10" style="background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06)); background-size: 100% 4px, 6px 100%;"></div>
          <template v-if="activeCamera">
            <video v-if="activeCamera.type === 'video/mp4'" :src="activeCamera.feed_url" autoplay loop muted controls class="w-full h-full object-cover"></video>
            <img v-else :src="activeCamera.feed_url" alt="Camera Feed" class="w-full h-full object-contain relative z-0" @error="handleImageError" />
            <div class="absolute bottom-4 left-4 right-4 flex flex-col z-20">
              <span class="text-[10px] font-mono bg-black/80 text-white px-2 py-1 rounded border border-gray-700 w-fit">
                {{ activeCamera.name || activeCamera.id }} <br/>
                {{ activeCamera.city }}, {{ activeCamera.country }}
              </span>
            </div>
            
            <div class="absolute top-4 right-4 flex flex-col items-end gap-2 z-40 pointer-events-none">
              <div v-if="aiAnalysis.incidents && aiAnalysis.incidents.length > 0" class="flex flex-col items-end gap-1">
                <span v-for="(inc, idx) in aiAnalysis.incidents" :key="idx" class="text-[10px] font-bold bg-red-600/90 text-white px-2 py-0.5 rounded-full border border-red-400 shadow-[0_0_15px_red]">
                  DETECTED: {{ inc.toUpperCase() }}
                </span>
              </div>
              <div v-if="aiAnalysis.description && !isAnalyzing" class="group relative cursor-pointer mt-1 pointer-events-auto">
                <div class="w-6 h-6 rounded-full bg-cyan-500/80 text-white flex items-center justify-center font-bold text-xs border border-cyan-400 shadow-[0_0_10px_cyan]">i</div>
                <div class="absolute right-0 mt-2 w-64 bg-gray-900/95 border border-cyan-500/50 rounded p-2 text-[10px] text-cyan-100 opacity-0 group-hover:opacity-100 transition-opacity shadow-xl z-50 pointer-events-none">
                  <span class="font-bold text-cyan-400 block mb-1">AI SCENE ANALYSIS</span>
                  {{ aiAnalysis.description }}
                </div>
              </div>
              <div v-if="isAnalyzing" class="text-[10px] font-mono text-cyan-400 animate-pulse bg-black/80 px-2 py-1 rounded border border-cyan-900 mt-2">
                ANALYZING FEED...
              </div>
            </div>
            <button @click="cycleCamera" class="absolute inset-0 z-30 opacity-0 cursor-pointer w-full h-full"></button>

          </template>
        </div>
      </div>

      <!-- Aviation / Flights Table (Spans 3 cols, 6 rows) -->
      <div class="col-span-3 row-span-6 bg-gray-900/80 border border-gray-800 rounded-xl overflow-hidden flex flex-col">
        <div class="bg-gray-800/80 border-b border-gray-700 px-4 py-1.5 text-[10px] font-bold text-green-400 tracking-widest flex justify-between">
          <span>ATC TRANSPONDERS</span>
        </div>
        <div class="flex-1 overflow-auto">
          <table class="w-full text-left text-[10px] sm:text-xs">
            <thead class="bg-black/40 text-gray-500 sticky top-0">
              <tr>
                <th class="p-2 font-normal">CALLSIGN</th>
                <th class="p-2 font-normal">ORIGIN</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-800/50">
              <tr v-for="(flight, i) in flights.slice(0, 15)" :key="i" class="hover:bg-gray-800/50 cursor-pointer" @click="focusMap(flight.latitude, flight.longitude)">
                <td class="p-2 font-bold text-white">{{ flight.callsign }}</td>
                <td class="p-2 text-gray-400 truncate max-w-[100px]">{{ flight.country_of_origin }}</td>
              </tr>
              <tr v-if="flights.length === 0"><td colspan="2" class="p-4 text-center text-gray-600">AWAITING RADAR SWEEP...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import * as L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';
import axios from 'axios';
import { otelLog } from './otlpLogger';

const REFRESH_INTERVAL_SECONDS = 60;
let mapInstance: L.Map | null = null;
let heatLayer: any = null;

const dotCams = ref<any[]>([]);
const crimes = ref<any[]>([]);
const earthquakes = ref<any[]>([]);
const flights = ref<any[]>([]);
const fires = ref<any[]>([]);
const sansData = ref<any>(null);
const dshieldPorts = ref<any[]>([]);
const issTracker = ref<any>(null);

const activeCamera = ref<any>(null);
const countdown = ref(REFRESH_INTERVAL_SECONDS);
let sweepTimer: number | undefined;
let camCycleTimer: number | undefined;


const flightError = ref(false);

const aiAnalysis = ref({ description: '', incidents: [] });
const isAnalyzing = ref(false);


const heatmapPoints = computed(() => {
  const points: [number, number, number][] = []; 
  fires.value.forEach(f => points.push([parseFloat(f.latitude), parseFloat(f.longitude), 1.0]));
  crimes.value.forEach(c => points.push([parseFloat(c.latitude), parseFloat(c.longitude), 0.8]));
  flights.value.forEach(f => points.push([parseFloat(f.latitude), parseFloat(f.longitude), 0.4]));
  earthquakes.value.forEach(e => points.push([parseFloat(e.latitude), parseFloat(e.longitude), Math.min(1.0, e.magnitude / 6)]));
  dotCams.value.forEach(c => { if(c.latitude) points.push([parseFloat(c.latitude), parseFloat(c.longitude), 0.2]); });
  return points;
});

watch(heatmapPoints, (newPoints) => {
  if (!mapInstance || !heatLayer) return;
  heatLayer.setLatLngs(newPoints);
}, { deep: true });

const focusMap = (lat: number, lng: number) => {
  if (mapInstance) mapInstance.flyTo([lat, lng], 5, { duration: 1.5 });
};

const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement;
  img.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 400 300"><rect width="400" height="300" fill="%23000"/><text x="50%" y="50%" font-family="monospace" font-size="12" fill="%23ff0000" text-anchor="middle">LINK SEVERED</text></svg>';
};


const analyzeCCTVFeed = async (cam: any) => {
  if (!cam || !cam.feed_url) return;
  // Skip video for now, only images
  if (cam.type === 'video/mp4') return;
  
  
  isAnalyzing.value = true;
  aiAnalysis.value = { description: '', incidents: [] };
  otelLog('INFO', `Initiating cloud vision analysis on CCTV feed from ${cam.city || 'Unknown'}.`);

  
  try {
    const res = await axios.post(`http://${window.location.hostname}:8001/api/vision`, { imageUrl: cam.feed_url });

    if (res.data) {
      aiAnalysis.value = res.data;
      if (res.data.incidents && res.data.incidents.length > 0) {
        otelLog('ERROR', `AI Vision detected critical incident in ${cam.city || 'Unknown'}: ${res.data.incidents.join(', ')}`);
      } else {
        otelLog('INFO', `AI Vision analysis complete for ${cam.city || 'Unknown'}. No anomalies detected.`);
      }
    }


  } catch (e) {
    console.error('AI Analysis failed:', e);
    otelLog('ERROR', `AI Vision model analysis failed or timed out for ${cam.city || 'Unknown'}.`);

  } finally {
    isAnalyzing.value = false;
  }
};

const cycleCamera = () => {
    if (dotCams.value.length === 0) return;
    const randomIdx = Math.floor(Math.random() * dotCams.value.length);
    activeCamera.value = dotCams.value[randomIdx];
    focusMap(activeCamera.value.latitude, activeCamera.value.longitude);
    analyzeCCTVFeed(activeCamera.value);
};


const startCamCycle = () => {
    camCycleTimer = window.setInterval(() => { cycleCamera(); }, 30000);
};

// --- FETCHERS ---
const fetchISS = async () => {
  try {
    const res = await axios.get("https://api.wheretheiss.at/v1/satellites/25544");
    issTracker.value = res.data;
  
    otelLog('WARN', 'ISS orbital tracker API connection failed.');
  
    otelLog('WARN', 'SANS Internet Storm Center DShield API failed.');
  
    otelLog('WARN', 'NASA FIRMS active fire API timed out or failed.');
  
    otelLog('WARN', 'USGS Earthquake JSON feed unavailable.');
  } catch (e) {}




};

const fetchSANS = async () => {
  try {
    const res = await axios.get("https://isc.sans.edu/api/infocon?json");
    if(res.data && res.data.status) sansData.value = res.data;

    // Fetch DShield Top Ports
    const portsRes = await axios.get("https://isc.sans.edu/api/topports/records/10?json");
    if(portsRes.data) {
        dshieldPorts.value = portsRes.data;
    }
  } catch (e) {}
};

const fetchFires = async () => {
  try {
    const res = await axios.get(`https://firms.modaps.eosdis.nasa.gov/api/area/csv/063b0c36734b7e2196ce3b1407acd23e/VIIRS_SNPP_NRT/world/1`);
    const lines = res.data.split('\n').slice(1, 200); 
    const parsedFires = [];
    for (const line of lines) {
      const parts = line.split(',');
      if (parts.length > 2 && !isNaN(parseFloat(parts[0]))) {
        parsedFires.push({ latitude: parseFloat(parts[0]), longitude: parseFloat(parts[1]), brightness: parts[2] });
      }
    }
    fires.value = parsedFires;
  } catch (e) {}
};

const fetchFlights = async () => {
  flightError.value = false;
  try {
    const res = await axios.get("https://api.adsb.lol/v2/ladd", { timeout: 8000 });
    
    if (res.data && res.data.ac) {
        flights.value = res.data.ac.map((ac: any) => ({
        callsign: ac.flight ? ac.flight.trim() : "UNKNOWN", country_of_origin: ac.r || "UNKNOWN", longitude: ac.lon, latitude: ac.lat, velocity: ac.gs, altitude: ac.alt_baro
        })).filter((f: any) => f.latitude && f.longitude);
    } else {
        flights.value = [];
    }
  } catch (e) { 
      
    otelLog('ERROR', 'Global ADS-B flight transponder API failed (api.adsb.lol).');
    flightError.value = true;
  }

};

const fetchEarthquakes = async () => {
  try {
    const res = await axios.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson");
    earthquakes.value = (res.data.features || []).map((f: any) => ({
      id: f.id, title: f.properties.title, magnitude: f.properties.mag, time: new Date(f.properties.time).toISOString(), longitude: f.geometry.coordinates[0], latitude: f.geometry.coordinates[1]
    }));
  } catch (e) {}
};

const fetchLocalBackups = async () => {
  try {
    const dotRes = await fetch(import.meta.env.BASE_URL + 'data/dot_cameras_expanded.json');
    if (dotRes.ok) {
      dotCams.value = (await dotRes.json()).cameras.slice(0, 1000); 
      if (!activeCamera.value && dotCams.value.length > 0) {
        cycleCamera();
        startCamCycle();
      }
    }
    const crimeRes = await fetch(import.meta.env.BASE_URL + 'data/live_crime_data.json');
    if (crimeRes.ok) crimes.value = (await crimeRes.json()).incidents;
  } catch (e) {}
};

const forceFullSweep = async () => {
  countdown.value = REFRESH_INTERVAL_SECONDS;
  await Promise.allSettled([
    fetchISS(), fetchSANS(), fetchFires(), fetchFlights(), fetchEarthquakes(), fetchLocalBackups()
  ]);
};

onMounted(() => {
  mapInstance = L.map('map', { center: [20, 0], zoom: 2, zoomControl: false, attributionControl: false });
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { subdomains: 'abcd', maxZoom: 19 }).addTo(mapInstance);
  
  // @ts-ignore
  heatLayer = L.heatLayer([], { radius: 15, blur: 20, maxZoom: 10, max: 1.0, gradient: {0.4: 'cyan', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'} }).addTo(mapInstance);

  forceFullSweep();
otelLog('INFO', 'OSINT Dashboard initialized and running full sensor sweep.');

  sweepTimer = window.setInterval(() => {
    countdown.value -= 1;
    if (countdown.value <= 0) { forceFullSweep(); otelLog('INFO', 'OSINT Dashboard executing periodic 60s sensor sweep.'); }
  }, 1000);
});

onUnmounted(() => {
  if (sweepTimer) clearInterval(sweepTimer);
  if (camCycleTimer) clearInterval(camCycleTimer);
});
</script>

<style scoped>
:deep(.leaflet-pane) { z-index: 10 !important; }
:deep(.leaflet-top), :deep(.leaflet-bottom) { z-index: 10 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0, 255, 255, 0.2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0, 255, 255, 0.5); }
</style>

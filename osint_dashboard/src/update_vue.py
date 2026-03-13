import re
import sys

with open('/home/openclaw/.openclaw/workspace/OSInt/dashboard/src/App.vue', 'r') as f:
    content = f.read()

template_start = content.find('    <!-- Main Grid Dashboard -->')
template_end = content.find('    </div>\n  </div>\n</template>')

new_grid = """    <!-- Main Grid Dashboard -->
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
                <td class="p-2 font-bold text-red-400">{{ port.port }}</td>
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
      </div>\n"""

new_content = content[:template_start] + new_grid + content[template_end:]

with open('/home/openclaw/.openclaw/workspace/OSInt/dashboard/src/App.vue', 'w') as f:
    f.write(new_content)

import re

with open('src/App.vue', 'r') as f:
    content = f.read()

# Inject import
content = content.replace("import axios from 'axios';", "import axios from 'axios';\nimport { otelLog } from './otlpLogger';")

# Add init log
content = content.replace("forceFullSweep();", "forceFullSweep();\notelLog('INFO', 'OSINT Dashboard initialized and running full sensor sweep.');")

# fetchISS
iss_err = """
    otelLog('WARN', 'ISS orbital tracker API connection failed.');
  } catch (e) {}
"""
content = re.sub(r'\} catch \(e\) \{\}', iss_err, content, count=1)

# fetchSANS
sans_err = """
    otelLog('WARN', 'SANS Internet Storm Center DShield API failed.');
  } catch (e) {}
"""
content = re.sub(r'\} catch \(e\) \{\}', sans_err, content, count=1)

# fetchFires
fire_err = """
    otelLog('WARN', 'NASA FIRMS active fire API timed out or failed.');
  } catch (e) {}
"""
content = re.sub(r'\} catch \(e\) \{\}', fire_err, content, count=1)

# fetchFlights
flight_err = """
    otelLog('ERROR', 'Global ADS-B flight transponder API failed (api.adsb.lol).');
    flightError.value = true;
  }
"""
content = content.replace("flightError.value = true;\n  }", flight_err)

# fetchEarthquakes
eq_err = """
    otelLog('WARN', 'USGS Earthquake JSON feed unavailable.');
  } catch (e) {}
"""
content = re.sub(r'\} catch \(e\) \{\}', eq_err, content, count=1)

# AI Vision log injection
ai_logic_start = """
  isAnalyzing.value = true;
  aiAnalysis.value = { description: '', incidents: [] };
  otelLog('INFO', `Initiating cloud vision analysis on CCTV feed from ${cam.city || 'Unknown'}.`);
"""
content = content.replace("isAnalyzing.value = true;\n  aiAnalysis.value = { description: '', incidents: [] };", ai_logic_start)

ai_logic_success = """
    if (res.data) {
      aiAnalysis.value = res.data;
      if (res.data.incidents && res.data.incidents.length > 0) {
        otelLog('ERROR', `AI Vision detected critical incident in ${cam.city || 'Unknown'}: ${res.data.incidents.join(', ')}`);
      } else {
        otelLog('INFO', `AI Vision analysis complete for ${cam.city || 'Unknown'}. No anomalies detected.`);
      }
    }
"""
content = content.replace("""    if (res.data) {
      aiAnalysis.value = res.data;
    }""", ai_logic_success)

ai_logic_err = """
  } catch (e) {
    console.error('AI Analysis failed:', e);
    otelLog('ERROR', `AI Vision model analysis failed or timed out for ${cam.city || 'Unknown'}.`);
"""
content = content.replace("  } catch (e) {\n    console.error('AI Analysis failed:', e);", ai_logic_err)

with open('src/App.vue', 'w') as f:
    f.write(content)

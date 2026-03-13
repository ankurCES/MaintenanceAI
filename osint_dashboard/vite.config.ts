import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'

const apiPlugin = {
  name: 'api-plugin',
  configureServer(server) {
    server.middlewares.use(async (req, res, next) => {
      if ((req.url === '/api/vision' || req.url === '/OSInt-dashboard/api/vision') && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString() });
        req.on('end', async () => {
          req.body = JSON.parse(body || '{}');
          try {
            const mod = await import('./api/vision.js');
            res.status = (code) => { res.statusCode = code; return res; };
            res.json = (data) => {
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify(data));
            };
            await mod.default(req, res);
          } catch (e) {
            console.error(e);
            res.statusCode = 500;
            res.end(JSON.stringify({ error: e.message }));
          }
        });
        return;
      }
      next();
    });
  }
}

export default defineConfig({
  base: '/',
  plugins: [vue(), apiPlugin],
  server: {
    proxy: {
      '^/OSInt-dashboard/api/telemetry': {
        target: 'http://127.0.0.1:8080/ingest/generic',
        changeOrigin: true,
        rewrite: () => ''
      }
    }
  }
})

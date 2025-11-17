import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      host: '0.0.0.0',
      port: parseInt(env.VITE_PORT || '5173'),
      proxy: {
        '/api': {
          target: env.VITE_API_URL,
          changeOrigin: true
        },
        '/ws': {
          target: env.VITE_WS_URL,
          ws: true
        }
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['vue', 'vue-router', 'pinia'],
            'ton': ['@tonconnect/ui-vue', '@ton/ton'],
            'telegram': ['@telegram-apps/sdk-vue']
          }
        }
      }
    }
  }
})

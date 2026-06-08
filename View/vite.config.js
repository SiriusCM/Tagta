import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'

const basePath = process.env.VITE_BASE_PATH || '/'

export default defineConfig({
    base: basePath,
    plugins: [vue()],
    server: {
        port: 5173,
        proxy: {
            '/api': {
                // 测试环境
                //target: 'http://localhost:8080',
                // 生产环境:
                target: 'http://116.196.69.192:8080',
                changeOrigin: true
            }
        }
    }
})
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 從環境變數讀取配置
// 使用 Node.js 的 process.env（在構建時可用）
// @ts-ignore - process 在 Node.js 環境中可用
const allowedHostsEnv = process.env.VITE_PREVIEW_ALLOWED_HOSTS || 'all'

// 解析 allowedHosts
// Vite 的 allowedHosts 類型為 true | string[]
// 'all' 或 '*' 表示允許所有 host，設置為 true
// 否則解析為字符串數組
const allowedHosts: true | string[] = 
  (allowedHostsEnv === 'all' || allowedHostsEnv === '*')
    ? true
    : allowedHostsEnv.split(',').map(h => h.trim())

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    // 端口可以通過環境變數 VITE_PORT 設置（預設 5173）
    port: 5173
  },
  preview: {
    host: true,
    // 端口可以通過環境變數 VITE_PREVIEW_PORT 設置（預設 4173）
    port: 4173,
    // 允許的 host（從環境變數 VITE_PREVIEW_ALLOWED_HOSTS 讀取）
    // 格式: 用逗號分隔多個域名，例如: "example.com,app.example.com"
    // 設置為 "all" 或 "*" 允許所有 host（設置為 true）
    // 如果未設置，預設為 true（允許所有 host）
    allowedHosts
  },
  // 將環境變數暴露給客戶端（僅 VITE_ 開頭的變數）
  envPrefix: 'VITE_'
});
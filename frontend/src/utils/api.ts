/**
 * API 配置工具
 * 從環境變數讀取後端 API 基礎 URL
 */

// Vite 環境變數必須以 VITE_ 開頭才能在客戶端訪問
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
console.log('API_BASE_URL', API_BASE_URL);

/**
 * 獲取完整的 API URL
 * @param endpoint - API 端點（例如：'/api/health'）
 * @returns 完整的 API URL
 */
export function getApiUrl(endpoint: string): string {
  // 如果設置了 API_BASE_URL，使用它；否則使用相對路徑（同源）
  if (API_BASE_URL) {
    // 確保 endpoint 以 / 開頭
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    // 移除 API_BASE_URL 末尾的斜線（如果有的話）
    let baseUrl = API_BASE_URL.replace(/\/$/, '');
    
    // 如果 baseUrl 不包含 protocol，自動加上 http://
    // 這可以處理 Zeabur 等平台可能移除 protocol 的情況
    if (!baseUrl.match(/^https?:\/\//)) {
      // 對於內部服務（.internal 域名），通常使用 http://
      // 如果域名包含 .internal，使用 http://；否則使用 https://
      if (baseUrl.includes('.internal')) {
        baseUrl = `http://${baseUrl}`;
      } else {
        baseUrl = `https://${baseUrl}`;
      }
    }
    
    return `${baseUrl}${normalizedEndpoint}`;
  }
  // 如果沒有設置 API_BASE_URL，使用相對路徑（適用於同源部署）
  return endpoint;
}

/**
 * 獲取後端 API 基礎 URL（用於日誌等）
 */
export function getApiBaseUrl(): string {
  return API_BASE_URL || '(same origin)';
}
// 简单的加密/解密工具（使用 Web Crypto API）

// 生成一个简单的密钥（基于域名，这样每个域名都有不同的密钥）
function getKeyMaterial(): Promise<CryptoKey> {
  const encoder = new TextEncoder();
  // 使用域名 + 固定字符串作为密钥材料
  const keyMaterial = encoder.encode(`${window.location.hostname}anki-generator-secret-key-2024`);
  
  return crypto.subtle.importKey(
    'raw',
    keyMaterial,
    { name: 'PBKDF2' },
    false,
    ['deriveBits', 'deriveKey']
  );
}

// 派生加密密钥
async function deriveKey(): Promise<CryptoKey> {
  const keyMaterial = await getKeyMaterial();
  const encoder = new TextEncoder();
  const salt = encoder.encode('anki-generator-salt');
  
  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: 100000,
      hash: 'SHA-256'
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  );
}

/**
 * 加密文本
 */
export async function encrypt(text: string): Promise<string> {
  try {
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const key = await deriveKey();
    const iv = crypto.getRandomValues(new Uint8Array(12)); // 12 bytes for GCM
    
    const encrypted = await crypto.subtle.encrypt(
      {
        name: 'AES-GCM',
        iv: iv
      },
      key,
      data
    );
    
    // 将 IV 和加密数据组合：IV (12 bytes) + encrypted data
    const combined = new Uint8Array(iv.length + encrypted.byteLength);
    combined.set(iv, 0);
    combined.set(new Uint8Array(encrypted), iv.length);
    
    // 转换为 base64
    return btoa(String.fromCharCode(...combined));
  } catch (error) {
    console.error('Encryption error:', error);
    // 如果加密失败，返回 base64 编码（至少不是明文）
    return btoa(unescape(encodeURIComponent(text)));
  }
}

/**
 * 解密文本
 */
export async function decrypt(encryptedText: string): Promise<string> {
  try {
    const combined = Uint8Array.from(atob(encryptedText), c => c.charCodeAt(0));
    const iv = combined.slice(0, 12);
    const encrypted = combined.slice(12);
    
    const key = await deriveKey();
    
    const decrypted = await crypto.subtle.decrypt(
      {
        name: 'AES-GCM',
        iv: iv
      },
      key,
      encrypted
    );
    
    const decoder = new TextDecoder();
    return decoder.decode(decrypted);
  } catch (error) {
    console.error('Decryption error:', error);
    // 如果解密失败，尝试作为 base64 解码（向后兼容）
    try {
      return decodeURIComponent(escape(atob(encryptedText)));
    } catch {
      throw new Error('Failed to decrypt');
    }
  }
}


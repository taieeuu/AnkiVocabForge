"""
FastAPI Server for Anki Generator
提供與 backend 相同的 API 接口，集成 backend2 的業務邏輯
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 從 routes 模組導入所有路由
from routes import api_router

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(title="Anki Generator API", version="2.0.0")

# 從環境變數讀取 CORS 設定
cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "*")
if cors_origins_env == "*":
    cors_origins = ["*"]
else:
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

logger.info(f"CORS allowed origins: {cors_origins}")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊所有路由
app.include_router(api_router)


if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)

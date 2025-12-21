# Backend 結構說明

## 目錄結構

```
backend/
├── main.py                # FastAPI 主應用文件（簡潔版）
├── routes/                # API 路由模組
│   ├── __init__.py        # 路由註冊
│   ├── health.py          # 健康檢查路由
│   ├── settings.py        # 設置 API 路由
│   ├── analyze.py         # 分析 API 路由（圖片/PDF）
│   ├── generate.py        # 生成 API 路由（文章/單字/AI）
│   ├── generate_helpers.py # 生成路由的共用輔助函數
│   └── files.py           # 文件管理 API 路由
├── helpers/               # 共用工具函數
│   ├── __init__.py
│   ├── session.py         # Session 管理工具
│   ├── file_utils.py      # 文件處理工具
│   └── api_key.py         # API Key 驗證和管理
├── libs/                  # 核心庫模組
│   ├── config.py          # 配置管理
│   ├── logger.py          # 日誌系統
│   ├── gpt.py             # GPT 客戶端
│   ├── parser.py          # 文件解析器
│   └── anki_logic.py      # Anki 邏輯
├── service/               # 業務邏輯服務層
│   ├── main_processor.py  # 主處理器
│   ├── anki_service.py    # Anki 服務
│   └── parser_service.py  # 解析服務
├── utils.py               # 其他工具函數（語音相關）
└── requirements.txt       # Python 依賴

```

## 主要改進

### 1. 模組化路由
- 將原本 1113 行的 `main.py`（原 `api_server.py`）拆分為多個路由文件
- 每個路由文件負責特定的 API 端點組
- 更容易維護和擴展

### 2. 共用工具模組
- `helpers/` 目錄包含可重用的工具函數
- 減少代碼重複
- 提高代碼可測試性

### 3. 清晰的職責分離
- **routes/**: API 端點定義
- **helpers/**: 共用工具函數
- **service/**: 業務邏輯
- **libs/**: 核心庫和配置

## API 路由組織

### Health & Settings
- `GET /api/health` - 健康檢查
- `GET /api/settings` - 獲取設置
- `POST /api/settings` - 更新設置

### Analyze
- `POST /api/analyze/images` - 分析 PDF/圖片
- `GET /api/files/image/{session_id}/{filename}` - 獲取圖片

### Generate
- `POST /api/generate/article` - 從文章生成卡片
- `POST /api/generate/vocab` - 從單字列表生成卡片
- `POST /api/generate/ai` - AI 生成卡片
- `POST /api/generate/grammar` - 從文法生成卡片（待實現）
- `POST /api/generate/package` - 打包卡片為 .apkg

### Files
- `GET /api/files/download/{session_id}` - 下載整個 session
- `GET /api/files/list/{session_id}` - 列出 session 文件
- `GET /api/files/download/{session_id}/{file_path}` - 下載特定文件
- `DELETE /api/files/cleanup/{session_id}` - 清理 session

## 使用方式

### 開發環境
```bash
cd backend
python main.py
```

### Docker
```bash
docker build -f Dockerfile -t anki-backend .
docker run -p 8000:8000 anki-backend
```

## 注意事項

- `utils.py` 保留用於向後兼容（`libs/gpt.py` 使用）
- Session 目錄結構：
  - `source/` - 原始輸入文件
  - `orig/` - 原始生成的卡片
  - `edited/` - 編輯後的卡片


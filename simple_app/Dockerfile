# ── Dockerfile 說明 ──────────────────────────────────────
#
# Dockerfile 是一份「食譜」，告訴 Cloud Run 如何準備執行環境。
# 每一行 FROM / WORKDIR / COPY / RUN / CMD 都是一個步驟。
#
# 部署流程：
#   Dockerfile → (build) → Docker Image → (push) → Cloud Run 執行
#
# ─────────────────────────────────────────────────────────

# Step 1：選擇基底映像檔
# python:3.11-slim 是官方提供的精簡版 Python 3.11 環境
FROM python:3.11-slim

# Step 2：設定容器內的工作目錄
# 之後的指令都會在這個目錄下執行
WORKDIR /app

# Step 3：先複製 requirements.txt，安裝 Python 套件
# 為什麼先複製 requirements.txt？因為 Docker 有快取機制，
# 只要 requirements.txt 沒改變，這一層就不會重新執行，加快 build 速度
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4：複製程式碼
COPY app.py .

# Step 5：設定環境變數
# Cloud Run 會自動注入 PORT 環境變數，程式必須監聽這個 port
ENV PORT=8080

# Step 6：啟動指令
# gunicorn 是正式環境用的 Python web server（比 Flask 內建的更穩定）
# --bind 0.0.0.0:8080  監聽所有網路介面的 8080 port
# --workers 1          使用 1 個 worker process
# --threads 8          每個 worker 8 個執行緒（處理並發請求）
# app:app              第一個 app 是模組名稱(app.py)，第二個是 Flask 物件名稱
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "app:app"]

# 使用官方 Python 3.11 slim 映像檔
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY app.py .

# Cloud Run 會自動設定 PORT 環境變數（預設 8080）
ENV PORT=8080

# 使用 gunicorn 啟動（正式環境不用 Flask dev server）
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "app:app"]

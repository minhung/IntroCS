# coding=utf-8
"""
【Cloud Run 入門範例】
=====================
這是一個簡單的 Flask 網頁程式，示範：
  1. 如何建立基本的網頁路由（Route）
  2. 如何接收表單輸入
  3. 如何回傳 HTML 結果

學生可以在此基礎上，嘗試：
  - 加入更多路由
  - 加入自己的運算邏輯
  - 修改 HTML 頁面樣式
"""

from flask import Flask, request
import html

# ── 建立 Flask app ───────────────────────────────────────
# Flask(__name__) 告訴 Flask 這個 app 的名稱是目前的模組
app = Flask(__name__)


# ── 路由 1：首頁 GET / ───────────────────────────────────
# @app.route('/') 代表當使用者開啟網站根目錄時，執行下面的函式
@app.route('/')
def index():
    """顯示輸入表單"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Cloud Run 範例</title>
      <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 60px auto; }
        input[type=text] { padding: 8px; width: 300px; font-size: 16px; }
        input[type=submit] { padding: 8px 20px; font-size: 16px; cursor: pointer; }
        .hint { color: #888; font-size: 13px; }
      </style>
    </head>
    <body>
      <h2>🌐 Cloud Run 範例程式</h2>
      <p>輸入你的名字，讓程式算出你的幸運數字！</p>

      <form action="/result" method="post">
        <label>你的名字：</label><br><br>
        <input type="text" name="username" placeholder="請輸入名字">
        <input type="submit" value="送出">
      </form>

      <br>
      <p class="hint">
        這個程式部署在 Google Cloud Run 上。<br>
        程式結構：Flask（Python）→ Dockerfile → Cloud Run
      </p>
    </body>
    </html>
    """


# ── 路由 2：結果頁 POST /result ──────────────────────────
# methods=['POST'] 代表這個路由只接受 POST 請求（表單送出）
@app.route('/result', methods=['POST'])
def result():
    """接收表單資料，計算結果，回傳結果頁"""

    # request.form.get() 取得表單欄位的值
    # 若欄位不存在，回傳預設值 '訪客'
    username = request.form.get('username', '訪客')

    # ── 在這裡加入你的程式邏輯 ──
    # 以下是一個簡單的「幸運數字」計算範例：
    # 把名字每個字的 Unicode 碼點加總，取餘數
    lucky_number = sum(ord(c) for c in username) % 100

    # 根據幸運數字給出不同的訊息
    if lucky_number >= 80:
        message = "✨ 今天大吉大利！"
    elif lucky_number >= 50:
        message = "😊 今天運氣不錯！"
    elif lucky_number >= 30:
        message = "😐 今天平平淡淡。"
    else:
        message = "😅 今天小心一點..."

    # html.escape() 防止 XSS 攻擊（使用者輸入的內容不能直接放進 HTML）
    safe_name = html.escape(username)

    # 回傳 HTML 字串給使用者
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>結果</title>
      <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 60px auto; }}
        .result-box {{ background: #f0f8ff; border-radius: 10px; padding: 30px; text-align: center; }}
        .lucky {{ font-size: 60px; font-weight: bold; color: #2E75B6; }}
      </style>
    </head>
    <body>
      <div class="result-box">
        <h2>🎲 {safe_name} 的幸運數字</h2>
        <div class="lucky">{lucky_number}</div>
        <h3>{message}</h3>
        <p>計算方式：名字每個字的 Unicode 碼點加總 ÷ 100 的餘數</p>
      </div>
      <br>
      <a href="/">← 返回首頁</a>
    </body>
    </html>
    """


# ── 啟動程式 ─────────────────────────────────────────────
# 這段只在「直接執行 python app.py」時才會啟動
# 部署到 Cloud Run 後，Dockerfile 裡的 gunicorn 會負責啟動，不會執行這段
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    # debug=True 會在程式碼修改後自動重新載入（只用於開發環境）
    app.run(host='0.0.0.0', port=port, debug=True)

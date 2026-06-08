# 骰子累積點數遊戲 - Flask 版本說明

這是一個簡單的 Flask 網頁程式，功能是讓兩位玩家輸入姓名，每回合擲骰子累積點數。
有興趣的同學可以用這個架構把自己寫的 Python 程式部署到 Render 或其他平台上。

* [骰子累積點數遊戲 Render 連結](https://introcs-hello.onrender.com/)

---

## 程式簡單說明

### 1. 路由（Route）的概念

Flask 用 `@app.route` 裝飾器（decorator）來對應網址和處理函式：

```python
@app.route('/')
def index():
    ...

@app.route('/play', methods=['POST'])
def play():
    ...
```

`'/'` 由 `index()` 處理；`'/play'` 由 `play()` 處理。
`methods=['POST']` 表示這個路由只接受表單送出的 POST 請求。

---

### 2. 網頁輸入方式

網頁輸入方式有兩種。

第一種是在文字輸入欄輸入資料（首頁表單）：

```html
<form action="/play" method="post">
  <p>Name of Player 1</p>
  <textarea name="player_1" rows="1" cols="30"></textarea>
  <p>Name of Player 2</p>
  <textarea name="player_2" rows="1" cols="30"></textarea>
  <input type="submit" name="PName" value="Submit">
</form>
```

第二種是按鈕輸入（結果頁）：

```html
<form action="/play" method="post">
  <a href="/"><button type="button">Replay</button></a>
  <input type="submit" name="step" value="Throw Again">
</form>
```

請注意 `input` 裡的 `name` 屬性，程式會用這個名稱來判斷使用者按了哪個按鈕。

---

### 3. 取得輸入資料

Flask 用 `request.form.get(name)` 取得表單輸入的內容：

```python
player1 = request.form.get('player_1')  # 取得 name="player_1" 欄位的內容
```

判斷使用者按了哪個按鈕：

```python
if request.form.get('PName') is not None:
    # 使用者按了 Submit（第一次送出）
    ...

if request.form.get('step') is not None:
    # 使用者按了 Throw Again
    ...
```

---

### 4. 用 session 儲存遊戲狀態

若用一般變數儲存遊戲狀態，在 Cloud 環境中多個使用者同時玩時會互相干擾。

Flask 的 `session` 會把資料存在使用者的瀏覽器 cookie 裡，每個使用者有自己獨立的狀態：

```python
session['hp1'] = randint(1, 6)   # 寫入
hp1 = session.get('hp1', 0)      # 讀取
```

使用 `session` 需要設定 `secret_key`：

```python
app.secret_key = 'dice-game-secret-key-2024'
```

---

### 5. 中文處理

Python 3 的字串預設就是 unicode，可以直接使用中文，不需要額外處理：

```python
round_txt = f"{player1} 擲出點數 {dice1}，目前點數 {new_hp1}\n"
```

另外，將使用者輸入的內容放入 HTML 時，需用 `html.escape()` 防止安全性問題：

```python
import html
safe_text = html.escape(user_input)
```

---

## 部署到 Render

1. 將 `app.py` 和 `requirements.txt` 放入 GitHub repository
2. 前往 [render.com](https://render.com) 建立新的 Web Service，連結該 repository
3. 設定如下：
   - **Root Directory**：程式所在的子資料夾（若有）
   - **Build Command**：`pip install -r requirements.txt`
   - **Start Command**：`gunicorn app:app`
4. 部署完成後會得到一個 `https://xxx.onrender.com` 的網址

之後每次更新程式只要 push 到 GitHub，Render 會自動重新部署。

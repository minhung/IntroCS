# Flask 入門範例說明

這是一個給初學者參考的最簡單 Flask 網頁程式。輸入名字後，程式會根據名字的 Unicode 碼點計算出一個幸運數字。

同學可以在這個架構的基礎上，把自己寫的 Python 程式邏輯放進來，部署到 Render 或其他平台上。

---

## 程式簡單說明

### 1. 路由（Route）的概念

Flask 用 `@app.route` 裝飾器來對應網址和處理函式：

```python
@app.route('/')
def index():
    ...

@app.route('/result', methods=['POST'])
def result():
    ...
```

`'/'` 由 `index()` 處理，顯示首頁表單；`'/result'` 由 `result()` 處理計算結果。

一個程式可以有很多個路由，每個路由對應不同的網址和功能，同學可以依需求自行增加。

---

### 2. 網頁輸入方式

首頁表單讓使用者輸入名字：

```html
<form action="/result" method="post">
  <input type="text" name="username" placeholder="請輸入名字">
  <input type="submit" value="送出">
</form>
```

`action="/result"` 表示按下送出後，資料會傳送到 `/result` 這個路由。

Flask 用 `request.form.get(name)` 取得表單輸入的內容，若欄位不存在則回傳預設值：

```python
username = request.form.get('username', '訪客')
```

---

### 3. 加入自己的程式邏輯

取得輸入資料後，可以在這裡加入任何 Python 運算。以這個範例為例，把名字每個字的 Unicode 碼點加總取餘數：

```python
lucky_number = sum(ord(c) for c in username) % 100
```

同學可以把這段換成自己的計算邏輯，例如成績計算、遊戲判斷、資料處理等。

---

### 4. 回傳 HTML 結果

Flask 的路由函式直接回傳 HTML 字串給使用者。使用 Python 的 f-string 可以方便地把變數嵌入 HTML 裡：

```python
return f"""
<html>
  <body>
    <h2>{safe_name} 的幸運數字是 {lucky_number}</h2>
  </body>
</html>
"""
```

請注意 f-string 裡如果要用 CSS 的大括號 `{}`，需要寫成 `{{}}` 才不會被誤判為變數。

---

### 5. 安全性：html.escape()

將使用者輸入的內容直接放進 HTML 是有風險的，可能造成 XSS 攻擊。
一定要先用 `html.escape()` 處理後再放入 HTML：

```python
import html
safe_name = html.escape(username)
```

---

### 6. 啟動程式的方式

程式最底下這段：

```python
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
```

只在直接執行 `python app.py` 時才會啟動（本機測試用）。
部署到 Render 後，`gunicorn` 會負責啟動程式，不會執行這段。

---

## 同學可以嘗試的修改

- 把幸運數字的計算換成自己的邏輯
- 加入更多輸入欄位（例如兩個名字、數字輸入）
- 修改 HTML 的樣式讓頁面更好看
- 加入新的路由，做出多個頁面的網站

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

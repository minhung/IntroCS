# 姓名對戰遊戲 - Flask 版本說明

這是一個 Flask 網頁程式，輸入兩位玩家的姓名（至少三個中文字），程式會根據每個字的 Unicode 碼點計算出各項能力值，並模擬回合制對戰，決定勝負。

* [姓名對戰遊戲 - Render](https://introcs.onrender.com)

---

## 程式簡單說明

### 1. 路由（Route）的概念

Flask 用 `@app.route` 裝飾器來對應網址和處理函式：

```python
@app.route('/')
def main_page():
    ...

@app.route('/fight', methods=['POST'])
def fight():
    ...
```

`'/'` 由 `main_page()` 處理，顯示輸入表單；`'/fight'` 由 `fight()` 處理對戰邏輯。
`methods=['POST']` 表示這個路由只接受表單送出的 POST 請求。

---

### 2. 網頁輸入方式

首頁表單讓使用者輸入兩位玩家的姓名：

```html
<form action="/fight" method="post">
  <p>Name of Fighter 1 (至少三個中文字)</p>
  <textarea name="player_1" rows="1" cols="60"></textarea>
  <p>Name of Fighter 2 (至少三個中文字)</p>
  <textarea name="player_2" rows="1" cols="60"></textarea>
  <input type="submit" value="Submit">
</form>
```

Flask 用 `request.form.get(name)` 取得表單輸入的內容：

```python
player1 = request.form.get('player_1', '')
player2 = request.form.get('player_2', '')
```

---

### 3. 用 Unicode 碼點計算能力值

程式取姓名前三個字的 Unicode 碼點（每個中文字對應一個整數），作為計算各項能力值的依據：

```python
p1c1, p1c2, p1c3 = ord(player1[0]), ord(player1[1]), ord(player1[2])
```

`ord()` 是 Python 內建函式，可以取得字元的 Unicode 碼點，例如 `ord('陳')` 會得到 `38472`。

以 VIT（體力）為例，根據碼點範圍對應不同的數值：

```python
coe1 = (c1 - 34081) // 100
if coe1 == 0:          v1 = 333
elif -20 < coe1 < 0:   v1 = 297
...
```

這樣每個名字都會得到固定但看似隨機的能力值，STR、INT、DEX、AGI 也用相同方式計算。

---

### 4. 技能系統

程式定義了 16 個技能，每位玩家根據名字的碼點組合分配到其中 4 個：

```python
SKILLS = {
    'sk01': '機車店老闆的靈魂',
    'sk02': '計概期末報告',
    ...
}

def assign_skills(c1, c2, c3):
    sk1_key = f'sk{str((c1 % 8) + 1).zfill(2)}'
    sk2_key = ['sk04', 'sk09', 'sk12', 'sk14'][(c2 % 4)]
    ...
```

每回合用 `randint(0, 3)` 隨機從 4 個技能中選一個使出。

---

### 5. 回合制對戰

對戰邏輯是一個迴圈，兩位玩家輪流出招，直到其中一人 HP 歸零：

```python
for _ in range(MAX_ROUNDS):
    # player1 出招
    sk = p1_skills[randint(0, 3)]
    use_skill(p1, p2, sk)
    if p2['hp'] <= 0:
        break

    # player2 出招
    sk = p2_skills[randint(0, 3)]
    use_skill(p2, p1, sk)
    if p1['hp'] <= 0:
        break
```

設定 `MAX_ROUNDS = 200` 防止兩位玩家都很耐打時造成無限迴圈。

---

### 6. 逐回合顯示

所有回合的結果在伺服器端一次算完，HTML 裡將每個回合包在 `<div>` 中預設隱藏，由 JavaScript 控制按鈕逐回合顯示：

```javascript
function showNext() {
    current++;
    document.getElementById('round-' + current).classList.add('visible');
    if (current >= total) {
        document.getElementById('btn-next').style.display = 'none';
    }
}
```

---

### 7. 安全性：html.escape()

將使用者輸入的內容放入 HTML 時，需用 `html.escape()` 防止 XSS 攻擊：

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

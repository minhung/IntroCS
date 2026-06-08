# coding=utf-8
"""
骰子累積點數遊戲 - Flask / Python 3 版本
原版：webapp2 + Python 2（Google App Engine 舊版）
改寫：Flask + Python 3（適用 Render / Cloud Run）

遊戲規則：
  兩位玩家各自擲骰子（1~6），每按一次「Throw Again」累積點數。
  歷史 Log 會顯示每一回合的結果。
"""

from flask import Flask, request, session
from random import randint
import html

app = Flask(__name__)
# session 需要 secret_key 才能運作
app.secret_key = 'dice-game-secret-key-2024'

# ── 首頁：輸入兩位玩家名稱 ──────────────────────────────
MAIN_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>骰子遊戲</title>
</head>
<body>
  <p>這是一個簡單的程式，輸入兩個 player 姓名，每回擲骰子，累計點數。</p>
  <form action="/play" method="post">
    <p>Name of Player 1</p>
    <div><textarea name="player_1" rows="1" cols="30"></textarea></div>
    <p>Name of Player 2</p>
    <div><textarea name="player_2" rows="1" cols="30"></textarea></div>
    <div><input type="submit" name="PName" value="Submit"></div>
  </form>
</body>
</html>
"""


@app.route('/')
def index():
    """首頁：清除 session，顯示輸入表單"""
    session.clear()
    return MAIN_PAGE_HTML


@app.route('/play', methods=['POST'])
def play():
    """
    處理兩種情況：
    1. 第一次送出（PName）：初始化玩家、第一次擲骰
    2. 之後按「Throw Again」（step）：繼續累積點數
    """

    # ── 情況 1：第一次送出，初始化遊戲 ──────────────────
    if request.form.get('PName') is not None:
        player1 = request.form.get('player_1', '玩家1')
        player2 = request.form.get('player_2', '玩家2')

        dice1 = randint(1, 6)
        dice2 = randint(1, 6)

        # 把遊戲狀態存進 session
        session['player1'] = player1
        session['player2'] = player2
        session['hp1'] = dice1
        session['hp2'] = dice2
        session['round'] = 1
        session['log'] = []   # 歷史紀錄

        round_txt = (
            f"{player1} 擲出點數 {dice1}，目前點數 {dice1}\n"
            f"{player2} 擲出點數 {dice2}，目前點數 {dice2}\n"
        )
        session['log'] = [round_txt]

    # ── 情況 2：繼續擲骰 ─────────────────────────────────
    elif request.form.get('step') is not None:
        player1 = session.get('player1', '玩家1')
        player2 = session.get('player2', '玩家2')
        hp1 = session.get('hp1', 0)
        hp2 = session.get('hp2', 0)
        current_round = session.get('round', 1) + 1
        log = session.get('log', [])

        dice1 = randint(1, 6)
        new_hp1 = hp1 + dice1
        dice2 = randint(1, 6)
        new_hp2 = hp2 + dice2

        round_txt = (
            f"{player1} 目前點數 {hp1}\n"
            f"{player1} 擲出點數 {dice1}，目前點數 {new_hp1}\n"
            f"{player2} 目前點數 {hp2}\n"
            f"{player2} 擲出點數 {dice2}，目前點數 {new_hp2}\n"
        )

        log.append(round_txt)
        session['hp1'] = new_hp1
        session['hp2'] = new_hp2
        session['round'] = current_round
        session['log'] = log

    else:
        # 直接開啟 /play 沒有表單資料，導回首頁
        return '<p>請先輸入玩家名稱。<br><a href="/">返回</a></p>'

    # ── 產生結果頁 ───────────────────────────────────────
    player1 = session['player1']
    player2 = session['player2']
    current_round = session['round']
    log = session['log']
    current_txt = log[-1]   # 最新一回合

    # 歷史 Log（從最新到最舊）
    log_html = ''
    for j, entry in enumerate(reversed(log)):
        round_num = current_round - j
        log_html += f'<h4>Round {round_num}</h4>'
        log_html += f'<blockquote><pre>{html.escape(entry)}</pre></blockquote>'

    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>骰子遊戲</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; }}
    pre {{ background: #f5f5f5; padding: 10px; border-radius: 6px; }}
    button, input[type=submit] {{
      padding: 8px 20px; font-size: 15px; cursor: pointer;
      margin-right: 8px; border-radius: 4px; border: 1px solid #aaa;
    }}
    input[type=submit] {{
      background: #2E75B6; color: white; border: none;
    }}
  </style>
</head>
<body>
  <h3>Result</h3>
  <hr>
  <h3>Round {current_round}</h3>
  <pre>{html.escape(current_txt)}</pre>

  <h3>Options</h3>
  <form action="/play" method="post">
    <a href="/"><button type="button">Replay</button></a>
    <input type="submit" name="step" value="Throw Again">
  </form>
  <hr>

  <h3>Log</h3>
  {log_html}
</body>
</html>
"""


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

# coding=utf-8
"""
名字對戰遊戲 - Flask / Python 3 版本
原版：webapp2 + Python 2（Google App Engine 舊版）
改寫：Flask + Python 3（適用 Cloud Run）
"""

from flask import Flask, request
from random import randint
import html

app = Flask(__name__)

# ── 首頁：輸入兩位玩家名稱 ──────────────────────────────
MAIN_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>名字對戰遊戲</title>
</head>
<body>
  <h2>名字對戰遊戲</h2>
  <form action="/fight" method="post">
    <p>Name of Fighter 1 (至少三個中文字)</p>
    <textarea name="player_1" rows="1" cols="60"></textarea>
    <p>Name of Fighter 2 (至少三個中文字)</p>
    <textarea name="player_2" rows="1" cols="60"></textarea>
    <br><br>
    <input type="submit" value="Submit">
  </form>
</body>
</html>
"""

@app.route('/')
def main_page():
    return MAIN_PAGE_HTML


# ── 對戰邏輯 ────────────────────────────────────────────
@app.route('/fight', methods=['POST'])
def fight():
    player1 = request.form.get('player_1', '')
    player2 = request.form.get('player_2', '')

    if len(player1) < 3 or len(player2) < 3:
        return '<p>請輸入至少三個中文字！<br><a href="/">返回</a></p>'

    # ── 取得每位玩家名字前三字的 Unicode 碼點 ──
    p1c1, p1c2, p1c3 = ord(player1[0]), ord(player1[1]), ord(player1[2])
    p2c1, p2c2, p2c3 = ord(player2[0]), ord(player2[1]), ord(player2[2])

    # ── 計算素質的通用函式 ──────────────────────────────
    def calc_stat(coe, base, divisor, ranges):
        """
        coe: Unicode 碼點
        base: 基準值
        divisor: 除數
        ranges: list of (low, high, value)，符合條件回傳 value
        最後一個 fallback 為 0
        """
        val = (coe - base) // divisor
        for low, high, result in ranges:
            if low == high:          # 精確相等
                if val == low:
                    return result
            elif low is None:        # val < high
                if val < high:
                    return result
            elif high is None:       # val > low
                if val > low:
                    return result
            else:
                if low < val < high:
                    return result
        return 0

    # ── VIT ─────────────────────────────────────────────
    def calc_vit(c1, c2, c3):
        coe1 = (c1 - 34081) // 100
        if coe1 == 0:           v1 = 333
        elif -20 < coe1 < 0:    v1 = 297
        elif -40 < coe1 < -20:  v1 = 188
        elif -100 < coe1 < -40: v1 = 76
        elif 0 < coe1 < 20:     v1 = 297
        elif 20 < coe1 < 40:    v1 = 188
        elif 40 < coe1 < 100:   v1 = 76
        else:                   v1 = 0

        coe2 = (c2 - 24950) // 70
        if coe2 == 0:             v2 = 333
        elif -50 < coe2 < 0:     v2 = 301
        elif -100 < coe2 < -50:  v2 = 211
        elif -200 < coe2 < -100: v2 = 96
        elif 0 < coe2 < 50:      v2 = 284
        elif 50 < coe2 < 100:    v2 = 203
        elif 100 < coe2 < 200:   v2 = 93
        else:                    v2 = 0

        coe3 = (c3 - 28304) // 40
        if coe3 == 0:             v3 = 333
        elif -50 < coe3 < 0:     v3 = 289
        elif -100 < coe3 < -50:  v3 = 205
        elif -200 < coe3 < -100: v3 = 91
        elif 0 < coe3 < 50:      v3 = 301
        elif 50 < coe3 < 100:    v3 = 193
        elif 100 < coe3 < 200:   v3 = 102
        else:                    v3 = 1
        return v1 + v2 + v3

    # ── STR ─────────────────────────────────────────────
    def calc_str(c1, c2, c3):
        coe1 = (c1 - 33081) // 100
        if coe1 == 10:          s1 = 333
        elif 10 < coe1 < 30:    s1 = 298
        elif 30 < coe1 < 50:    s1 = 188
        elif 50 < coe1 < 70:    s1 = 79
        elif 0 < coe1 < 10:     s1 = 287
        elif -20 < coe1 < 0:    s1 = 198
        elif -80 < coe1 < -20:  s1 = 77
        else:                   s1 = 0

        coe2 = (c2 - 24950) // 80
        if coe2 == 0:             s2 = 333
        elif -50 < coe2 < 0:     s2 = 304
        elif -100 < coe2 < -50:  s2 = 201
        elif -200 < coe2 < -100: s2 = 98
        elif 0 < coe2 < 50:      s2 = 274
        elif 50 < coe2 < 100:    s2 = 213
        elif 100 < coe2 < 200:   s2 = 83
        else:                    s2 = 0

        coe3 = (c3 - 29104) // 40
        if coe3 == -20:             s3 = 333
        elif -70 < coe3 < -20:     s3 = 284
        elif -120 < coe3 < -70:    s3 = 202
        elif -220 < coe3 < -120:   s3 = 94
        elif -20 < coe3 < 30:      s3 = 311
        elif 30 < coe3 < 80:       s3 = 194
        elif 80 < coe3 < 180:      s3 = 104
        else:                      s3 = 1
        return s1 + s2 + s3

    # ── INT ─────────────────────────────────────────────
    def calc_int(c1, c2, c3):
        coe1 = (c1 - 36581) // 100
        if coe1 == -25:           i1 = 333
        elif -25 < coe1 < 0:     i1 = 287
        elif 0 < coe1 < 25:      i1 = 198
        elif 25 < coe1 < 50:     i1 = 86
        elif -50 < coe1 < -25:   i1 = 287
        elif -75 < coe1 < -50:   i1 = 178
        elif -100 < coe1 < -75:  i1 = 86
        else:                    i1 = 0

        coe2 = (c2 - 24950) // 80
        if coe2 == 0:             i2 = 333
        elif -50 < coe2 < 0:     i2 = 321
        elif -100 < coe2 < -50:  i2 = 201
        elif -200 < coe2 < -100: i2 = 76
        elif 0 < coe2 < 50:      i2 = 274
        elif 50 < coe2 < 100:    i2 = 223
        elif 100 < coe2 < 200:   i2 = 73
        else:                    i2 = 0

        coe3 = (c3 - 26304) // 40
        if coe3 == 50:            i3 = 333
        elif 0 < coe3 < 50:      i3 = 287
        elif -50 < coe3 < 0:     i3 = 204
        elif -150 < coe3 < -50:  i3 = 94
        elif 50 < coe3 < 100:    i3 = 307
        elif 100 < coe3 < 150:   i3 = 196
        elif 150 < coe3 < 250:   i3 = 107
        else:                    i3 = 1
        return i1 + i2 + i3

    # ── DEX ─────────────────────────────────────────────
    def calc_dex(c1, c2, c3):
        coe1 = (c1 - 27081) // 100
        if coe1 == 70:           d1 = 333
        elif 50 < coe1 < 70:    d1 = 298
        elif 30 < coe1 < 50:    d1 = 187
        elif -30 < coe1 < 30:   d1 = 96
        elif 70 < coe1 < 90:    d1 = 292
        elif 90 < coe1 < 110:   d1 = 184
        elif 110 < coe1 < 170:  d1 = 86
        else:                   d1 = 0

        coe2 = (c2 - 24950) // 60
        if coe2 == 0:             d2 = 333
        elif -50 < coe2 < 0:     d2 = 281
        elif -100 < coe2 < -50:  d2 = 231
        elif -200 < coe2 < -100: d2 = 86
        elif 0 < coe2 < 50:      d2 = 274
        elif 50 < coe2 < 100:    d2 = 233
        elif 100 < coe2 < 200:   d2 = 73
        else:                    d2 = 0

        coe3 = (c3 - 21104) // 40
        if coe3 == 180:           d3 = 333
        elif 130 < coe3 < 180:   d3 = 290
        elif 80 < coe3 < 130:    d3 = 200
        elif -20 < coe3 < 80:    d3 = 90
        elif 180 < coe3 < 230:   d3 = 300
        elif 230 < coe3 < 280:   d3 = 190
        elif 280 < coe3 < 380:   d3 = 100
        else:                    d3 = 1
        return d1 + d2 + d3

    # ── AGI ─────────────────────────────────────────────
    def calc_agi(c1, c2, c3):
        coe1 = (c1 - 44081) // 100
        if coe1 == -100:            a1 = 333
        elif -125 < coe1 < -100:   a1 = 291
        elif -150 < coe1 < -125:   a1 = 184
        elif -175 < coe1 < -150:   a1 = 72
        elif -100 < coe1 < -75:    a1 = 290
        elif -75 < coe1 < -50:     a1 = 183
        elif -50 < coe1 < -25:     a1 = 77
        else:                      a1 = 0

        coe2 = (c2 - 24950) // 70
        if coe2 == 0:             a2 = 333
        elif -50 < coe2 < 0:     a2 = 300
        elif -100 < coe2 < -50:  a2 = 210
        elif -200 < coe2 < -100: a2 = 90
        elif 0 < coe2 < 50:      a2 = 280
        elif 50 < coe2 < 100:    a2 = 200
        elif 100 < coe2 < 200:   a2 = 90
        else:                    a2 = 0

        coe3 = (c3 - 34304) // 40
        if coe3 == -150:            a3 = 333
        elif -200 < coe3 < -150:   a3 = 289
        elif -250 < coe3 < -200:   a3 = 205
        elif -350 < coe3 < -250:   a3 = 91
        elif -150 < coe3 < -100:   a3 = 301
        elif -100 < coe3 < -50:    a3 = 193
        elif -50 < coe3 < 50:      a3 = 102
        else:                      a3 = 1
        return a1 + a2 + a3

    # ── 計算兩位玩家的所有素質 ──────────────────────────
    p1 = {
        'name': player1,
        'vit': calc_vit(p1c1, p1c2, p1c3),
        'str': calc_str(p1c1, p1c2, p1c3),
        'int': calc_int(p1c1, p1c2, p1c3),
        'dex': calc_dex(p1c1, p1c2, p1c3),
        'agi': calc_agi(p1c1, p1c2, p1c3),
    }
    p1['hp'] = p1['vit'] * 3 + p1['str'] + 1004

    p2 = {
        'name': player2,
        'vit': calc_vit(p2c1, p2c2, p2c3),
        'str': calc_str(p2c1, p2c2, p2c3),
        'int': calc_int(p2c1, p2c2, p2c3),
        'dex': calc_dex(p2c1, p2c2, p2c3),
        'agi': calc_agi(p2c1, p2c2, p2c3),
    }
    p2['hp'] = p2['vit'] * 3 + p2['str'] + 1004

    # ── 技能庫 ──────────────────────────────────────────
    SKILLS = {
        'sk01': '機車店老闆的靈魂',
        'sk02': '計概期末報告',
        'sk03': '數學系也要談戀愛',
        'sk04': '期末考穩定爆炸中',
        'sk05': '翹課俠',
        'sk06': '組織的團結力',
        'sk07': '大數學系的榮耀',
        'sk08': 'D.冠希哥的意志',
        'sk09': '進擊的宗瑞兄',
        'sk10': '撿肥皂',
        'sk11': '神諾基亞',
        'sk12': '說好的學分呢?',
        'sk13': '我的微積分期末考哪有這麼可愛',
        'sk14': '我的學分很少',
        'sk15': '沐浴乳',
        'sk16': '肝鐵人',
    }

    def use_skill(attacker, defender, skill_key):
        """執行技能，回傳戰鬥日誌文字，並直接修改 attacker/defender dict"""
        name_a = attacker['name']
        name_d = defender['name']

        if skill_key == 'sk01':
            dmg = attacker['str'] // 10 * 6
            defender['hp'] -= dmg
            return f'{name_a} 使用技能 {SKILLS[skill_key]}，大喊:"修煞車皮一定要拆坐墊，你在大聲什麼啦!" 對{name_d}造成 {dmg} 的傷害'

        elif skill_key == 'sk02':
            dmg = attacker['int'] // 10 * 6
            defender['hp'] -= dmg
            return (f'{name_a} 使用技能 {SKILLS[skill_key]}:先別管安麗了，你聽過計概期末報告嗎?\n'
                    f'{name_d}感到一股巨大壓力，對{name_d} 造成{dmg}的傷害')

        elif skill_key == 'sk03':
            dmg = (attacker['dex'] + attacker['agi']) // 10 * 3
            defender['hp'] -= dmg
            return (f'{name_a}使用技能{SKILLS[skill_key]}\n'
                    f'大一的{name_a}:我要找一個超正女朋友,\n大二的{name_a}:不要長太差就好了,\n'
                    f'大三的{name_a}:是女的就可以了,\n大四的{name_a}:驀然回首 室友就在燈火闌珊處,\n'
                    f'{name_d}菊花一緊，感到非常害怕,對{name_d}造成 {dmg}的傷害')

        elif skill_key == 'sk04':
            dmg = (1000 - attacker['int']) // 3
            defender['hp'] -= dmg
            return f'{name_a}使用技能 {SKILLS[skill_key]} 期中考成績越低造成的傷害越高\n對 {name_d} 造成 {dmg}的傷害'

        elif skill_key == 'sk05':
            dmg = attacker['agi'] // 10 * 6
            defender['hp'] -= dmg
            return f'{name_a}使用技能 {SKILLS[skill_key]}\n對 {name_d} 造成 {dmg}的傷害'

        elif skill_key == 'sk06':
            dmg = (attacker['str'] + attacker['int'] + attacker['vit'] +
                   attacker['dex'] + attacker['agi']) // 50 * 6
            defender['hp'] -= dmg
            return (f'{name_a} 使用技能 {SKILLS[skill_key]}\n'
                    f'{name_d}受到團結一心的數學系排擠非常傷心\n對{name_d}造成{dmg}的傷害')

        elif skill_key == 'sk07':
            boost = attacker['int'] * 9 // 1000 + 100
            for stat in ['hp', 'str', 'vit', 'int', 'dex', 'agi']:
                attacker[stat] = attacker[stat] * boost // 100
            pct = boost - 100
            return (f'{name_a} 使用技能 {SKILLS[skill_key]}\n'
                    f'{name_a}以身為數學系的一員為榮，受到歷代數學系榮耀的祝福\n'
                    f'所有能力提升百分之{pct}\n'
                    f'HP提升為{attacker["hp"]} STR提升為{attacker["str"]} VIT提升為{attacker["vit"]}')

        elif skill_key == 'sk08':
            dmg = attacker['vit'] // 10 * 6
            defender['hp'] -= dmg
            return (f'{name_a} 使用技能 {SKILLS[skill_key]}\n'
                    f'大喊:想要{name_d}的裸照嗎，自己去找吧!我把所有裸照都藏在送修的筆電裡了，\n'
                    f'於是數學系開啟了大裸照的時代\n對{name_d}造成{dmg}的傷害')

        elif skill_key == 'sk09':
            dmg = attacker['dex'] // 10 * 6
            defender['hp'] -= dmg
            return (f'{name_a} 使用技能 {SKILLS[skill_key]}\n'
                    f'借給{name_d} 47.5G的宗瑞兄全集，那一天{name_d}終於回想起了hinet小天使守門員的恐怖，\n'
                    f'還有無法下載迷片的屈辱\n隔天{name_d}右手痠痛，兩眼疲憊，雙腿無力\n對{name_d}造成{dmg}的傷害')

        elif skill_key == 'sk10':
            dmg = defender['agi'] // 10 * 3
            attacker['hp'] -= dmg
            attacker['str'] = attacker['str'] * 120 // 100
            attacker['dex'] = attacker['dex'] * 120 // 100
            return (f'{name_a}使用技能{SKILLS[skill_key]}\n'
                    f'失去了一些身為健康男人的重要東西，覺醒了撿肥皂的興趣\n'
                    f'{name_a}受到毀滅性的撕裂傷 造成{dmg}的傷害，但非常快樂\n'
                    f'STR提升為{attacker["str"]} DEX提升為{attacker["dex"]}')

        elif skill_key == 'sk11':
            dmg = attacker['str'] + attacker['dex']
            attacker['hp'] -= dmg
            defender['hp'] -= dmg
            return (f'{name_a}使用技能{SKILLS[skill_key]}\n'
                    f'一支諾基亞手機掉在系館地上，天崩地裂，\n'
                    f'於是成大數學系從此消失在地圖上了，對所有人造成 {dmg} 的傷害')

        elif skill_key == 'sk12':
            dmg = 1000 - defender['int']
            defender['hp'] -= dmg
            return (f'{name_a} 使用技能 {SKILLS[skill_key]}\n'
                    f'時間過了，走了，學分面臨選擇，期中考，爆了，我哭了，\n'
                    f'{name_d}慘遭二一 對{name_d}造成{dmg}的傷害')

        elif skill_key == 'sk13':
            dmg = defender['hp'] // 10 + (1000 - defender['int']) // 2
            defender['hp'] -= dmg
            return (f'{name_a} 使用技能{SKILLS[skill_key]}\n'
                    f'微積分期末考；你不要誤會喔! 人家才不是為了你把題目變簡單\n'
                    f'{name_d}微積分還是被當了，對{name_d}造成 {dmg} 的傷害')

        elif skill_key == 'sk14':
            dmg = 2000 - defender['int'] - defender['agi']
            defender['hp'] -= dmg
            return (f'{name_a} 使用技能{SKILLS[skill_key]}\n'
                    f'{name_d} 長相奇葩，沒有學分願意跟{name_d}在一起\n'
                    f'對{name_d}造成{dmg}的傷害')

        elif skill_key == 'sk15':
            attacker['hp'] += 300
            attacker['str'] += 100
            return (f'{name_a} 使用技能{SKILLS[skill_key]}\n'
                    f'召喚沐浴乳，{name_a}終於不用再冒著生命危險去撿肥皂了\n'
                    f'HP提升為{attacker["hp"]} STR提升為{attacker["str"]}')

        elif skill_key == 'sk16':
            attacker['hp'] = attacker['hp'] // 2
            for stat in ['str', 'vit', 'int', 'dex', 'agi']:
                attacker[stat] = attacker[stat] * 3 // 2
            return (f'{name_a}使用技能{SKILLS[skill_key]}\n'
                    f'精彩社交+書卷獎=你的肝已經無人可擋\n'
                    f'HP降低百分之五十，其他能力全部提升百分之五十')

        return ''

    # ── 技能分配 ─────────────────────────────────────────
    SKILL_MAP = {0: 'sk01', 1: 'sk08', 2: 'sk11', 3: 'sk16'}

    def assign_skills(c1, c2, c3):
        sk1_key = f'sk{str((c1 % 8) + 1).zfill(2)}'
        sk2_key = ['sk04', 'sk09', 'sk12', 'sk14'][(c2 % 4)]
        sk3_key = ['sk03', 'sk05', 'sk10', 'sk15'][(c1 + c3) % 4]
        sk4_key = ['sk02', 'sk06', 'sk07', 'sk16'][(c1 + c2 + c3) % 4]
        return [sk1_key, sk2_key, sk3_key, sk4_key]

    p1_skills = assign_skills(p1c1, p1c2, p1c3)
    p2_skills = assign_skills(p2c1, p2c2, p2c3)

    # ── 戰鬥 ─────────────────────────────────────────────
    txt_HP = '{0}的HP剩下{1}'
    txt_death = '{0}的HP歸零'
    fight_log = []

    # 初始狀態
    init_log = (
        f"{p1['name']}的能力值\n HP {p1['hp']}\n VIT {p1['vit']}\n STR {p1['str']}\n"
        f" INT {p1['int']}\n DEX {p1['dex']}\n AGI {p1['agi']}\n"
        f"{p1['name']}獲得技能 {', '.join(SKILLS[s] for s in p1_skills)}\n\n"
        f"-------------------------------\n"
        f"{p2['name']}的能力值\n HP {p2['hp']}\n VIT {p2['vit']}\n STR {p2['str']}\n"
        f" INT {p2['int']}\n DEX {p2['dex']}\n AGI {p2['agi']}\n"
        f"{p2['name']}獲得技能 {', '.join(SKILLS[s] for s in p2_skills)}\n"
    )
    fight_log.append(init_log)

    MAX_ROUNDS = 200   # 防止無限迴圈
    for _ in range(MAX_ROUNDS):
        round_log = '-------------------------------\n'

        # player1 出招
        sk = p1_skills[randint(0, 3)]
        round_log += use_skill(p1, p2, sk) + '\n'
        if p1['hp'] <= 0:
            round_log += f'恭喜{p2["name"]}獲得勝利'
            fight_log.append(round_log)
            break
        if p2['hp'] <= 0:
            round_log += f'恭喜{p1["name"]}獲得勝利'
            fight_log.append(round_log)
            break
        round_log += txt_HP.format(p2['name'], p2['hp']) + '\n'

        # player2 出招
        sk = p2_skills[randint(0, 3)]
        round_log += use_skill(p2, p1, sk) + '\n'
        if p1['hp'] <= 0:
            round_log += f'恭喜{p2["name"]}獲得勝利'
            fight_log.append(round_log)
            break
        if p2['hp'] <= 0:
            round_log += f'恭喜{p1["name"]}獲得勝利'
            fight_log.append(round_log)
            break
        round_log += txt_HP.format(p1['name'], p1['hp']) + '\n'

        fight_log.append(round_log)
    else:
        fight_log.append(f'超過{MAX_ROUNDS}回合，平手！')

    # ── 產生 HTML 結果頁 ──────────────────────────────────
    out = ['<html><head><meta charset="utf-8"><title>對戰結果</title></head><body>']
    out.append('<h2>對戰結果</h2>')
    out.append('<h3>Initial Stat:</h3>')
    out.append(f'<blockquote><pre>{html.escape(fight_log[0])}</pre></blockquote>')

    for i, log in enumerate(fight_log[1:], start=1):
        out.append(f'<b>Round {i}:</b>')
        out.append(f'<blockquote><pre>{html.escape(log)}</pre></blockquote>')

    out.append('<br><a href="/">再玩一次</a>')
    out.append('</body></html>')
    return '\n'.join(out)


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

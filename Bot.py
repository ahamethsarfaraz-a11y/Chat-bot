import requests
import random
import time
import threading
import json
import os
import sqlite3
import io
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

TOKEN = ""
URL = "https://api.telegram.org/bot" + TOKEN + "/"
BOT_USERNAME = "Cricketrivalrybot"

BANNER_FILE_ID = "AgACAgUAAxkBAAFKrxlqFWi9Bkqpwj8hpsART6hNvQGQFAACARBrGwrLsVSnHwn2NwABy4ABAAMCAAN4AAM7BA"

games = {}
player_game = {}

DB_FILE = "cricket.db"

WIN_STICKER = "CAACAgUAAxkBAAFKrPJqFUaZiw9y209_lT3rxzWl2JkMxAACbxcAAsH7CVdefzyODEIXXDsE"
WIN_STICKER2 = "CAACAgUAAxkBAAFKrCVqFT8eqpF1zn9qITLD0zfkMlyhIwACYSAAAlDNqFRrPW9iJlH0yTsE"
START_STICKER = "CAACAgUAAxkBAAFJ7CRqCoG6I7i5rz8EqcedhKAfVmpnmgAC5RwAAmpVWFRVEf2PcqTE5jsE"
FOUR_STICKER = "CAACAgUAAxkBAAFJ8nFqCtp9ijnURSGhO4xdj9BK0TaW0QACrjIAAteWWVQpZLt5N1YpoTsE"
ONE_RUN_STICKER = "CAACAgUAAxkBAAFKBFBqC-BTTmHwDwVqDZo8OpBqVlSqJAACYRwAAkiOYFTGJHOAVH5UTDsE"
TWO_RUN_STICKER = "CAACAgUAAxkBAAFJ8sdqCtzJ5c-9wpdlTU4abddp9SvZFgACcB4AArHPWFRuZA6UEYFb5zsE"
RUN_STICKER = "CAACAgUAAxkBAAFJ24JqCZwnmFQybnv119mUbkIwtGYoIwACox0AAiIdUVSdDUdMI13ydjsE"
FIVE_STICKER = "CAACAgUAAxkBAAFJ261qCZyaLxLrbs60Zz8NaSk88gtdGwACASIAAuqbSFQ4-YD0I0u9CzsE"
WIN_RUN_STICKER = "CAACAgUAAxkBAAFJ8qBqCtw3dXg0t-6kPdX3hroaJPoUoQAC0h4AAiT1WFT9wU26nWrUrDsE"
BATTER_READY_STICKER = "CAACAgUAAxkBAAFJ3JZqCaIlwHVEW4wKXIVLzaYxuKeeRwACqR4AAs-zSVRSmyKMPkKyezsE"
HUNDRED_STICKER = "CAACAgUAAxkBAAFJ3JFqCaG0m0UgGVjQvS3ByabJjjldAgACPB4AAhTXUFQOCm4-VfErETsE"
INNINGS_STICKER = "CAACAgUAAxkBAAFJ3INqCaFBziCz5qKw479_cQVm1CPkPAAC8iIAAlmHUVQ3rLTj-bPnsTsE"
SIX_STICKER = "CAACAgUAAxkBAAFJ3GZqCaB8-4daa9-5WRYPEr-epHWPWwACah4AAsUrUFSbtBvXF2mATjsE"
FIFTY_STICKER = "CAACAgUAAxkBAAFJ3FFqCaAbd-NnfYo8q3QlkFRfEBMT6wACLSAAAizwSFTCb-q2_WzDKTsE"
WICKET_STICKER = "CAACAgUAAxkBAAFKrfhqFVXDrDuA-2zwu1SmQ5HFH-ezmwACbxUAAlAu0VRwJqSgOqReCDsE"
NO_BALL_STICKER1 = "CAACAgUAAxkBAAFKA_BqC9kxe3K_HNgR2uJm3R8fPqX4uQACZBsAAiHZYVSPXzFMATDYfDsE"
NO_BALL_STICKER2 = "CAACAgUAAxkBAAFKA8VqC9VA9H7_MJIPDvZm1nStyTbfcgACYR4AAhuxWFRK5AucAmjxYzsE"
FREE_HIT_STICKER = "CAACAgUAAxkBAAFKBC5qC91CviBReix9xE2K-adTaRylvQACLx8AAnuWYVQO-YGFO1gVCTsE"
TIMEOUT_STICKER = "CAACAgUAAxkBAAFKAAE2aguNY5pF6gqG9P0HAf7x0sm0FzsAAsYeAAKR7WBU5dzYyr7V7B07BA"
ZERO_STICKER = "CAACAgUAAxkBAAFKTEhqD7rg6nkIVg9kR9FXiSvUAAG27O0AAoscAAJRUXlUl9b003x-cJw7BA"

COMMENTARY_SIX = ["What a hit! SIX! 🔥","Smashed over the boundary! SIX!","Out of the stadium! Enormous SIX! 🏟️","Huge hit! Crowd goes wild! SIX!"]
COMMENTARY_FOUR = ["Found the gap! FOUR! ✨","Cracking shot to the rope! FOUR!","Driven through covers — FOUR!","Raced to the boundary! FOUR!"]
COMMENTARY_THREE = ["Good running! 3 runs!","Mis-field! 3 runs!","Came back for the third! 3!"]
COMMENTARY_TWO = ["Easy 2 runs!","Quick between wickets — 2!","Found the gap! 2 runs!"]
COMMENTARY_ONE = ["Single taken! 1 run.","Nudged to leg — 1.","Sensible single!"]
COMMENTARY_FIVE = ["Five runs! Rare overthrow!","Five! Excellent running!"]
COMMENTARY_WICKET = ["BOWLED! Stumps shattered! 💥","CAUGHT! Great catch! 🤲","OUT! Perfect delivery!","DISMISSED! Great bowling! 🎯"]

# ================================================================
# DATABASE
# ================================================================

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS players (
        uid INTEGER PRIMARY KEY,
        name TEXT,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        runs INTEGER DEFAULT 0,
        balls_faced INTEGER DEFAULT 0,
        balls_bowled INTEGER DEFAULT 0,
        runs_conceded INTEGER DEFAULT 0,
        highest INTEGER DEFAULT 0,
        highest_balls INTEGER DEFAULT 0,
        games INTEGER DEFAULT 0,
        sixes INTEGER DEFAULT 0,
        fours INTEGER DEFAULT 0,
        centuries INTEGER DEFAULT 0,
        fifties INTEGER DEFAULT 0,
        ducks INTEGER DEFAULT 0,
        wickets INTEGER DEFAULT 0,
        hat_tricks INTEGER DEFAULT 0,
        man_of_match INTEGER DEFAULT 0,
        no_balls INTEGER DEFAULT 0,
        free_hits INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS group_stats (
        gcid INTEGER,
        uid INTEGER,
        name TEXT,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        runs INTEGER DEFAULT 0,
        highest INTEGER DEFAULT 0,
        games INTEGER DEFAULT 0,
        PRIMARY KEY (gcid, uid)
    )''')
    conn.commit()
    conn.close()

def init_player(uid, name):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO players (uid, name) VALUES (?, ?)', (uid, name))
    c.execute('UPDATE players SET name=? WHERE uid=?', (name, uid))
    conn.commit()
    conn.close()

def upd(uid, name, stat, val=1):
    try:
        init_player(uid, name)
        conn = get_db()
        c = conn.cursor()
        c.execute(f'UPDATE players SET {stat} = {stat} + ? WHERE uid = ?', (val, uid))
        conn.commit()
        conn.close()
    except Exception as e:
        print("upd error:", e)

def upd_glb(gcid, uid, name, runs, won):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO group_stats (gcid, uid, name) VALUES (?, ?, ?)', (gcid, uid, name))
        c.execute('''UPDATE group_stats SET
            name=?, runs=runs+?, games=games+1,
            wins=wins+?, losses=losses+?,
            highest=MAX(highest,?)
            WHERE gcid=? AND uid=?''',
            (name, runs, 1 if won else 0, 0 if won else 1, runs, gcid, uid))
        conn.commit()
        conn.close()
    except Exception as e:
        print("upd_glb error:", e)

def get_player(uid):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM players WHERE uid=?', (uid,))
    p = c.fetchone()
    conn.close()
    return p

def lb_text():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM players ORDER BY wins DESC, runs DESC LIMIT 10')
    players = c.fetchall()
    conn.close()
    if not players: return "No games yet!"
    emojis = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    txt = "🏆 GLOBAL LEADERBOARD\n━━━━━━━━━━━━━━━━\n"
    for i, p in enumerate(players):
        txt += emojis[i]+" "+p["name"]+"\n   🏏"+str(p["runs"])+" 🏆"+str(p["wins"])+" 🎯"+str(p["highest"])+"\n"
    return txt+"━━━━━━━━━━━━━━━━"

def glb_text(gcid):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM group_stats WHERE gcid=? ORDER BY wins DESC, runs DESC LIMIT 10', (gcid,))
    players = c.fetchall()
    conn.close()
    if not players: return "No games in this group yet!"
    emojis = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    txt = "🏆 GROUP LEADERBOARD\n━━━━━━━━━━━━━━━━\n"
    for i, p in enumerate(players):
        txt += emojis[i]+" "+p["name"]+"\n   🏏"+str(p["runs"])+" 🏆"+str(p["wins"])+" 🎯"+str(p["highest"])+"\n"
    return txt+"━━━━━━━━━━━━━━━━"

def mystats_text(uid, name):
    p = get_player(uid)
    if not p: return "No stats yet! Play first."
    balls = p["balls_faced"]
    sr = round(p["runs"]/balls*100, 2) if balls > 0 else 0
    bowled = p["balls_bowled"]
    eco = round(p["runs_conceded"]/(bowled/6), 2) if bowled > 0 else 0
    return ("🏏 Stats: "+p["name"]+"\n📅 "+datetime.now().strftime("%Y-%m-%d")+"\n⋄◇◇◇◈\n\n"
        "🏆 Highest: "+str(p["highest"])+"("+str(p["highest_balls"])+"b)\n"
        "📊 Runs: "+str(p["runs"])+"("+str(p["games"])+"g)\n"
        "💥 Wkts: "+str(p["wickets"])+"\n"
        "🔥 6s: "+str(p["sixes"])+"\n"
        "✨ 4s: "+str(p["fours"])+"\n"
        "🏅 100s: "+str(p["centuries"])+"\n"
        "⭐ 50s: "+str(p["fifties"])+"\n"
        "🦆 Ducks: "+str(p["ducks"])+"\n"
        "🎩 HT: "+str(p["hat_tricks"])+"\n"
        "⚡ SR: "+str(sr)+"\n"
        "🎯 Eco: "+str(eco)+"\n⋄◇◇◇◈\n\n"
        "🥇 MoM: "+str(p["man_of_match"])+"\n"
        "🏆 W: "+str(p["wins"])+" 😔 L: "+str(p["losses"]))

# ================================================================
# IMAGE GENERATION
# ================================================================

def get_user_photo(uid):
    """Download user profile photo, return PIL Image or None"""
    try:
        r = requests.get(URL+"getUserProfilePhotos", params={"user_id": uid, "limit": 1}, timeout=10).json()
        photos = r.get("result", {}).get("photos", [])
        if not photos: return None
        file_id = photos[0][-1]["file_id"]
        fr = requests.get(URL+"getFile", params={"file_id": file_id}, timeout=10).json()
        fpath = fr["result"]["file_path"]
        img_url = f"https://api.telegram.org/file/bot{TOKEN}/{fpath}"
        img_data = requests.get(img_url, timeout=10).content
        return Image.open(io.BytesIO(img_data)).convert("RGBA")
    except Exception as e:
        print("get_user_photo error:", e)
        return None

def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=2):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)

def make_circle_img(img, size):
    img = img.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([0, 0, size, size], fill=255)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(img, (0, 0), mask)
    return result

def get_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def generate_mystats_image(uid, name):
    """Generate black/gold stats card with user DP"""
    p = get_player(uid)
    W, H = 700, 500
    img = Image.new("RGBA", (W, H), (10, 10, 10, 255))
    draw = ImageDraw.Draw(img)

    # Gold border
    draw.rounded_rectangle([4, 4, W-4, H-4], radius=20, outline=(212, 175, 55), width=3)

    # Header bar
    draw.rounded_rectangle([4, 4, W-4, 80], radius=20, fill=(30, 30, 30), outline=(212, 175, 55), width=2)

    # User DP circle
    dp = get_user_photo(uid)
    dp_size = 70
    dp_x, dp_y = 20, 8
    if dp:
        dp_circle = make_circle_img(dp, dp_size)
        img.paste(dp_circle, (dp_x, dp_y), dp_circle)
    else:
        draw.ellipse([dp_x, dp_y, dp_x+dp_size, dp_y+dp_size], fill=(50, 50, 50), outline=(212, 175, 55), width=2)
        draw.text((dp_x+18, dp_y+18), "🏏", font=get_font(30), fill=(212, 175, 55))

    # Gold circle border around DP
    draw.ellipse([dp_x-2, dp_y-2, dp_x+dp_size+2, dp_y+dp_size+2], outline=(212, 175, 55), width=2)

    # Name
    draw.text((105, 15), name, font=get_font(26, bold=True), fill=(212, 175, 55))
    draw.text((105, 48), "🏏 Cricket Rivalry Stats", font=get_font(16), fill=(180, 180, 180))

    if not p:
        draw.text((W//2-80, H//2), "No stats yet!", font=get_font(24, bold=True), fill=(212, 175, 55))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf

    balls = p["balls_faced"]
    sr = round(p["runs"]/balls*100, 2) if balls > 0 else 0
    bowled = p["balls_bowled"]
    eco = round(p["runs_conceded"]/(bowled/6), 2) if bowled > 0 else 0

    # Stats grid
    stats = [
        ("RUNS", str(p["runs"]), "GAMES", str(p["games"])),
        ("HIGHEST", str(p["highest"])+"("+str(p["highest_balls"])+"b)", "SR", str(sr)),
        ("SIXES", str(p["sixes"]), "FOURS", str(p["fours"])),
        ("100s", str(p["centuries"]), "50s", str(p["fifties"])),
        ("WICKETS", str(p["wickets"]), "ECO", str(eco)),
        ("DUCKS", str(p["ducks"]), "MoM", str(p["man_of_match"])),
        ("WINS", str(p["wins"]), "LOSSES", str(p["losses"])),
    ]

    start_y = 100
    for i, (k1, v1, k2, v2) in enumerate(stats):
        y = start_y + i * 54
        # Left card
        draw_rounded_rect(draw, [20, y, 330, y+46], 10, fill=(25, 25, 25), outline=(212, 175, 55), width=1)
        draw.text((30, y+4), k1, font=get_font(13), fill=(180, 180, 180))
        draw.text((30, y+22), v1, font=get_font(18, bold=True), fill=(212, 175, 55))
        # Right card
        draw_rounded_rect(draw, [360, y, 670, y+46], 10, fill=(25, 25, 25), outline=(212, 175, 55), width=1)
        draw.text((370, y+4), k2, font=get_font(13), fill=(180, 180, 180))
        draw.text((370, y+22), v2, font=get_font(18, bold=True), fill=(212, 175, 55))

    # Bottom bar
    draw.rounded_rectangle([4, H-36, W-4, H-4], radius=10, fill=(30, 30, 30))
    draw.text((W//2-80, H-28), "CRICKET RIVALRY BOT", font=get_font(14, bold=True), fill=(212, 175, 55))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def generate_mom_image(batter_name, batter_uid, runs, balls_f, fours, sixes,
                        bowler_name, b_runs, b_balls, b_wickets, winner_name):
    """Generate Man of Match image after game ends - Black/Gold theme"""
    W, H = 700, 520
    img = Image.new("RGBA", (W, H), (10, 10, 10, 255))
    draw = ImageDraw.Draw(img)

    # Gold outer border
    draw.rounded_rectangle([3, 3, W-3, H-3], radius=22, outline=(212, 175, 55), width=4)

    # Header
    draw.rounded_rectangle([3, 3, W-3, 85], radius=22, fill=(20, 20, 20), outline=(212, 175, 55), width=2)
    draw.text((W//2-120, 10), "🏆 MATCH RESULT 🏆", font=get_font(28, bold=True), fill=(212, 175, 55))
    draw.text((W//2-90, 50), "Winner: "+winner_name, font=get_font(20), fill=(255, 255, 255))

    # MOM Section
    draw.text((W//2-100, 100), "🎖️ MAN OF THE MATCH", font=get_font(22, bold=True), fill=(212, 175, 55))
    draw.line([(40, 130), (W-40, 130)], fill=(212, 175, 55), width=2)

    # Batter DP
    dp = get_user_photo(batter_uid)
    dp_size = 90
    dp_x, dp_y = W//2 - dp_size//2, 140
    if dp:
        dp_circle = make_circle_img(dp, dp_size)
        img.paste(dp_circle, (dp_x, dp_y), dp_circle)
    else:
        draw.ellipse([dp_x, dp_y, dp_x+dp_size, dp_y+dp_size], fill=(40, 40, 40), outline=(212, 175, 55), width=2)
    draw.ellipse([dp_x-3, dp_y-3, dp_x+dp_size+3, dp_y+dp_size+3], outline=(212, 175, 55), width=3)

    # Batter name
    draw.text((W//2-len(batter_name)*7, dp_y+dp_size+8), batter_name, font=get_font(22, bold=True), fill=(212, 175, 55))

    # Batter stats row
    sr = round(runs/balls_f*100, 1) if balls_f > 0 else 0
    bat_stats = [("RUNS", str(runs)), ("BALLS", str(balls_f)), ("4s", str(fours)), ("6s", str(sixes)), ("SR", str(sr))]
    bx = 30
    for label, val in bat_stats:
        draw_rounded_rect(draw, [bx, 290, bx+118, 350], 10, fill=(25,25,25), outline=(212,175,55), width=1)
        draw.text((bx+8, 295), label, font=get_font(13), fill=(180,180,180))
        draw.text((bx+8, 316), val, font=get_font(18, bold=True), fill=(212,175,55))
        bx += 128

    # Divider
    draw.line([(40, 365), (W-40, 365)], fill=(60, 60, 60), width=1)
    draw.text((30, 375), "⚾ BEST BOWLER", font=get_font(18, bold=True), fill=(180, 180, 180))

    # Bowler stats
    eco = round(b_runs/(b_balls/6), 2) if b_balls > 0 else 0
    bowl_stats = [("BOWLER", bowler_name[:10]), ("OVERS", str(b_balls//6)+"."+str(b_balls%6)),
                  ("RUNS", str(b_runs)), ("WKTS", str(b_wickets)), ("ECO", str(eco))]
    bx = 30
    for label, val in bowl_stats:
        draw_rounded_rect(draw, [bx, 405, bx+118, 465], 10, fill=(25,25,25), outline=(80,80,80), width=1)
        draw.text((bx+8, 410), label, font=get_font(12), fill=(150,150,150))
        draw.text((bx+8, 430), val, font=get_font(16, bold=True), fill=(200,200,200))
        bx += 128

    # Footer
    draw.rounded_rectangle([3, H-36, W-3, H-3], radius=10, fill=(20,20,20))
    draw.text((W//2-80, H-28), "CRICKET RIVALRY BOT", font=get_font(14, bold=True), fill=(212,175,55))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# ================================================================
# TELEGRAM HELPERS
# ================================================================

def parse_num(text):
    try:
        t = str(text).strip()
        if len(t)==1 and t in "0123456": return int(t)
        return None
    except: return None

def get_req(method, params={}):
    try:
        timeout = 35 if method=="getUpdates" else 10
        return requests.get(URL+method, params=params, timeout=timeout).json()
    except requests.exceptions.Timeout:
        if method!="getUpdates": print("Timeout:",method)
        return {}
    except Exception as e:
        if method!="getUpdates": print("API error:",method,e)
        return {}

def send(cid, text, markup=None):
    try:
        p = {"chat_id":cid,"text":str(text)[:4096]}
        if markup: p["reply_markup"]=json.dumps(markup)
        get_req("sendMessage",p)
    except Exception as e: print("send error:",e)

def send_html(cid, text, markup=None):
    try:
        p = {"chat_id":cid,"text":str(text)[:4096],"parse_mode":"HTML"}
        if markup: p["reply_markup"]=json.dumps(markup)
        r = get_req("sendMessage",p)
        if not r.get("ok"): send(cid, text, markup)
    except:
        try: send(cid,text,markup)
        except: pass

def send_md(cid, text, markup=None):
    send_html(cid, text, markup)

def mention(uid, name):
    try:
        safe = str(name).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        return '<a href="tg://user?id='+str(uid)+'">'+safe+'</a>'
    except: return str(name)

def bold(text):
    return "<b>"+str(text)+"</b>"

def send_sticker(cid, fid):
    try: get_req("sendSticker",{"chat_id":cid,"sticker":fid})
    except Exception as e: print("Sticker skip:",type(e).__name__)

def answer(qid, text="", alert=False):
    try: get_req("answerCallbackQuery",{"callback_query_id":qid,"text":text,"show_alert":alert})
    except: pass

def remove_buttons(cid, mid):
    try: get_req("editMessageReplyMarkup",{"chat_id":cid,"message_id":mid,"reply_markup":json.dumps({})})
    except: pass

def is_admin(cid, uid):
    try:
        for a in get_req("getChatAdministrators",{"chat_id":cid}).get("result",[]):
            if a["user"]["id"]==uid: return True
    except: pass
    return False

def is_host(g, uid):
    return uid == g.get("host") or uid == g.get("creator")

def is_host_or_admin(g, cid, uid):
    return is_host(g, uid) or is_admin(cid, uid)

def send_photo_buffer(cid, buf, caption=""):
    try:
        buf.seek(0)
        requests.post(URL+"sendPhoto",
            data={"chat_id": cid, "caption": caption},
            files={"photo": ("image.png", buf, "image/png")},
            timeout=20)
    except Exception as e: print("send_photo_buffer error:", e)

def send_banner(cid):
    try:
        requests.post(URL+"sendPhoto",
            data={"chat_id": cid, "photo": BANNER_FILE_ID},
            timeout=10)
    except Exception as e: print("send_banner error:", e)

def bowling_btn():
    return {"inline_keyboard":[[{"text":"⚾ Go to Bowl (DM)","url":"https://t.me/Cricketrivalrybot?start=bowl"}]]}

def back_kb(gcid):
    try:
        c = str(gcid)
        if c.startswith("-100"): c=c[4:]
        elif c.startswith("-"): c=c[1:]
        return {"inline_keyboard":[[{"text":"🏏 Back to Group","url":"https://t.me/c/"+c+"/99999999"}]]}
    except: return None

def join_team_kb():
    return {"inline_keyboard":[
        [{"text":"🔵 Join Team A","callback_data":"join_team_a"}],
        [{"text":"🔴 Join Team B","callback_data":"join_team_b"}]
    ]}

def toss_kb(): return {"inline_keyboard":[[{"text":"🪙 Heads","callback_data":"toss_heads"},{"text":"🪙 Tails","callback_data":"toss_tails"}]]}
def bat_bowl_kb(): return {"inline_keyboard":[[{"text":"🏏 Bat","callback_data":"choice_bat"},{"text":"⚾ Bowl","callback_data":"choice_bowl"}]]}
def follow_on_kb(): return {"inline_keyboard":[[{"text":"✅ Follow-On","callback_data":"followon_yes"},{"text":"❌ Skip","callback_data":"followon_no"}]]}
def host_kb(): return {"inline_keyboard":[[{"text":"🎮 I'm the Host!","callback_data":"set_host"}]]}
def endgame_confirm_kb(): return {"inline_keyboard":[[{"text":"✅ Yes, End Game","callback_data":"endgame_confirm"},{"text":"❌ Cancel","callback_data":"endgame_cancel"}]]}

def mode_kb():
    return {"inline_keyboard":[
        [{"text":"⚔️ 1v1 Rivalry","callback_data":"mode_1v1"}],
        [{"text":"🏆 Solo Tournament","callback_data":"mode_solo"}],
        [{"text":"👥 Team Match","callback_data":"mode_team"}],
        [{"text":"🏟️ Test Match","callback_data":"mode_test"}]
    ]}

def over_kb():
    return {"inline_keyboard":[
        [{"text":str(n)+"Ov","callback_data":"over_"+str(n)} for n in [1,2,3]],
        [{"text":str(n)+"Ov","callback_data":"over_"+str(n)} for n in [4,5,6]],
        [{"text":"10 Overs","callback_data":"over_10"},{"text":"20 Overs","callback_data":"over_20"}],
        [{"text":"♾️ Infinity","callback_data":"over_inf"}]
    ]}

def over_kb_team():
    return {"inline_keyboard":[
        [{"text":str(n)+"Ov","callback_data":"over_"+str(n)} for n in [3,4,5]],
        [{"text":str(n)+"Ov","callback_data":"over_"+str(n)} for n in [6,7,8]],
        [{"text":"10 Overs","callback_data":"over_10"},{"text":"15 Overs","callback_data":"over_15"}],
        [{"text":"20 Overs","callback_data":"over_20"}]
    ]}

def wicket_kb():
    return {"inline_keyboard":[
        [{"text":str(n)+" Wkt","callback_data":"wkt_"+str(n)} for n in [1,2,3]],
        [{"text":str(n)+" Wkts","callback_data":"wkt_"+str(n)} for n in [4,5,6]]
    ]}

def test_type_kb():
    return {"inline_keyboard":[
        [{"text":"⚔️ 1v1 Test","callback_data":"test_1v1"}],
        [{"text":"👥 Team Test","callback_data":"test_team"}]
    ]}

def cap_a_kb(teams):
    return {"inline_keyboard":[[{"text":str(i+1)+". "+p[1],"callback_data":"cap_a_"+str(i)}] for i,p in enumerate(teams[0])]}

def cap_b_kb(teams):
    return {"inline_keyboard":[[{"text":str(i+1)+". "+p[1],"callback_data":"cap_b_"+str(i)}] for i,p in enumerate(teams[1])]}

def change_cap_a_kb(teams):
    return {"inline_keyboard":[[{"text":str(i+1)+". "+p[1],"callback_data":"chcap_a_"+str(i)}] for i,p in enumerate(teams[0])]}

def change_cap_b_kb(teams):
    return {"inline_keyboard":[[{"text":str(i+1)+". "+p[1],"callback_data":"chcap_b_"+str(i)}] for i,p in enumerate(teams[1])]}

def batter_kb(g, team_idx, for_nonstriker=False):
    dismissed = g["dismissed"][team_idx]
    striker = g.get("striker")
    non_striker = g.get("non_striker")
    rows = []
    for p in g["teams"][team_idx]:
        if p[0] in dismissed: continue
        if for_nonstriker and striker and p[0]==striker: continue
        if not for_nonstriker and non_striker and p[0]==non_striker: continue
        prefix = "ns_uid_" if for_nonstriker else "bat_uid_"
        rows.append([{"text":p[1],"callback_data":prefix+str(p[0])}])
    return {"inline_keyboard":rows} if rows else None

def bowler_kb(g):
    wi = g["bowling"]
    last = g.get("last_bowler")
    team = g["teams"][wi]
    rows = []
    for p in team:
        if len(team)>1 and p[0]==last: continue
        rows.append([{"text":p[1],"callback_data":"bowl_uid_"+str(p[0])}])
    return {"inline_keyboard":rows} if rows else None

def new_game(mode, test_type=None):
    is_team = (mode=="team" or (mode=="test" and test_type=="team"))
    return {
        "mode":mode,"test_type":test_type,
        "phase":"waiting_host" if is_team else "setup_over",
        "creator":None,"host":None,"host_name":"",
        "players":[],"teams":[[],[]],"team_names":["Team A","Team B"],
        "captains":[None,None],
        "overs":None,"max_wickets":3,
        "batting":0,"bowling":1,
        "scores":[0,0],"wickets":[0,0],
        "extras":[0,0],
        "balls":0,"innings":1,
        "target":None,"bc":None,"wc":None,
        "toss_winner":None,
        "current_over_runs":0,"ball_log":[],
        "current_over_log":[],
        "free_hit":False,"infinity_overs":False,
        "striker":None,"non_striker":None,
        "current_bowler":None,"last_bowler":None,
        "over_bowler_locked":False,
        "dismissed":[[],[]],
        "bowl_miss":{},"ball_timer_token":0,
        "join_deadline":None,"join_warned":False,
        "batter_zero_count":{},"wicket_track":[],
        "innings_stats":[
            {"runs":0,"balls":0,"sixes":0,"fours":0,"singles":0,"wickets":0,"extras":0},
            {"runs":0,"balls":0,"sixes":0,"fours":0,"singles":0,"wickets":0,"extras":0}
        ],
        "player_bat_stats":{},"player_bowl_stats":{},
        "player_ball_log":{},"player_over_log":{},
        "solo_order":[],"solo_current":0,
        "solo_scores":{},"solo_balls":0,"solo_wickets":0,
        "solo_bc":None,"solo_wc":None,"solo_bowler":None,
        "solo_bowler_balls":0,"max_players":None,"infinity_players":False,
        "test_innings_num":1,
        "test_scores":[[0,0,0,0],[0,0,0,0]],
        "test_wickets":[[0,0,0,0],[0,0,0,0]],
        "test_bat_stats":[[{},{}],[{},{}]],
        "test_bowl_stats":[[{},{}],[{},{}]],
        "follow_on_offered":False,
        "waiting_striker":False,"waiting_nonstriker":False,"waiting_bowler":False,
        "last_ball_odd":False,
        "consecutive_miss":0,
        "hat_trick_track":{},
    }

def is_team_mode(g):
    return g["mode"]=="team" or (g["mode"]=="test" and g.get("test_type")=="team")

def ov_str(balls):
    b = balls if balls is not None else 0
    return str(b//6)+"."+str(b%6)

def crr_calc(runs, balls):
    if not balls or balls==0: return "0.00"
    return str(round(runs/(balls/6),2))

def rrr_calc(need, balls_left):
    if not balls_left or balls_left<=0: return "∞"
    return str(round(need/(balls_left/6),2))

def init_bat_stats(g, uid, name):
    k = str(uid)
    if k not in g["player_bat_stats"]:
        g["player_bat_stats"][k] = {"name":name,"runs":0,"balls":0,"fours":0,"sixes":0,"out":False}
    if k not in g["player_ball_log"]: g["player_ball_log"][k] = []
    if k not in g["player_over_log"]: g["player_over_log"][k] = []

def init_bowl_stats(g, uid, name):
    k = str(uid)
    if k not in g["player_bowl_stats"]:
        g["player_bowl_stats"][k] = {"name":name,"balls":0,"runs":0,"wickets":0,"overs":0}

def get_striker(g):
    bi = g["batting"]
    if not is_team_mode(g):
        return g["players"][bi] if bi<len(g["players"]) else None
    sid = g.get("striker")
    dismissed = g["dismissed"][bi]
    team = g["teams"][bi]
    if sid:
        p = next((x for x in team if x[0]==sid),None)
        if p and p[0] not in dismissed: return p
    avail = [p for p in team if p[0] not in dismissed]
    return avail[0] if avail else None

def get_nonstriker(g):
    bi = g["batting"]
    if not is_team_mode(g): return None
    nsid = g.get("non_striker")
    dismissed = g["dismissed"][bi]
    team = g["teams"][bi]
    striker = get_striker(g)
    if nsid and (not striker or nsid!=striker[0]):
        p = next((x for x in team if x[0]==nsid and x[0] not in dismissed),None)
        if p: return p
    avail = [p for p in team if p[0] not in dismissed and (not striker or p[0]!=striker[0])]
    return avail[0] if avail else None

def get_bowler(g):
    wi = g["bowling"]
    if not is_team_mode(g):
        return g["players"][wi] if wi<len(g["players"]) else None
    bid = g.get("current_bowler")
    if bid:
        p = next((x for x in g["teams"][wi] if x[0]==bid),None)
        if p: return p
    return None

def get_solo_bb(g):
    cur_uid = g["solo_order"][g["solo_current"]]
    bowl_uid = g["solo_bowler"]
    batter = next((p for p in g["players"] if p[0]==cur_uid),g["players"][0])
    bowler = next((p for p in g["players"] if p[0]==bowl_uid),g["players"][1])
    return batter,bowler

def get_next_solo_bowler(g):
    if g["solo_current"]>=len(g["solo_order"]): return None
    cur_uid = g["solo_order"][g["solo_current"]]
    last = g.get("last_bowler")
    avail = [p for p in g["players"] if p[0]!=cur_uid]
    if len(avail)>1 and last:
        nl = [p for p in avail if p[0]!=last]
        if nl: avail=nl
    return random.choice(avail) if avail else None

def is_no_ball(bp, wp):
    return (bp==1 and wp==6) or (bp==6 and wp==1)

def rotate_strike(g):
    if not is_team_mode(g): return
    s=g.get("striker"); ns=g.get("non_striker")
    if s and ns: g["striker"]=ns; g["non_striker"]=s

def max_wkts_for_team(g, team_idx):
    return max(1,len(g["teams"][team_idx])-1)

def squad_text(g, team_idx):
    team = g["teams"][team_idx]
    cap = g["captains"][team_idx]
    dismissed = g["dismissed"][team_idx]
    txt = ""
    for p in team:
        crown = " 👑" if p[0]==cap else ""
        out_mark = " ❌" if p[0] in dismissed else ""
        txt += "  • "+p[1]+crown+out_mark+"\n"
    return txt

def live_bat_line(g, uid):
    ps = g["player_bat_stats"].get(str(uid),{})
    return str(ps.get("runs",0))+"("+str(ps.get("balls",0))+"b)"

def live_bowl_line(g, uid):
    bs = g["player_bowl_stats"].get(str(uid),{})
    return ov_str(bs.get("balls",0))+" "+str(bs.get("wickets",0))+"wkt"

def fmt_rb(runs, balls): return str(runs)+"("+str(balls)+")"
def fmt_sr(runs, balls):
    if balls==0: return "0.0"
    return str(round(runs/balls*100,1))
def fmt_eco(runs, balls):
    if balls==0: return "0.0"
    return str(round(runs/(balls/6),1))

def build_team_scorecard_block(g, ti, balls_now):
    bi = g["batting"]
    tname = g["team_names"][ti]
    sc=g["scores"][ti]; wk=g["wickets"][ti]
    ext=g["extras"][ti] if ti<len(g.get("extras",[0,0])) else 0
    b=balls_now if ti==bi else 0
    lines = []
    lines.append("🏏 "+tname+": "+str(sc)+"/"+str(wk)+" ("+ov_str(b)+" ov) | Ext: "+str(ext))
    lines.append("-"*34)
    lines.append("{:<13} {:>7} {:>3} {:>3} {:>5}".format("PLAYER","R(B)","4s","6s","SR"))
    lines.append("-"*34)
    for p in g["teams"][ti]:
        k=str(p[0]); ps=g["player_bat_stats"].get(k,{})
        runs=ps.get("runs",0); pballs=ps.get("balls",0)
        fours=ps.get("fours",0); sixes=ps.get("sixes",0)
        sr=round(runs/pballs*100) if pballs>0 else 0
        is_striker=p[0]==g.get("striker"); is_ns=p[0]==g.get("non_striker")
        star="*" if is_striker else ("+" if is_ns else " ")
        if ps.get("out",False): star=" "
        nm=(p[1]+star)[:13]
        if pballs==0 and not ps.get("out",False):
            lines.append("{:<13} {:>7}".format(nm,"(DNB)"))
        else:
            rb=str(runs)+"("+str(pballs)+")"
            lines.append("{:<13} {:>7} {:>3} {:>3} {:>5}".format(nm,rb,fours,sixes,sr))
    lines.append("-"*34)
    lines.append("{:<13} {:>7} {:>3} {:>3} {:>5}".format("BOWLER","O","R","W","ECON"))
    lines.append("-"*34)
    bowl_team=1-ti; has_bowler=False
    for p in g["teams"][bowl_team]:
        k=str(p[0]); bs=g["player_bowl_stats"].get(k,{})
        if bs.get("balls",0)>0:
            has_bowler=True; b2=bs["balls"]
            eco=round(bs["runs"]/(b2/6),1) if b2>0 else 0
            nm=p[1][:13]
            lines.append("{:<13} {:>7} {:>3} {:>3} {:>5}".format(nm,ov_str(b2),bs["runs"],bs["wickets"],eco))
    if not has_bowler: lines.append("(no balls bowled yet)")
    return "\n".join(lines)

def simple_sb(g):
    bi=g["batting"]; balls=g.get("balls",0) or 0
    overs_val=g.get("overs") or 0; inf=g.get("infinity_overs",False)
    txt = "📊 SCOREBOARD\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    if g["mode"]=="solo":
        ss=sorted(g["solo_scores"].items(),key=lambda x:x[1],reverse=True)
        for uid,score in ss:
            nm=next((p[1] for p in g["players"] if p[0]==uid),"?")
            cur=" 🏏" if g["solo_current"]<len(g["solo_order"]) and uid==g["solo_order"][g["solo_current"]] else ""
            txt+=nm+": "+str(score)+cur+"\n"
    elif is_team_mode(g):
        for i in range(2):
            mark="🏏" if i==bi else "⚾"
            ext=g["extras"][i] if i<len(g.get("extras",[0,0])) else 0
            overs_disp=ov_str(balls) if i==bi else "0.0"
            txt+=mark+" "+g["team_names"][i]+": "+str(g["scores"][i])+"/"+str(g["wickets"][i])+" ("+overs_disp+" ov) | Ext: "+str(ext)+"\n"
        striker=get_striker(g); bowler=get_bowler(g)
        if striker: txt+="  🏏 "+striker[1]+": "+live_bat_line(g,striker[0])+" *\n"
        ns=get_nonstriker(g)
        if ns: txt+="  🏏 "+ns[1]+": "+live_bat_line(g,ns[0])+"\n"
        if bowler: txt+="  ⚾ "+bowler[1]+": "+live_bowl_line(g,bowler[0])+"\n"
    elif g["mode"]=="test":
        ti=g.get("test_innings_num",1)
        for i in range(2):
            mark="🏏" if i==bi else "⚾"
            parts=[str(g["test_scores"][i][j])+"/"+str(g["test_wickets"][i][j]) for j in range(ti)]
            nm=g["players"][i][1] if i<len(g["players"]) else "?"
            txt+=mark+" "+nm+": "+" & ".join(parts)+"\n"
        t0=sum(g["test_scores"][0][:ti]); t1=sum(g["test_scores"][1][:ti])
        if t0!=t1:
            leader=(g["players"][0][1] if t0>t1 else g["players"][1][1]) if len(g["players"])>=2 else "?"
            txt+="📊 "+leader+" leads by "+str(abs(t0-t1))+"\n"
    else:
        for i in range(2):
            mark="🏏" if i==bi else "⚾"
            nm=g["players"][i][1] if i<len(g["players"]) else "?"
            ps=g["player_bat_stats"].get(str(g["players"][i][0]) if i<len(g["players"]) else "0",{})
            txt+=mark+" "+nm+": "+str(g["scores"][i])+"/"+str(g["wickets"][i])
            if ps.get("balls",0)>0: txt+="  ("+str(ps.get("runs",0))+"("+str(ps.get("balls",0))+"b))"
            txt+="\n"
    txt+="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    if g.get("target") and g["mode"] not in ("test","solo"):
        need=max(0,(g["target"] or 0)-g["scores"][bi])
        if not inf and overs_val and overs_val!=999:
            left=max(0,overs_val*6-balls)
            txt+="🎯 Need: "+str(need)+" in "+str(left)+" balls\n"
            txt+="📈 RRR: "+rrr_calc(need,left)+"\n"
        else: txt+="🎯 Need: "+str(need)+"\n"
    if g["mode"]!="solo":
        txt+="📋 Inn"+str(g.get("innings",1))+" | "+ov_str(balls)
        if not inf and overs_val and overs_val!=999: txt+="/"+str(overs_val)+"ov"
    if g.get("free_hit"): txt+="\n🆓 FREE HIT NEXT BALL!"
    return txt

def build_full_scorecard(g):
    bi=g["batting"]; host_name=g.get("host_name","Host")
    balls_now=g.get("balls",0) or 0
    header="📊 <b>FULL SCORECARD</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    blocks=[]
    for ti in range(2): blocks.append(build_team_scorecard_block(g,ti,balls_now))
    body="<pre>"+("\n\n").join(blocks)+"</pre>"
    footer=""
    if g.get("target"):
        need=max(0,g["target"]-g["scores"][bi])
        overs_val=g.get("overs") or 0
        left=max(0,overs_val*6-balls_now) if overs_val and overs_val!=999 else 0
        footer+="🎯 Target: "+str(g["target"])+" | Need: "+str(need)
        if left>0: footer+=" in "+str(left)+" balls | RRR: "+rrr_calc(need,left)
        footer+="\n"
    footer+="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🎙️ Host: "+host_name
    return header+body+"\n"+footer

def build_over_scorecard(g):
    bi=g["batting"]; host_name=g.get("host_name","Host")
    balls_now=g.get("balls",0) or 0
    header="📋 <b>END OF OVER "+str(balls_now//6)+"</b>\n"
    header+="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    blocks=[]
    for ti in range(2): blocks.append(build_team_scorecard_block(g,ti,balls_now))
    body="<pre>"+("\n\n").join(blocks)+"</pre>"
    footer="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🎙️ Host: "+host_name
    return header+body+"\n"+footer

def build_innings_end_scorecard(g, inn_num):
    bi=g["batting"]; balls_now=g.get("balls",0) or 0
    host_name=g.get("host_name","Host")
    header="📋 <b>INNINGS "+str(inn_num)+" END</b>\n"
    header+="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    body=""
    if is_team_mode(g):
        body="<pre>"+build_team_scorecard_block(g,bi,balls_now)+"</pre>"
    footer="\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🎙️ Host: "+host_name
    return header+body+footer

def build_final_scorecard(g, winner_name, margin):
    host_name=g.get("host_name","Host")
    bi=g["batting"]; balls_now=g.get("balls",0) or 0
    header="🏆 <b>MATCH OVER</b> 🏆\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    header+="🥇 WINNER: "+winner_name+"\n"
    if margin: header+="👉 "+margin+"\n"
    header+="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    body=""
    if g["mode"]=="solo":
        ss=sorted(g["solo_scores"].items(),key=lambda x:x[1],reverse=True)
        emojis=["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        lines=[]
        for i,(puid,score) in enumerate(ss):
            nm=next((p[1] for p in g["players"] if p[0]==puid),"?")
            em=emojis[i] if i<len(emojis) else str(i+1)+"."
            lines.append(em+" "+nm+" → "+str(score)+" runs")
        body="<pre>"+"\n".join(lines)+"</pre>\n"
    elif not is_team_mode(g):
        lines=[]
        for i in range(2):
            nm=g["players"][i][1] if i<len(g["players"]) else "?"
            puid=g["players"][i][0] if i<len(g["players"]) else 0
            sc=g["scores"][i]; wk=g["wickets"][i]
            b=balls_now if i==bi else 0
            k=str(puid); ps=g["player_bat_stats"].get(k,{})
            runs=ps.get("runs",0); pballs=ps.get("balls",0)
            fours=ps.get("fours",0); sixes=ps.get("sixes",0)
            sr=round(runs/pballs*100) if pballs>0 else 0
            lines.append("🏏 "+nm+": "+str(sc)+"/"+str(wk)+" ("+ov_str(b)+" ov)")
            lines.append("-"*34)
            lines.append("{:<13} {:>7} {:>3} {:>3} {:>5}".format("PLAYER","R(B)","4s","6s","SR"))
            lines.append("-"*34)
            rb=str(runs)+"("+str(pballs)+")"
            lines.append("{:<13} {:>7} {:>3} {:>3} {:>5}".format(nm[:13],rb,fours,sixes,sr))
            lines.append("-"*34)
        body="<pre>"+"\n".join(lines)+"</pre>\n"
    else:
        blocks=[]
        for ti in range(2): blocks.append(build_team_scorecard_block(g,ti,balls_now))
        body="<pre>"+("\n\n").join(blocks)+"</pre>\n"
    best_bat_runs=-1; best_bat_name="?"; best_bat_uid=None; best_bat_balls=0; best_bat_fours=0; best_bat_sixes=0
    for k,ps in g["player_bat_stats"].items():
        if ps.get("runs",0)>best_bat_runs:
            best_bat_runs=ps["runs"]; best_bat_name=ps["name"]; best_bat_uid=k
            best_bat_balls=ps.get("balls",0); best_bat_fours=ps.get("fours",0); best_bat_sixes=ps.get("sixes",0)
    best_bowl_wkts=-1; best_bowl_eco=999; best_bowl_name="?"; best_bowl_runs=0; best_bowl_balls=0; best_bowl_uid=None
    for k,bs in g["player_bowl_stats"].items():
        if bs.get("balls",0)>0:
            w=bs.get("wickets",0); eco=bs["runs"]/(bs["balls"]/6) if bs["balls"]>0 else 0
            if w>best_bowl_wkts or (w==best_bowl_wkts and eco<best_bowl_eco):
                best_bowl_wkts=w; best_bowl_eco=eco; best_bowl_name=bs["name"]
                best_bowl_runs=bs.get("runs",0); best_bowl_balls=bs.get("balls",0); best_bowl_uid=k
    if best_bat_uid:
        try: upd(int(best_bat_uid),best_bat_name,"man_of_match")
        except: pass
    awards="🎖️ <b>AWARDS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    if best_bat_runs>=0:
        awards+="🏆 MoM:      "+best_bat_name+" ("+str(max(0,best_bat_runs))+" runs)\n"
        awards+="🏏 Best Bat: "+best_bat_name+" ("+str(max(0,best_bat_runs))+" runs)\n"
    if best_bowl_wkts>=0:
        awards+="⚾ Best Bowl: "+best_bowl_name+" ("+str(max(0,best_bowl_wkts))+" Wkts)\n"
    awards+="\n🎙️ Host: "+host_name
    return header+"\n"+body+awards, best_bat_uid, best_bat_name, best_bat_runs, best_bat_balls, best_bat_fours, best_bat_sixes, best_bowl_name, best_bowl_runs, best_bowl_balls, best_bowl_wkts

def check_individual_fifty(g, cid, uid, name, new_runs, old_runs):
    if old_runs<50<=new_runs:
        upd(uid,name,"fifties"); send_sticker(cid,FIFTY_STICKER)
        send(cid,"🎉 FIFTY! "+name+" scored 50 runs!")
    if old_runs<100<=new_runs:
        upd(uid,name,"centuries"); send_sticker(cid,HUNDRED_STICKER)
        send(cid,"💯 CENTURY! "+name+" 100 runs!")

def check_target_after_penalty(g, cid):
    bi=g["batting"]; wi=g["bowling"]
    if g.get("innings")==2 and g.get("target") is not None:
        if g["scores"][bi]>=g["target"]:
            wname=g["team_names"][bi] if is_team_mode(g) else (g["players"][bi][1] if bi<len(g["players"]) else "?")
            finish_game(g,cid,wname,bi,wi,"Won via penalty runs! 🎉")
            return True
    return False

def send_bowl_dm(g, gcid):
    try:
        if g["mode"]=="solo": batter,bowler=get_solo_bb(g); balls=g.get("solo_balls",0)
        else: batter=get_striker(g); bowler=get_bowler(g); balls=g.get("balls",0)
        if not batter or not bowler: return
        overs_val=g.get("overs") or 0
        total="♾️" if g.get("infinity_overs") else str(overs_val*6)
        fh="\n🆓 FREE HIT! Same number = dot NOT out!" if g.get("free_hit") else ""
        bat_line=live_bat_line(g,batter[0])
        msg=("🎯 YOUR TURN TO BOWL!\n━━━━━━━━━━━━━━━━\n"
             "🏏 Batter: "+batter[1]+"  "+bat_line+"\n"
             "🔢 Send 1-6 (NOT 0!)\n━━━━━━━━━━━━━━━━\n"
             "🎳 "+ov_str(balls)+" of "+total+fh+"\n⏱ 1 minute!")
        send(bowler[0],msg,back_kb(gcid))
    except Exception as e: print("send_bowl_dm error:",e)

def send_bowl_result(bowler_uid, gcid):
    try:
        bk=back_kb(gcid)
        if bk: send(bowler_uid,"✅ Ball Delivered! Return to group!",bk)
        else: send(bowler_uid,"✅ Ball Delivered!")
    except: pass

def next_ball_msg(g, cid):
    try:
        if g.get("waiting_striker") or g.get("waiting_nonstriker") or g.get("waiting_bowler"): return
        if g["mode"]=="solo": batter,bowler=get_solo_bb(g)
        else: batter=get_striker(g); bowler=get_bowler(g)
        if not batter or not bowler: return
        bb=bowling_btn()
        bat_line=live_bat_line(g,batter[0]); bowl_line=live_bowl_line(g,bowler[0])
        msg=(simple_sb(g)+"\n\n"
             "⚾ "+mention(bowler[0],bowler[1])+" bowl now!  ["+bowl_line+"]\n"
             "🏏 "+mention(batter[0],batter[1])+" get ready!  ["+bat_line+"]")
        send_html(cid,msg,bb)
        send_bowl_dm(g,cid)
        nt=g.get("ball_timer_token",0)+1; g["ball_timer_token"]=nt
        t=threading.Thread(target=start_timers,args=(g,cid,nt,batter,bowler))
        t.daemon=True; t.start()
    except Exception as e:
        print("next_ball_msg error:",e)
        import traceback; traceback.print_exc()

def handle_bowl_miss(g, cid, bowler):
    bi=g["batting"]; wi=g["bowling"]
    if "extras" not in g: g["extras"]=[0,0]
    if is_team_mode(g):
        g["scores"][bi]+=6; g["extras"][bi]+=6
        g["innings_stats"][bi]["runs"]+=6
        g["innings_stats"][bi]["extras"]=g["innings_stats"][bi].get("extras",0)+6
        g["balls"]=g.get("balls",0)+1; g["innings_stats"][bi]["balls"]+=1
        g["current_over_runs"]=g.get("current_over_runs",0)+6
        g["ball_log"].append("P+6"); g["current_over_log"].append("P+6")
        if g["mode"]=="test": g["test_scores"][bi][g.get("test_innings_num",1)-1]=g["scores"][bi]
        cmiss=g.get("consecutive_miss",0)+1; g["consecutive_miss"]=cmiss
        bwn=mention(bowler[0],bowler[1])
        send_html(cid,"⚠️ "+bwn+" missed!\n+6 penalty (Extras) to "+g["team_names"][bi]+"!\nScore: "+str(g["scores"][bi])+"/"+str(g["wickets"][bi])+" | Extras: "+str(g["extras"][bi]))
        if check_target_after_penalty(g,cid): return True
        if cmiss>=2:
            g["consecutive_miss"]=0; g["current_bowler"]=None; g["over_bowler_locked"]=False
            g["scores"][bi]+=6; g["extras"][bi]+=6; g["innings_stats"][bi]["runs"]+=6
            g["balls"]=g.get("balls",0)+1; g["innings_stats"][bi]["balls"]+=1
            if g["mode"]=="test": g["test_scores"][bi][g.get("test_innings_num",1)-1]=g["scores"][bi]
            send(cid,"🚨 2 consecutive misses! Changing bowler! +6 more penalty!")
            if check_target_after_penalty(g,cid): return True
            g["waiting_bowler"]=True; ask_bowler_inline(g,cid)
        else:
            g["current_bowler"]=None; g["over_bowler_locked"]=False
            g["waiting_bowler"]=True; ask_bowler_inline(g,cid)
        return False
    else:
        cmiss=g.get("consecutive_miss",0)+1; g["consecutive_miss"]=cmiss
        bwn=mention(bowler[0],bowler[1]) if bowler else "Bowler"
        if g["mode"]=="solo":
            cur_uid=g["solo_order"][g["solo_current"]]
            g["solo_scores"][cur_uid]=g["solo_scores"].get(cur_uid,0)+6
            g["solo_balls"]=g.get("solo_balls",0)+1
            g["extras"][bi]+=6
        else:
            g["scores"][bi]+=6; g["extras"][bi]+=6
            g["innings_stats"][bi]["runs"]+=6
            g["innings_stats"][bi]["extras"]=g["innings_stats"][bi].get("extras",0)+6
            g["balls"]=g.get("balls",0)+1; g["innings_stats"][bi]["balls"]+=1
            if g["mode"]=="test": g["test_scores"][bi][g.get("test_innings_num",1)-1]=g["scores"][bi]
        send_html(cid,"⚠️ "+bwn+" missed! +6 runs to batter!\nMiss "+str(cmiss)+"/3 — 3 misses = eliminated!")
        if g["mode"] not in ("solo",) and check_target_after_penalty(g,cid): return True
        if cmiss>=3:
            g["consecutive_miss"]=0
            send_sticker(cid,WICKET_STICKER)
            if g["mode"]=="solo":
                cur_uid=g["solo_order"][g["solo_current"]]
                winner_name=next((p[1] for p in g["players"] if p[0]==cur_uid),"?")
                send(cid,"🚨 3 misses! "+bwn+" ELIMINATED!\n🏆 "+winner_name+" wins!")
                finish_game(g,cid,winner_name,0,1,"by bowler elimination!")
            else:
                batter=get_striker(g)
                batter_name=batter[1] if batter else (g["players"][bi][1] if bi<len(g["players"]) else "?")
                send(cid,"🚨 3 misses! "+bwn+" ELIMINATED!\n🏆 "+batter_name+" wins!")
                finish_game(g,cid,batter_name,bi,wi,"by bowler elimination!")
            return True
        else:
            next_ball_msg(g,cid)
            return False

def start_timers(g, cid, token, batter, bowler):
    def bt():
        try:
            time.sleep(30)
            if games.get(cid) is not g or g.get("ball_timer_token")!=token: return
            wk="solo_wc" if g["mode"]=="solo" else "wc"
            if g.get(wk) is None and g.get("phase")=="batting":
                send_html(cid,"⏰ 30s left!\n"+mention(bowler[0],bowler[1])+" send number in bot DM!")
                time.sleep(30)
                if games.get(cid) is not g or g.get("ball_timer_token")!=token: return
                if g.get(wk) is None and g.get("phase")=="batting":
                    handle_bowl_miss(g,cid,bowler)
        except Exception as e: print("bt error:",e)

    def bat_t():
        try:
            while True:
                time.sleep(1)
                if games.get(cid) is not g or g.get("ball_timer_token")!=token: return
                wk="solo_wc" if g["mode"]=="solo" else "wc"
                bk2="solo_bc" if g["mode"]=="solo" else "bc"
                if g.get(wk) is not None and g.get(bk2) is None and g.get("phase")=="batting":
                    time.sleep(30)
                    if games.get(cid) is not g or g.get("ball_timer_token")!=token: return
                    if g.get(wk) is not None and g.get(bk2) is None and g.get("phase")=="batting":
                        send_html(cid,"⏰ 30s left!\n"+mention(batter[0],batter[1])+" type 0-6!")
                        time.sleep(30)
                        if games.get(cid) is not g or g.get("ball_timer_token")!=token: return
                        if g.get(wk) is not None and g.get(bk2) is None and g.get("phase")=="batting":
                            send_sticker(cid,TIMEOUT_STICKER)
                            send_html(cid,"⌛ TIMEOUT! "+mention(batter[0],batter[1])+" dot ball!")
                            g[bk2]=g[wk]; g["bc"]=g[wk]; g["wc"]=g[wk]
                            if g["mode"]=="solo": g["solo_bc"]=None; g["solo_wc"]=None
                            resolve(g,cid)
                    return
                if g.get("phase")!="batting": return
        except Exception as e: print("bat_t error:",e)

    t1=threading.Thread(target=bt); t1.daemon=True; t1.start()
    t2=threading.Thread(target=bat_t); t2.daemon=True; t2.start()

def ask_batter_inline(g, cid, for_nonstriker=False):
    bi=g["batting"]; cap=g["captains"][bi]; host=g.get("host")
    kb=batter_kb(g,bi,for_nonstriker)
    if not kb:
        g["waiting_striker"]=False; g["waiting_nonstriker"]=False
        if not g.get("waiting_bowler"): next_ball_msg(g,cid)
        return
    reason="Choose NON-STRIKER:" if for_nonstriker else "Choose STRIKER:"
    if for_nonstriker: g["waiting_nonstriker"]=True
    else: g["waiting_striker"]=True
    if cap:
        cname=next((p[1] for p in g["teams"][bi] if p[0]==cap),"Captain")
        send_html(cid,"👑 "+mention(cap,cname)+" "+reason,kb)
    elif host:
        send_html(cid,"👑 "+mention(host,g.get("host_name","Host"))+" "+reason,kb)
    else:
        send(cid,"👑 "+reason,kb)

def ask_bowler_inline(g, cid, reason="⚾ Choose bowler:"):
    wi=g["bowling"]; host=g.get("host"); cap=g["captains"][wi]
    kb=bowler_kb(g)
    if not kb: return
    g["waiting_bowler"]=True
    if cap:
        cname=next((p[1] for p in g["teams"][wi] if p[0]==cap),"Captain")
        send_html(cid,mention(cap,cname)+" "+reason,kb)
    elif host:
        send_html(cid,mention(host,g.get("host_name","Host"))+" "+reason,kb)
    else:
        send(cid,reason,kb)

def cleanup_game(cid, g):
    for p in g.get("players",[]):
        if player_game.get(p[0])==cid:
            try: del player_game[p[0]]
            except: pass
    for ti in range(2):
        for p in g.get("teams",[[],[]])[ti]:
            if player_game.get(p[0])==cid:
                try: del player_game[p[0]]
                except: pass
    if cid in games:
        try: del games[cid]
        except: pass

def finish_game(g, cid, winner_name, winner_idx, loser_idx, margin):
    try:
        g["phase"]="done"
        send_sticker(cid,WIN_RUN_STICKER); send_sticker(cid,WIN_STICKER); send_sticker(cid,WIN_STICKER2)
        if is_team_mode(g):
            for p in g["teams"][winner_idx]:
                init_player(p[0],p[1]); upd(p[0],p[1],"wins"); upd(p[0],p[1],"games")
                upd_glb(cid,p[0],p[1],g["scores"][winner_idx],True)
            for p in g["teams"][loser_idx]:
                init_player(p[0],p[1]); upd(p[0],p[1],"losses"); upd(p[0],p[1],"games")
                upd_glb(cid,p[0],p[1],g["scores"][loser_idx],False)
        elif g["mode"]=="solo":
            ss=sorted(g["solo_scores"].items(),key=lambda x:x[1],reverse=True)
            for i,(uid,score) in enumerate(ss):
                p=next((x for x in g["players"] if x[0]==uid),None)
                if p:
                    won=i==0; upd(p[0],p[1],"wins" if won else "losses"); upd(p[0],p[1],"games")
                    upd_glb(cid,p[0],p[1],score,won)
        else:
            for i in range(min(2,len(g["players"]))):
                p=g["players"][i]; won=i==winner_idx
                upd(p[0],p[1],"wins" if won else "losses"); upd(p[0],p[1],"games")
                upd_glb(cid,p[0],p[1],g["scores"][i],won)

        result = build_final_scorecard(g,winner_name,margin)
        scorecard_text = result[0]
        best_bat_uid = result[1]; best_bat_name = result[2]
        best_bat_runs = result[3]; best_bat_balls = result[4]
        best_bat_fours = result[5]; best_bat_sixes = result[6]
        best_bowl_name = result[7]; best_bowl_runs = result[8]
        best_bowl_balls = result[9]; best_bowl_wkts = result[10]

        send_html(cid, scorecard_text)

        # Send MOM image
        if best_bat_uid:
            try:
                mom_img = generate_mom_image(
                    best_bat_name, int(best_bat_uid),
                    max(0,best_bat_runs), best_bat_balls, best_bat_fours, best_bat_sixes,
                    best_bowl_name, best_bowl_runs, best_bowl_balls, max(0,best_bowl_wkts),
                    winner_name
                )
                send_photo_buffer(cid, mom_img, "🎖️ Man of the Match — "+best_bat_name)
            except Exception as e:
                print("MOM image error:", e)

        cleanup_game(cid,g)
    except Exception as e:
        print("finish_game error:",e)
        send(cid,"🏆 MATCH OVER!\n🥇 WINNER: "+winner_name+"\nGG!")
        cleanup_game(cid,g)

# ================================================================
# FIXED FUNCTIONS - THESE WERE THE PROBLEMATIC ONES
# ================================================================

def check_hat_trick(g, bowler_uid):
    """Check if bowler has taken a hat-trick (3 wickets in 3 balls)"""
    track = g.setdefault("hat_trick_track", {})
    bk = str(bowler_uid)
    bowler_balls = track.setdefault(bk, [])
    if len(bowler_balls) >= 3:
        last3 = bowler_balls[-3:]
        return all(last3)  # All 3 balls were wickets (True)
    return False

def record_bowler_ball(g, bowler_uid, is_wicket):
    """Record a ball for hat-trick tracking"""
    track = g.setdefault("hat_trick_track", {})
    bk = str(bowler_uid)
    track.setdefault(bk, []).append(is_wicket)

# ================================================================
# END OF FIXED FUNCTIONS
# ================================================================

def save_test_innings_stats(g):
    ti = g.get("test_innings_num",1) - 1
    bi = g["batting"]; wi = g["bowling"]
    inn_idx = ti // 2
    if "test_bat_stats_per_inn" not in g: g["test_bat_stats_per_inn"] = {}
    if "test_bowl_stats_per_inn" not in g: g["test_bowl_stats_per_inn"] = {}
    import copy
    bat_key = str(bi)+"_"+str(inn_idx)
    bowl_key = str(wi)+"_"+str(inn_idx)
    g["test_bat_stats_per_inn"][bat_key] = copy.deepcopy(g["player_bat_stats"])
    g["test_bowl_stats_per_inn"][bowl_key] = copy.deepcopy(g["player_bowl_stats"])

def resolve(g, cid):
    try:
        bp=g.get("bc"); wp=g.get("wc")
        if bp is None or wp is None: return
        g["bc"]=None; g["wc"]=None
        bi=g["batting"]; wi=g["bowling"]
        is_fh=g.get("free_hit",False); g["free_hit"]=False
        g["consecutive_miss"]=0
        if "extras" not in g: g["extras"]=[0,0]
        if g["mode"]=="solo":
            batter,bowler=get_solo_bb(g)
            cur_uid=g["solo_order"][g["solo_current"]]
            g["solo_balls"]=g.get("solo_balls",0)+1
            g["solo_bowler_balls"]=g.get("solo_bowler_balls",0)+1
        else:
            batter=get_striker(g); bowler=get_bowler(g)
            g["balls"]=g.get("balls",0)+1
            g["innings_stats"][bi]["balls"]+=1
        if not batter or not bowler: return
        init_bat_stats(g,batter[0],batter[1])
        init_bowl_stats(g,bowler[0],bowler[1])
        upd(bowler[0],bowler[1],"balls_bowled")
        g["last_bowler"]=bowler[0]
        g["player_bowl_stats"][str(bowler[0])]["balls"]=g["player_bowl_stats"][str(bowler[0])].get("balls",0)+1
        nb=is_no_ball(bp,wp)
        bn=mention(batter[0],batter[1]); bwn=mention(bowler[0],bowler[1])
        if nb:
            upd(bowler[0],bowler[1],"no_balls"); upd(batter[0],batter[1],"free_hits")
            label="NB+"+str(bp)
            g["ball_log"].append(label); g["current_over_log"].append(label)
            g["player_ball_log"].setdefault(str(batter[0]),[]).append("NB")
            g["player_over_log"].setdefault(str(batter[0]),[]).append("NB")
            g["player_bowl_stats"][str(bowler[0])]["balls"]-=1
            g["player_bowl_stats"][str(bowler[0])]["runs"]=g["player_bowl_stats"][str(bowler[0])].get("runs",0)+bp
            g["current_over_runs"]=g.get("current_over_runs",0)+bp
            g["innings_stats"][bi]["runs"]+=bp
            g["extras"][bi]+=1+bp
            if g["mode"]=="solo":
                prev=g["solo_scores"].get(cur_uid,0); g["solo_scores"][cur_uid]=prev+bp
                g["solo_balls"]=max(0,g["solo_balls"]-1)
                g["solo_bowler_balls"]=max(0,g.get("solo_bowler_balls",1)-1)
            else:
                g["scores"][bi]+=bp
                g["balls"]=max(0,g["balls"]-1)
                g["innings_stats"][bi]["balls"]=max(0,g["innings_stats"][bi]["balls"]-1)
                if g["mode"]=="test": g["test_scores"][bi][g.get("test_innings_num",1)-1]=g["scores"][bi]
            ps=g["player_bat_stats"][str(batter[0])]
            ps["runs"]=ps.get("runs",0)+bp
            if bp==4: ps["fours"]=ps.get("fours",0)+1
            elif bp==6: ps["sixes"]=ps.get("sixes",0)+1
            g["free_hit"]=True
            if bp%2==1 and bp!=0 and is_team_mode(g): rotate_strike(g); g["last_ball_odd"]=True
            else: g["last_ball_odd"]=False
            record_bowler_ball(g,bowler[0],False)
            bat_line=live_bat_line(g,batter[0]); bowl_line=live_bowl_line(g,bowler[0])
            send_sticker(cid,NO_BALL_STICKER1); send_sticker(cid,NO_BALL_STICKER2)
            send_html(cid,"🚫 NO BALL! (1&6)\n🏏 "+bn+" played "+str(bp)+" | ⚾ "+bwn+" bowled "+str(wp)+"\n+"+str(bp)+" runs (Extras)!\n🆓 FREE HIT NEXT BALL!\n\n🏏 "+batter[1]+": "+bat_line+" | ⚾ "+bowler[1]+": "+bowl_line)
            send(bowler[0],"🚫 NO BALL! FREE HIT next ball!",back_kb(cid))
            send_sticker(cid,FREE_HIT_STICKER)
            if g.get("innings")==2 and g.get("target") and g["scores"][bi]>=g["target"]:
                wname=g["team_names"][bi] if is_team_mode(g) else (g["players"][bi][1] if bi<len(g["players"]) else "?")
                finish_game(g,cid,wname,bi,wi,"Chased successfully! 🎉"); return
            next_ball_msg(g,cid); return
        if bp==wp:
            if is_fh:
                label="FH"
                g["ball_log"].append(label); g["current_over_log"].append(label)
                g["player_ball_log"].setdefault(str(batter[0]),[]).append("FH")
                g["player_over_log"].setdefault(str(batter[0]),[]).append("FH")
                ps=g["player_bat_stats"][str(batter[0])]; ps["balls"]=ps.get("balls",0)+1
                upd(batter[0],batter[1],"balls_faced")
                record_bowler_ball(g,bowler[0],False)
                bat_line=live_bat_line(g,batter[0]); bowl_line=live_bowl_line(g,bowler[0])
                send_sticker(cid,FREE_HIT_STICKER)
                send_html(cid,"🆓 FREE HIT — DOT!\n"+bn+" NOT OUT!\n\n🏏 "+batter[1]+": "+bat_line+" | ⚾ "+bowler[1]+": "+bowl_line)
                send(bowler[0],"🆓 Free hit dot!",back_kb(cid))
                g["last_ball_odd"]=False
            else:
                label="W"
                g["ball_log"].append(label); g["current_over_log"].append(label)
                g["player_ball_log"].setdefault(str(batter[0]),[]).append("W")
                g["player_over_log"].setdefault(str(batter[0]),[]).append("W")
                ps=g["player_bat_stats"][str(batter[0])]; ps["balls"]=ps.get("balls",0)+1; ps["out"]=True
                upd(batter[0],batter[1],"balls_faced")
                g["current_over_runs"]=0
                g["innings_stats"][bi]["wickets"]=g["innings_stats"][bi].get("wickets",0)+1
                g["player_bowl_stats"][str(bowler[0])]["wickets"]=g["player_bowl_stats"][str(bowler[0])].get("wickets",0)+1
                if g["mode"]=="solo":
                    g["solo_wickets"]=g.get("solo_wickets",0)+1
                    if g["solo_scores"].get(cur_uid,0)==0: upd(batter[0],batter[1],"ducks")
                else:
                    g["wickets"][bi]+=1
                    if g["scores"][bi]==0: upd(batter[0],batter[1],"ducks")
                    g["dismissed"][bi].append(batter[0])
                    if g["mode"]=="test": g["test_wickets"][bi][g.get("test_innings_num",1)-1]=g["wickets"][bi]
                upd(bowler[0],bowler[1],"wickets")
                record_bowler_ball(g,bowler[0],True)
                if check_hat_trick(g,bowler[0]):
                    upd(bowler[0],bowler[1],"hat_tricks")
                    send_html(cid,"🎩 HAT-TRICK! "+bwn+" 3 wickets in a row!")
                    g["hat_trick_track"][str(bowler[0])]=[]
                bat_line=live_bat_line(g,batter[0]); bowl_line=live_bowl_line(g,bowler[0])
                send_sticker(cid,WICKET_STICKER)
                send_html(cid,"💥 WICKET!\n🏏 "+bn+" played "+str(bp)+"\n"+random.choice(COMMENTARY_WICKET)+"\n"+bn+" DISMISSED!\n\n🏏 "+batter[1]+": "+bat_line+" | ⚾ "+bowler[1]+": "+bowl_line)
                send(bowler[0],"💥 WICKET!",back_kb(cid))
                g["last_ball_odd"]=False
        else:
            label=str(bp)
            g["ball_log"].append(label); g["current_over_log"].append(label)
            g["player_ball_log"].setdefault(str(batter[0]),[]).append(bp)
            g["player_over_log"].setdefault(str(batter[0]),[]).append(bp)
            ps=g["player_bat_stats"][str(batter[0])]
            old_bat_runs=ps.get("runs",0)
            ps["balls"]=ps.get("balls",0)+1; ps["runs"]=old_bat_runs+bp
            if bp==4: ps["fours"]=ps.get("fours",0)+1
            elif bp==6: ps["sixes"]=ps.get("sixes",0)+1
            g["player_bowl_stats"][str(bowler[0])]["runs"]=g["player_bowl_stats"][str(bowler[0])].get("runs",0)+bp
            upd(batter[0],batter[1],"balls_faced"); upd(batter[0],batter[1],"runs",bp)
            upd(bowler[0],bowler[1],"runs_conceded",bp)
            g["current_over_runs"]=g.get("current_over_runs",0)+bp
            g["innings_stats"][bi]["runs"]+=bp
            if bp==1: g["innings_stats"][bi]["singles"]+=1
            elif bp==4: g["innings_stats"][bi]["fours"]+=1; upd(batter[0],batter[1],"fours")
            elif bp==6: g["innings_stats"][bi]["sixes"]+=1; upd(batter[0],batter[1],"sixes")
            if g["mode"]=="solo":
                prev=g["solo_scores"].get(cur_uid,0); g["solo_scores"][cur_uid]=prev+bp; score_now=g["solo_scores"][cur_uid]
            else:
                g["scores"][bi]+=bp; score_now=g["scores"][bi]
                if g["mode"]=="test": g["test_scores"][bi][g.get("test_innings_num",1)-1]=score_now
            init_player(batter[0],batter[1])
            p_row=get_player(batter[0])
            if p_row and score_now>p_row["highest"]:
                conn=get_db(); c=conn.cursor()
                c.execute('UPDATE players SET highest=?, highest_balls=? WHERE uid=?',
                    (score_now, g["innings_stats"][bi]["balls"], batter[0]))
                conn.commit(); conn.close()
            record_bowler_ball(g,bowler[0],False)
            bat_line=live_bat_line(g,batter[0]); bowl_line=live_bowl_line(g,bowler[0])
            if bp==0:
                send_sticker(cid,ZERO_STICKER)
                send_html(cid,"🔴 DOT BALL!\n🏏 "+bn+"\nTotal: "+str(score_now)+"\n\n🏏 "+batter[1]+": "+bat_line+" | ⚾ "+bowler[1]+": "+bowl_line)
                send(bowler[0],"🔴 Dot!\n🏏 "+batter[1]+": "+bat_line,back_kb(cid))
            elif bp==6:
                send_sticker(cid,SIX_STICKER)
                send_html(cid,"🔥 SIX!\n🏏 "+bn+"\n"+random.choice(COMMENTARY_SIX)+"\nTotal: "+str(score_now)+"\n\n🏏 "+batter[1]+": "+bat_line+" | ⚾ "+bowler[1]+": "+bowl_line)
                send(bowler[0],"🔥 SIX!\n🏏 "+batter[1]+": "+bat_line,back_kb(cid))
            elif bp==4:
                send_sticker(cid,FOUR_STICKER)
                send_html(cid,"🏏 FOUR!\n🏏 "+bn+"\n"+random.choice(COMMENTARY_FOUR)+"\nTotal: "+str(score_now)+"\n\n🏏 "+batter[1]+": "+bat_line+" | ⚾ "+bowler[1]+": "+bowl_line)
                send(bowler[0],"🏏 FOUR!\n🏏 "+batter[1]+": "+bat_line,back_kb(cid))
            elif bp==5:
                send_sticker(cid,FIVE_STICKER)
                send_html(cid,"✨ 5!\n🏏 "+bn+"\n"+random.choice(COMMENTARY_FIVE)+"\nTotal: "+str(score_now)+"\n\n🏏 "+batter[1]+": "+bat_line+" | ⚾ "+bowler[1]+": "+bowl_line)
                send(bowler[0],"✨ 5!\n🏏 "+batter[1]+": "+bat_line,back_kb(cid))
            elif bp==3:
                send_sticker(cid,RUN_STICKER)
                send_html(cid,"✅ 3 RUNS\n🏏 "+bn+"\n"+random.choice(COMMENTARY_THREE)+"\nTotal: "+str(score_now)+"\n\n🏏 "+batter[1]+": "+bat_line+" | ⚾ "+bowler[1]+": "+bowl_line)
                send(bowler[0],"✅ 3!\n🏏 "+batter[1]+": "+bat_line,back_kb(cid))
            elif bp==2:
                send_sticker(cid,TWO_RUN_STICKER)
                send_html(cid,"✅ 2 RUNS\n🏏 "+bn+"\n"+random.choice(COMMENTARY_TWO)+"\nTotal: "+str(score_now)+"\n\n🏏 "+batter[1]+": "+bat_line+" | ⚾ "+bowler[1]+": "+bowl_line)
                send(bowler[0],"✅ 2!\n🏏 "+batter[1]+": "+bat_line,back_kb(cid))
            elif bp==1:
                send_sticker(cid,ONE_RUN_STICKER)
                send_html(cid,"✅ 1 RUN\n🏏 "+bn+"\n"+random.choice(COMMENTARY_ONE)+"\nTotal: "+str(score_now)+"\n\n🏏 "+batter[1]+": "+bat_line+" | ⚾ "+bowler[1]+": "+bowl_line)
                send(bowler[0],"✅ 1!\n🏏 "+batter[1]+": "+bat_line,back_kb(cid))
            if bp%2==1 and bp!=0 and is_team_mode(g): rotate_strike(g); g["last_ball_odd"]=True
            else: g["last_ball_odd"]=False
            check_individual_fifty(g,cid,batter[0],batter[1],ps["runs"],old_bat_runs)
        g["batter_zero_count"][str(batter[0])]=0
        if g["mode"]=="solo": handle_solo_after(g,cid,bp,wp,is_fh); return
        if g["mode"]=="test" and not is_team_mode(g): handle_test_after(g,cid,bp,wp,is_fh); return
        max_wkts=max_wkts_for_team(g,bi) if is_team_mode(g) else g.get("max_wickets",3)
        inf=g.get("infinity_overs",False); overs_val=g.get("overs") or 0; balls_now=g.get("balls",0)
        over_complete=not inf and overs_val>0 and balls_now>0 and balls_now%6==0
        over_done=(not inf and overs_val>0 and balls_now>=overs_val*6) or g["wickets"][bi]>=max_wkts
        if bp==wp and not is_fh and not over_done:
            avail=[p for p in g["teams"][bi] if p[0] not in g["dismissed"][bi]] if is_team_mode(g) else []
            if is_team_mode(g) and len(avail)<=1: over_done=True
            elif is_team_mode(g): ask_batter_inline(g,cid,for_nonstriker=False); return
        if g.get("innings")==2 and g.get("target") is not None:
            if g["scores"][bi]>=g["target"]:
                wname=g["team_names"][bi] if is_team_mode(g) else (g["players"][bi][1] if bi<len(g["players"]) else "?")
                finish_game(g,cid,wname,bi,wi,"Chased successfully!"); return
        if over_complete and not over_done and is_team_mode(g):
            for k in g["player_over_log"]: g["player_over_log"][k]=[]
            send_html(cid,build_over_scorecard(g))
            g["current_over_log"]=[]; g["current_over_runs"]=0
            g["last_bowler"]=bowler[0]
            g["player_bowl_stats"][str(bowler[0])]["overs"]=g["player_bowl_stats"][str(bowler[0])].get("overs",0)+1
            g["current_bowler"]=None; g["over_bowler_locked"]=False
            if not g.get("last_ball_odd",False): rotate_strike(g)
            g["last_ball_odd"]=False
            ask_bowler_inline(g,cid,"⚾ Over "+str(balls_now//6)+" complete! Choose next bowler:"); return
        elif over_complete and not over_done:
            g["current_over_log"]=[]; g["current_over_runs"]=0
        if over_done:
            if is_team_mode(g): send_html(cid,build_innings_end_scorecard(g,g.get("innings",1)))
            if g.get("innings")==2:
                margin_runs=max(0,(g.get("target",1)-1)-g["scores"][bi])
                wname=g["team_names"][wi] if is_team_mode(g) else (g["players"][wi][1] if wi<len(g["players"]) else "?")
                finish_game(g,cid,wname,wi,bi,"by "+str(margin_runs)+" runs"); return
            else:
                if is_team_mode(g):
                    inn1_bat=g["batting"]
                    g["phase"]="innings_break"
                    host=g.get("host"); hname=g.get("host_name","Host")
                    send_html(cid,
                        build_innings_end_scorecard(g,1)+
                        "\n\n⚡ <b>INNINGS 1 COMPLETE!</b>\n"+
                        "🏏 "+g["team_names"][inn1_bat]+": "+str(g["scores"][inn1_bat])+"/"+str(g["wickets"][inn1_bat])+"\n\n"+
                        (mention(host,hname) if host else hname)+" type /swap_innings to start Innings 2!"
                    )
                else:
                    g["target"]=g["scores"][bi]+1; g["innings"]=2
                    g["batting"],g["bowling"]=g["bowling"],g["batting"]
                    bi_new=g["batting"]
                    g["balls"]=0; g["wickets"][bi_new]=0
                    g["current_over_runs"]=0; g["ball_log"]=[]; g["current_over_log"]=[]
                    g["last_bowler"]=None; g["current_bowler"]=None; g["over_bowler_locked"]=False
                    g["dismissed"][bi_new]=[]
                    g["striker"]=None; g["non_striker"]=None; g["last_ball_odd"]=False
                    g["innings_stats"]=[{"runs":0,"balls":0,"sixes":0,"fours":0,"singles":0,"wickets":0,"extras":0},{"runs":0,"balls":0,"sixes":0,"fours":0,"singles":0,"wickets":0,"extras":0}]
                    g["waiting_striker"]=False; g["waiting_nonstriker"]=False; g["waiting_bowler"]=False
                    g["hat_trick_track"]={}; g["consecutive_miss"]=0
                    for k in g["player_over_log"]: g["player_over_log"][k]=[]
                    send_sticker(cid,INNINGS_STICKER)
                    bat_nm=g["players"][g["batting"]][1] if g["batting"]<len(g["players"]) else "?"
                    send(cid,"⚡ INNINGS 2!\n"+bat_nm+" need "+str(g["target"])+" to win!")
                    next_ball_msg(g,cid)
        elif not (over_complete and is_team_mode(g)):
            next_ball_msg(g,cid)
    except Exception as e:
        print("resolve error:",e)
        import traceback; traceback.print_exc()

def handle_test_after(g, cid, bp, wp, is_fh):
    try:
        bi=g["batting"]; wi=g["bowling"]
        ti=g.get("test_innings_num",1)
        balls_now=g.get("balls",0) or 0
        overs_val=g.get("overs") or 0; max_wkts=g.get("max_wickets",3)
        over_complete=balls_now>0 and overs_val>0 and balls_now%6==0
        over_done=(overs_val>0 and balls_now>=overs_val*6) or g["wickets"][bi]>=max_wkts
        if ti==4 and g.get("target") is not None and g["scores"][bi]>=g["target"]:
            g["test_scores"][bi][ti-1]=g["scores"][bi]; g["test_wickets"][bi][ti-1]=g["wickets"][bi]
            save_test_innings_stats(g)
            nm=g["players"][bi][1] if bi<len(g["players"]) else "?"
            finish_game(g,cid,nm,bi,wi,"chased target!"); return
        if over_complete and not over_done:
            send(cid,"📋 Over "+str(balls_now//6)+" done\n"+simple_sb(g))
            g["current_over_log"]=[]; g["current_over_runs"]=0
        if over_done:
            g["test_scores"][bi][ti-1]=g["scores"][bi]; g["test_wickets"][bi][ti-1]=g["wickets"][bi]
            save_test_innings_stats(g)
            def reset_inn():
                g["balls"]=0; g["wickets"]=[0,0]; g["scores"]=[0,0]
                g["current_over_runs"]=0; g["ball_log"]=[]; g["last_bowler"]=None
                g["dismissed"]=[[],[]]; g["current_over_log"]=[]; g["consecutive_miss"]=0
                g["player_bat_stats"]={}; g["player_bowl_stats"]={}
            if ti==1:
                g["test_innings_num"]=2; g["innings"]=2; g["batting"],g["bowling"]=g["bowling"],g["batting"]
                reset_inn(); send_sticker(cid,INNINGS_STICKER); send(cid,"🏟️ TEST — INN 2!\n"+simple_sb(g)); next_ball_msg(g,cid)
            elif ti==2:
                a1=g["test_scores"][0][0]; b1=g["test_scores"][1][0]; lead=a1-b1
                if bi==1 and lead>=30 and not g.get("follow_on_offered"):
                    g["follow_on_offered"]=True
                    host=g.get("host") or g.get("creator"); hname=g.get("host_name","Host")
                    send_html(cid,simple_sb(g)+"\n\n📊 "+(g["players"][0][1] if g["players"] else "A")+" leads by "+str(lead)+"!\n\n"+(mention(host,hname) if host else hname)+" enforce follow-on?",follow_on_kb()); return
                g["test_innings_num"]=3; g["innings"]=3; g["batting"],g["bowling"]=g["bowling"],g["batting"]
                reset_inn(); send_sticker(cid,INNINGS_STICKER); send(cid,"🏟️ TEST — INN 3!\n"+simple_sb(g)); next_ball_msg(g,cid)
            elif ti==3:
                a1=g["test_scores"][0][0]; a3=g["test_scores"][0][2]; b1=g["test_scores"][1][0]
                a_total=a1+a3; lead=a_total-b1
                if lead<=0:
                    nm1=g["players"][1][1] if len(g["players"])>1 else "B"
                    finish_game(g,cid,nm1,1,0,"by innings and "+str(abs(lead))+" runs"); return
                g["target"]=lead+1; g["test_innings_num"]=4; g["innings"]=4; g["batting"],g["bowling"]=g["bowling"],g["batting"]
                reset_inn(); send_sticker(cid,INNINGS_STICKER)
                nm_chase=g["players"][g["batting"]][1] if g["batting"]<len(g["players"]) else "?"
                send(cid,"🏟️ TEST — INN 4!\n🎯 "+nm_chase+" need "+str(g["target"])+" to win!\n"+simple_sb(g)); next_ball_msg(g,cid)
            elif ti==4:
                target_val=g.get("target") or 1
                if g["scores"][bi]>=target_val:
                    nm=g["players"][bi][1] if bi<len(g["players"]) else "?"
                    finish_game(g,cid,nm,bi,wi,"chased!"); return
                margin_v=max(0,target_val-1-g["scores"][bi])
                wname=g["players"][1-bi][1] if (1-bi)<len(g["players"]) else "?"
                finish_game(g,cid,wname,1-bi,bi,"by "+str(margin_v)+" runs")
        else: next_ball_msg(g,cid)
    except Exception as e:
        print("handle_test_after error:",e)
        import traceback; traceback.print_exc()

def handle_solo_after(g, cid, bp, wp, is_fh):
    try:
        inf=g.get("infinity_overs",False); overs_val=g.get("overs") or 0
        solo_balls=g.get("solo_balls",0)
        over_complete=not inf and overs_val>0 and solo_balls>0 and solo_balls%6==0
        over=(not inf and overs_val>0 and solo_balls>=overs_val*6) or g.get("solo_wickets",0)>=g.get("max_wickets",1)
        if over_complete and not over:
            send(cid,"📋 Over "+str(solo_balls//6)+" done | "+str(g["solo_scores"].get(g["solo_order"][g["solo_current"]],0))+" runs")
            g["current_over_log"]=[]; g["current_over_runs"]=0
        if g.get("solo_bowler_balls",0)>=3 and not over:
            nb=get_next_solo_bowler(g)
            if nb: g["solo_bowler"]=nb[0]; g["solo_bowler_balls"]=0
        wicket=bp==wp and not is_fh
        if over or wicket:
            g["solo_current"]+=1; g["solo_balls"]=0; g["solo_wickets"]=0
            g["ball_log"]=[]; g["current_over_log"]=[]; g["current_over_runs"]=0
            g["last_bowler"]=None; g["solo_bowler_balls"]=0; g["consecutive_miss"]=0
            if g["solo_current"]>=len(g["solo_order"]):
                ss=sorted(g["solo_scores"].items(),key=lambda x:x[1],reverse=True)
                winner_uid=ss[0][0]; winner_name=next((p[1] for p in g["players"] if p[0]==winner_uid),"?")
                finish_game(g,cid,winner_name,0,1,""); return
            next_uid=g["solo_order"][g["solo_current"]]
            next_name=next((p[1] for p in g["players"] if p[0]==next_uid),"?")
            nb2=get_next_solo_bowler(g)
            if nb2: g["solo_bowler"]=nb2[0]
            send_sticker(cid,START_STICKER)
            send(cid,"🏏 NEXT BATTER: "+next_name+"!\n"+simple_sb(g))
        next_ball_msg(g,cid)
    except Exception as e: print("handle_solo_after error:",e)

def join_timer_team(cid):
    for _ in range(60):
        time.sleep(5)
        g=games.get(cid)
        if not g or g.get("phase")!="joining": return
        remaining=(g.get("join_deadline") or 0)-time.time()
        if remaining<=60 and not g.get("join_warned"):
            g["join_warned"]=True
            send(cid,"⏰ 1 minute left!\nTap Join buttons or /join_a /join_b\n/extend to add 30s")
        if remaining<=0:
            g2=games.get(cid)
            if g2 and g2.get("phase")=="joining":
                a=g2["teams"][0]; b=g2["teams"][1]
                if not a or not b:
                    send(cid,"❌ Both teams need players! Game cancelled.")
                    if cid in games: del games[cid]; return
                send(cid,"⏰ Join time ended! Starting...\n🔵 Team A ("+str(len(a))+"): "+", ".join([p[1] for p in a])+"\n🔴 Team B ("+str(len(b))+"): "+", ".join([p[1] for p in b]))
                proceed_to_over_selection(g2,cid)
            return

def join_timer_solo(cid):
    for _ in range(24):
        time.sleep(5)
        g=games.get(cid)
        if not g or g.get("phase") not in ("joining","waiting"): return
        remaining=(g.get("join_deadline") or 0)-time.time()
        if remaining<=30 and not g.get("join_warned"):
            g["join_warned"]=True
            send(cid,"⏰ 30s left! /join to join!\n/startmatch if 3+ players ready")
        if remaining<=0:
            g2=games.get(cid)
            if g2 and g2.get("phase") in ("joining","waiting"):
                if len(g2.get("players",[]))>=3:
                    send(cid,"⏰ Join time ended! Starting with "+str(len(g2["players"]))+" players!")
                    start_solo_game(g2,cid)
                else:
                    send(cid,"❌ Need at least 3 players! Only "+str(len(g2.get("players",[])))+" joined. Game cancelled.")
                    if cid in games: del games[cid]
            return

def join_timer(cid):
    while True:
        time.sleep(5)
        g=games.get(cid)
        if not g or g.get("phase") not in ("joining","waiting"): return
        remaining=(g.get("join_deadline") or 0)-time.time()
        if remaining<=30 and not g.get("join_warned"):
            g["join_warned"]=True
            send(cid,"⏰ 30s left! /join to join!\n/extend to add time!")
        if remaining<=0:
            if g and g.get("phase") in ("joining","waiting"):
                if cid in games: del games[cid]
                send(cid,"Join time ended. Game cancelled!")
            return

def proceed_to_over_selection(g, cid):
    g["phase"]="setup_over"
    host=g.get("host")
    if host: send_html(cid,"🎮 "+mention(host,g.get("host_name","Host"))+" choose overs:",over_kb_team())
    else: send(cid,"Choose overs:",over_kb_team())

def start_solo_game(g, cid):
    g["solo_order"]=[p[0] for p in g["players"]]
    random.shuffle(g["solo_order"])
    for uid in g["solo_order"]: g["solo_scores"][uid]=0
    names=[next((p[1] for p in g["players"] if p[0]==uid),"?") for uid in g["solo_order"]]
    send(cid,"📋 Batting order:\n"+"\n".join([str(i+1)+". "+n for i,n in enumerate(names)]))
    g["phase"]="batting"; g["max_wickets"]=1
    first_uid=g["solo_order"][0]
    first=next((p[1] for p in g["players"] if p[0]==first_uid),"?")
    nb=get_next_solo_bowler(g)
    if nb: g["solo_bowler"]=nb[0]
    send_sticker(cid,START_STICKER)
    send(cid,"🏏 TOURNAMENT STARTS!\n"+first+" bats first!")
    next_ball_msg(g,cid)

def get_entities_players(msg):
    results=[]
    entities=msg.get("entities",[])
    for ent in entities:
        if ent.get("type")=="text_mention":
            m=ent.get("user",{}); puid=m.get("id"); pname=m.get("first_name","Player")
            if puid: results.append((puid,pname))
    return results

def do_innings2_start(g, cid):
    old_bat=g["batting"]
    g["target"]=g["scores"][old_bat]+1
    g["innings"]=2
    g["batting"],g["bowling"]=g["bowling"],g["batting"]
    bi_new=g["batting"]
    g["balls"]=0; g["wickets"][bi_new]=0
    g["current_over_runs"]=0; g["ball_log"]=[]; g["current_over_log"]=[]
    g["last_bowler"]=None; g["current_bowler"]=None; g["over_bowler_locked"]=False
    g["dismissed"][bi_new]=[]
    g["striker"]=None; g["non_striker"]=None; g["last_ball_odd"]=False
    g["innings_stats"]=[{"runs":0,"balls":0,"sixes":0,"fours":0,"singles":0,"wickets":0,"extras":0},{"runs":0,"balls":0,"sixes":0,"fours":0,"singles":0,"wickets":0,"extras":0}]
    g["waiting_striker"]=False; g["waiting_nonstriker"]=False; g["waiting_bowler"]=False
    g["hat_trick_track"]={}; g["consecutive_miss"]=0
    for k in g["player_over_log"]: g["player_over_log"][k]=[]
    send_sticker(cid,INNINGS_STICKER)
    bat_nm=g["team_names"][g["batting"]]; bowl_nm=g["team_names"][g["bowling"]]
    host=g.get("host"); hname=g.get("host_name","Host")
    txt="⚡ INNINGS 2 STARTS!\n"+bat_nm+" need "+str(g["target"])+" to win!\n"
    txt+="\n🏏 Batting: "+bat_nm+"\n"+squad_text(g,g["batting"])
    txt+="\n⚾ Bowling: "+bowl_nm+"\n"+squad_text(g,g["bowling"])
    send(cid,txt)
    g["waiting_striker"]=True; g["waiting_nonstriker"]=True; g["waiting_bowler"]=True
    g["striker"]=None; g["non_striker"]=None; g["current_bowler"]=None
    bi2=g["batting"]; wi2=g["bowling"]
    cap_bat2=g["captains"][bi2]; cap_bowl2=g["captains"][wi2]
    if cap_bat2:
        cbn2=next((p[1] for p in g["teams"][bi2] if p[0]==cap_bat2),"Captain")
        send_html(cid,"👑 "+mention(cap_bat2,cbn2)+" choose STRIKER:",batter_kb(g,bi2,False))
    else:
        send_html(cid,"👑 "+mention(host,hname)+" choose STRIKER:",batter_kb(g,bi2,False))
    if cap_bowl2:
        cwn2=next((p[1] for p in g["teams"][wi2] if p[0]==cap_bowl2),"Captain")
        send_html(cid,"👑 "+mention(cap_bowl2,cwn2)+" choose opening BOWLER:",bowler_kb(g))
    else:
        send_html(cid,"👑 "+mention(host,hname)+" choose opening BOWLER:",bowler_kb(g))

offset=0
def poll():
    global offset
    try:
        r=requests.get(URL+"getUpdates",params={"offset":offset,"timeout":30},timeout=35)
        return r.json().get("result",[])
    except requests.exceptions.Timeout: return []
    except Exception as e: print("Poll error:",e); return []

def handle_message(msg):
    try:
        cid=msg["chat"]["id"]
        uid=msg["from"]["id"]
        name=msg["from"].get("first_name","Player")
        text=msg.get("text","").strip()
        chat_type=msg["chat"].get("type","")
        g=games.get(cid)
        tl=text.lower()

        if tl.startswith("/start") and chat_type=="private":
            group_cid=player_game.get(uid)
            g2=games.get(group_cid)
            if g2 and g2.get("phase")=="batting":
                if g2["mode"]=="solo": _,bowler=get_solo_bb(g2)
                else: bowler=get_bowler(g2)
                if bowler and uid==bowler[0]:
                    if g2["mode"]=="solo": batter,_=get_solo_bb(g2); balls=g2.get("solo_balls",0)
                    else: batter=get_striker(g2); balls=g2.get("balls",0)
                    overs_val=g2.get("overs") or 0
                    total="♾️" if g2.get("infinity_overs") else str(overs_val*6)
                    fh="\n🆓 FREE HIT!" if g2.get("free_hit") else ""
                    bat_line=live_bat_line(g2,batter[0]) if batter else ""
                    send(uid,"🎯 YOUR TURN TO BOWL!\n━━━━━━━━━━━━━━━━\n🏏 Batter: "+(batter[1] if batter else "?")+"  "+bat_line+"\n🔢 Send 1-6 (NOT 0!)\n━━━━━━━━━━━━━━━━\n🎳 "+ov_str(balls)+" of "+total+fh+"\n⏱ 1 minute!",back_kb(group_cid))
                    return
            send(uid,"Hi! Cricket Rivalry Bot!\n🎯 Bowler types secret number here!\n\nGo to your group to play!")
            return

        if tl.startswith("/newgame"):
            if chat_type=="private": send(cid,"Use /newgame in your group!"); return
            if cid in games: send(cid,"Game running! Use /endgame first."); return
            send_banner(cid)
            send(cid,"🏏 Welcome to Cricket Rivalry!\n\nChoose game mode:",mode_kb())
            return

        if tl.startswith("/mystats"):
            p = get_player(uid)
            if not p:
                send(cid,"No stats yet! Play first.")
                return
            try:
                img_buf = generate_mystats_image(uid, name)
                send_photo_buffer(cid, img_buf, mystats_text(uid, name))
            except Exception as e:
                print("mystats image error:", e)
                send(cid, mystats_text(uid, name))
            return

        if tl.startswith("/swap_innings"):
            if chat_type=="private": send(cid,"Use in your group!"); return
            if not g: send(cid,"No game running!"); return
            if not is_host(g,uid): send(cid,"🚫 Only HOST can use /swap_innings!"); return
            if g.get("phase")!="innings_break": send(cid,"⚠️ Only usable after innings 1 ends!"); return
            g["phase"]="batting"
            do_innings2_start(g,cid)
            return

        if tl.startswith("/change_host"):
            if chat_type=="private": send(cid,"Use in your group!"); return
            if not g: send(cid,"No game running!"); return
            if not is_host(g,uid): send(cid,"🚫 Only current HOST can transfer host!"); return
            reply=msg.get("reply_to_message")
            if not reply or not reply.get("from"): send(cid,"Reply to someone's message to make them host!"); return
            new_host_uid=reply["from"]["id"]; new_host_name=reply["from"].get("first_name","Player")
            if new_host_uid==uid: send(cid,"You are already the host!"); return
            old_host_name=g.get("host_name","Host")
            g["host"]=new_host_uid; g["host_name"]=new_host_name
            if not any(p[0]==new_host_uid for p in g["players"]): g["players"].append((new_host_uid,new_host_name))
            player_game[new_host_uid]=cid
            send_html(cid,"🎮 Host transferred!\n"+mention(new_host_uid,new_host_name)+" is now the HOST!\n\n(Previous host: "+old_host_name+")")
            return

        if tl.startswith("/choose_captain") or tl.startswith("/change_captain"):
            if chat_type=="private": send(cid,"Use in your group!"); return
            if not g: send(cid,"No game running!"); return
            if not is_host(g,uid): send(cid,"🚫 Only HOST can change captains!"); return
            if not g["teams"][0] or not g["teams"][1]: send(cid,"Need players in both teams first!"); return
            g["phase"]="choose_cap_a"
            send_html(cid,"👑 Choose Team A Captain:",cap_a_kb(g["teams"]))
            return

        if tl.startswith("/toss"):
            if chat_type=="private": send(cid,"Use in your group!"); return
            if not g: send(cid,"No game running!"); return
            if not is_host(g,uid): send(cid,"🚫 Only HOST can do toss!"); return
            if is_team_mode(g):
                cap_a=g["captains"][0]
                if not cap_a: send(cid,"Set captains first! Use /choose_captain"); return
                cap_a_name=next((p[1] for p in g["teams"][0] if p[0]==cap_a),"Captain A")
                g["phase"]="toss"
                send_html(cid,"🪙 TOSS TIME!\n\n"+mention(cap_a,cap_a_name)+" (Team A Captain) calls the toss!",toss_kb())
            else:
                if len(g.get("players",[]))<2: send(cid,"Need 2 players first!"); return
                caller=g["players"][0]; g["phase"]="toss"
                send_html(cid,"🪙 TOSS TIME!\n\n"+mention(caller[0],caller[1])+" calls the toss!",toss_kb())
            return

        if tl.startswith("/join_a") or tl.startswith("/joina"):
            if not g: send(cid,"No game! Use /newgame first."); return
            if g.get("phase")!="joining": send(cid,"Joining is not open right now!"); return
            if uid==g.get("host"): send(cid,"Host cannot join a team!"); return
            already_team=None
            for i,team in enumerate(g["teams"]):
                if any(p[0]==uid for p in team): already_team=i; break
            if already_team==0: send(cid,"⚠️ You are already in 🔵 Team A!"); return
            if already_team==1: send(cid,"⚠️ You are already in 🔴 Team B!"); return
            g["teams"][0].append((uid,name))
            if not any(p[0]==uid for p in g["players"]): g["players"].append((uid,name))
            player_game[uid]=cid
            send(cid,"✅ "+name+" → 🔵 Team A!\n🔵 A("+str(len(g["teams"][0]))+"): "+", ".join([p[1] for p in g["teams"][0]])+"\n🔴 B("+str(len(g["teams"][1]))+"): "+", ".join([p[1] for p in g["teams"][1]]))
            return

        if tl.startswith("/join_b") or tl.startswith("/joinb"):
            if not g: send(cid,"No game! Use /newgame first."); return
            if g.get("phase")!="joining": send(cid,"Joining is not open right now!"); return
            if uid==g.get("host"): send(cid,"Host cannot join a team!"); return
            already_team=None
            for i,team in enumerate(g["teams"]):
                if any(p[0]==uid for p in team): already_team=i; break
            if already_team==1: send(cid,"⚠️ You are already in 🔴 Team B!"); return
            if already_team==0: send(cid,"⚠️ You are already in 🔵 Team A!"); return
            g["teams"][1].append((uid,name))
            if not any(p[0]==uid for p in g["players"]): g["players"].append((uid,name))
            player_game[uid]=cid
            send(cid,"✅ "+name+" → 🔴 Team B!\n🔵 A("+str(len(g["teams"][0]))+"): "+", ".join([p[1] for p in g["teams"][0]])+"\n🔴 B("+str(len(g["teams"][1]))+"): "+", ".join([p[1] for p in g["teams"][1]]))
            return

        if "/join" in tl and "/join_a" not in tl and "/join_b" not in tl and "/joina" not in tl and "/joinb" not in tl:
            if chat_type=="private": send(cid,"Use /join in your group!"); return
            if not g: send(cid,"No game. Use /newgame"); return
            if g.get("phase") not in ("joining","waiting"): send(cid,"Cannot join now!"); return
            if is_team_mode(g): send(cid,"Use /join_a or /join_b!"); return
            if any(p[0]==uid for p in g["players"]): send(cid,"⚠️ You already joined!"); return
            g["players"].append((uid,name)); player_game[uid]=cid
            if g.get("mode") in ("1v1","test") and g.get("test_type")!="team":
                if len(g["players"])==2:
                    g["phase"]="toss"; caller=g["players"][0]
                    send_html(cid,g["players"][0][1]+" vs "+g["players"][1][1]+"!\n\n🪙 "+mention(caller[0],caller[1])+" call the toss:",toss_kb())
                else: send(cid,name+" joined! Waiting for 1 more... /join")
            elif g.get("mode")=="solo":
                needed=g.get("max_players") or 999; joined=len(g["players"])
                if g.get("infinity_players"): send(cid,name+" joined! Total: "+str(joined)+"\n/startmatch to start")
                else:
                    send(cid,name+" joined! "+str(joined)+"/"+str(needed))
                    if joined>=needed: start_solo_game(g,cid)
            return

        if tl.startswith("/add_a"):
            if not g or not is_host(g,uid): send(cid,"🚫 Only HOST can add players!"); return
            added=[]
            reply=msg.get("reply_to_message")
            if reply and reply.get("from"):
                puid=reply["from"]["id"]; pname=reply["from"].get("first_name","Player")
                if puid!=uid:
                    for i,team in enumerate(g["teams"]): g["teams"][i]=[p for p in team if p[0]!=puid]
                    g["teams"][0].append((puid,pname))
                    if not any(p[0]==puid for p in g["players"]): g["players"].append((puid,pname))
                    player_game[puid]=cid; added.append(pname)
            for puid,pname in get_entities_players(msg):
                if puid and puid!=uid:
                    for i,team in enumerate(g["teams"]): g["teams"][i]=[p for p in team if p[0]!=puid]
                    g["teams"][0].append((puid,pname))
                    if not any(p[0]==puid for p in g["players"]): g["players"].append((puid,pname))
                    player_game[puid]=cid; added.append(pname)
            if added: send(cid,"✅ Added to 🔵 Team A: "+", ".join(added))
            else: send(cid,"❌ No player found! Reply to their message → /add_a")
            return

        if tl.startswith("/add_b"):
            if not g or not is_host(g,uid): send(cid,"🚫 Only HOST can add players!"); return
            added=[]
            reply=msg.get("reply_to_message")
            if reply and reply.get("from"):
                puid=reply["from"]["id"]; pname=reply["from"].get("first_name","Player")
                if puid!=uid:
                    for i,team in enumerate(g["teams"]): g["teams"][i]=[p for p in team if p[0]!=puid]
                    g["teams"][1].append((puid,pname))
                    if not any(p[0]==puid for p in g["players"]): g["players"].append((puid,pname))
                    player_game[puid]=cid; added.append(pname)
            for puid,pname in get_entities_players(msg):
                if puid and puid!=uid:
                    for i,team in enumerate(g["teams"]): g["teams"][i]=[p for p in team if p[0]!=puid]
                    g["teams"][1].append((puid,pname))
                    if not any(p[0]==puid for p in g["players"]): g["players"].append((puid,pname))
                    player_game[puid]=cid; added.append(pname)
            if added: send(cid,"✅ Added to 🔴 Team B: "+", ".join(added))
            else: send(cid,"❌ No player found! Reply to their message → /add_b")
            return

        if tl.startswith("/remove_player"):
            if not g or not is_host(g,uid): send(cid,"🚫 Only HOST can remove players!"); return
            removed=[]
            reply=msg.get("reply_to_message")
            if reply and reply.get("from"):
                puid=reply["from"]["id"]; pname=reply["from"].get("first_name","?")
                g["players"]=[p for p in g["players"] if p[0]!=puid]
                for team in g["teams"]: team[:]=[p for p in team if p[0]!=puid]
                if puid in player_game: del player_game[puid]
                removed.append(pname)
            for puid,pname in get_entities_players(msg):
                if puid:
                    g["players"]=[p for p in g["players"] if p[0]!=puid]
                    for team in g["teams"]: team[:]=[p for p in team if p[0]!=puid]
                    if puid in player_game: del player_game[puid]
                    removed.append(pname)
            send(cid,("✅ Removed: "+", ".join(removed)) if removed else "Reply to member's message!")
            return

        if tl.startswith("/swap"):
            if not g or not is_host(g,uid): send(cid,"🚫 Only HOST can swap players!"); return
            swapped=[]
            reply=msg.get("reply_to_message")
            if reply and reply.get("from"):
                puid=reply["from"]["id"]; pname=reply["from"].get("first_name","?")
                for i,team in enumerate(g["teams"]):
                    if any(p[0]==puid for p in team):
                        g["teams"][i]=[p for p in team if p[0]!=puid]
                        g["teams"][1-i].append((puid,pname)); swapped.append(pname+"→"+g["team_names"][1-i])
            for puid,pname in get_entities_players(msg):
                if puid:
                    for i,team in enumerate(g["teams"]):
                        if any(p[0]==puid for p in team):
                            g["teams"][i]=[p for p in team if p[0]!=puid]
                            g["teams"][1-i].append((puid,pname)); swapped.append(pname+"→"+g["team_names"][1-i])
            send(cid,("🔄 "+", ".join(swapped)) if swapped else "Reply to member's message!")
            return

        if tl.startswith("/startmatch"):
            if not g or not is_host(g,uid): send(cid,"🚫 Only HOST can start match!"); return
            if g.get("mode")=="solo":
                if len(g.get("players",[]))<3: send(cid,"Need at least 3 players!"); return
                start_solo_game(g,cid)
            elif is_team_mode(g):
                if g.get("phase")=="joining":
                    if not g["teams"][0] or not g["teams"][1]: send(cid,"Need players in both teams!"); return
                    proceed_to_over_selection(g,cid)
                else: send(cid,"Use /startmatch during joining phase.")
            return

        if tl.startswith("/extend"):
            if not g or not is_host(g,uid): send(cid,"🚫 Only HOST can extend time!"); return
            if g.get("phase") not in ("joining","waiting"): send(cid,"Can only extend during joining!"); return
            g["join_deadline"]=(g.get("join_deadline") or time.time())+30; g["join_warned"]=False
            send(cid,"⏰ Extended by 30 seconds!")
            return

        if tl.startswith("/leave"):
            gcid=cid if chat_type!="private" else player_game.get(uid)
            g2=games.get(gcid)
            if not g2 or g2.get("phase") not in ("joining","waiting"): send(cid,"Can only leave during joining!"); return
            g2["players"]=[p for p in g2["players"] if p[0]!=uid]
            for team in g2["teams"]: team[:]=[p for p in team if p[0]!=uid]
            if uid in player_game: del player_game[uid]
            send(gcid,name+" left!")
            return

        if tl.startswith("/members"):
            gcid=cid if chat_type!="private" else player_game.get(uid)
            g2=games.get(gcid)
            if not g2: send(cid,"No game running!"); return
            txt="👥 MEMBERS\n━━━━━━━━━━━━━━━━\n"
            if is_team_mode(g2):
                for ti in range(2):
                    cap=g2["captains"][ti]
                    txt+="\n"+("🔵" if ti==0 else "🔴")+" "+g2["team_names"][ti]+" ("+str(len(g2["teams"][ti]))+"):\n"
                    for i,p in enumerate(g2["teams"][ti]):
                        crown=" 👑" if p[0]==cap else ""
                        dismissed=g2["dismissed"][ti] if g2.get("phase")=="batting" else []
                        out_mark=" ❌" if p[0] in dismissed else ""
                        txt+="  "+str(i+1)+". "+p[1]+crown+out_mark+"\n"
            else:
                for i,p in enumerate(g2.get("players",[])):
                    txt+=str(i+1)+". "+p[1]+"\n"
            txt+="\n🎮 Host: "+g2.get("host_name","?")
            send(cid,txt)
            return

        if tl.startswith("/score"):
            gcid=cid if chat_type!="private" else player_game.get(uid)
            g2=games.get(gcid)
            if not g2: send(cid,"No game!"); return
            if g2.get("phase")=="batting" and is_team_mode(g2): send_html(cid,build_full_scorecard(g2))
            else: send(cid,simple_sb(g2))
            return

        if tl.startswith("/status"):
            gcid=cid if chat_type!="private" else player_game.get(uid)
            g2=games.get(gcid)
            if not g2: send(cid,"No game!"); return
            if g2.get("phase") in ("joining","waiting","choose_cap_a","choose_cap_b","toss","waiting_host","setup_over","setup_wicket"):
                t1n=", ".join([p[1] for p in g2["teams"][0]]) or "Empty"
                t2n=", ".join([p[1] for p in g2["teams"][1]]) or "Empty"
                cap_a=next((p[1] for p in g2["teams"][0] if g2["captains"][0] and p[0]==g2["captains"][0]),"Not set")
                cap_b=next((p[1] for p in g2["teams"][1] if g2["captains"][1] and p[0]==g2["captains"][1]),"Not set")
                send(cid,"🏏 STATUS\n━━━━━━━━━━━━━━━━\n🎮 Host: "+g2.get("host_name","Not set")+"\n🔵 A("+str(len(g2["teams"][0]))+"): "+t1n+"\n👑 Cap A: "+cap_a+"\n🔴 B("+str(len(g2["teams"][1]))+"): "+t2n+"\n👑 Cap B: "+cap_b+"\nPhase: "+g2.get("phase","?")+"\n\n🔵 /join_a or 🔴 /join_b to join!")
            else: send(cid,simple_sb(g2))
            return

        if tl.startswith("/endgame"):
            if chat_type=="private": send(cid,"Use in your group!"); return
            if not g: send(cid,"No game running!"); return
            if not is_host_or_admin(g,cid,uid): send(cid,"🚫 Only host or admin can end game!"); return
            send(cid,"⚠️ Are you sure you want to END the game?",endgame_confirm_kb())
            return

        if tl.startswith("/lb") or tl.startswith("/leaderboard"): send(cid,lb_text()); return
        if tl.startswith("/glb"):
            if chat_type=="private": send(cid,"Use /glb in group!"); return
            send(cid,glb_text(cid)); return

        if tl.startswith("/rules"):
            send(cid,"🏏 Cricket Rivalry\n\n━━ COMMANDS ━━\n/newgame — Start game\n/join — Join 1v1/Solo\n/join_a /join_b — Join teams\n/leave — Leave during joining\n/score — Live scorecard\n/status — Match status\n/members — View players\n/mystats /lb /glb — Stats\n/endgame — End game (host/admin)\n\n━━ HOST ONLY ━━\n/extend — Add 30s\n/startmatch — Force start\n/toss — Do toss\n/choose_captain — Pick captains\n/change_captain — Change captains\n/change_host — Transfer host\n/swap_innings — Start innings 2\n/add_a /add_b — Add to team\n/swap — Swap between teams\n/remove_player — Remove player\n\n━━ ROLES ━━\n🎮 Host: full control\n👑 Batting captain: striker/nonstriker\n👑 Bowling captain: bowler\n🛡 Admin: /endgame only")
            return

        num=parse_num(text)
        if num is not None:
            group_cid=player_game.get(uid)
            gcid=group_cid if chat_type=="private" else cid
            g2=games.get(gcid)
            if not g2 or g2.get("phase")!="batting": return
            if g2["mode"]=="solo": batter,bowler=get_solo_bb(g2); wk="solo_wc"; bk2="solo_bc"
            else: batter=get_striker(g2); bowler=get_bowler(g2); wk="wc"; bk2="bc"
            if chat_type=="private":
                if not bowler or uid!=bowler[0]: send(cid,"You are not the current bowler!"); return
                if num==0: send(cid,"⚠️ Bowler cannot use 0! Send 1-6."); return
                if g2.get(wk) is not None: send(cid,"Already bowled!"); return
                g2[wk]=num; g2["wc"]=num
                nt=g2.get("ball_timer_token",0)+1; g2["ball_timer_token"]=nt
                send_bowl_result(bowler[0],gcid)
                send_sticker(gcid,BATTER_READY_STICKER)
                if batter: send_html(gcid,"✅ Bowler sent!\n🏏 "+mention(batter[0],batter[1])+" type 0-6!")
                t=threading.Thread(target=start_timers,args=(g2,gcid,nt,batter,bowler)); t.daemon=True; t.start()
                if g2.get(bk2) is not None:
                    g2["bc"]=g2[bk2]
                    if g2["mode"]=="solo": g2["solo_bc"]=None; g2["solo_wc"]=None
                    resolve(g2,gcid)
            else:
                if not batter or uid!=batter[0]: return
                if num==0:
                    zk=str(uid); count=g2.get("batter_zero_count",{}).get(zk,0)+1
                    g2.setdefault("batter_zero_count",{})[zk]=count
                    if count>=3:
                        g2["batter_zero_count"][zk]=0
                        send_html(gcid,"⚠️ "+mention(uid,name)+" 3 zeros in a row! Type 1-6!"); return
                else: g2.setdefault("batter_zero_count",{})[str(uid)]=0
                if g2.get(wk) is None:
                    if bowler: send_html(gcid,"⏳ Wait for "+mention(bowler[0],bowler[1])+" to bowl!"); return
                if g2.get(bk2) is not None: send(gcid,"Already played!"); return
                g2[bk2]=num; g2["bc"]=num
                nt=g2.get("ball_timer_token",0)+1; g2["ball_timer_token"]=nt
                if g2["mode"]=="solo": g2["solo_bc"]=None; g2["solo_wc"]=None
                resolve(g2,gcid)
    except Exception as e:
        print("handle_message error:",e)
        import traceback; traceback.print_exc()

def handle_callback(cb):
    try:
        cid=cb["message"]["chat"]["id"]
        mid=cb["message"]["message_id"]
        uid=cb["from"]["id"]
        qid=cb["id"]
        d=cb["data"]
        name=cb["from"].get("first_name","Player")
        g=games.get(cid)

        if d in ("join_team_a","join_team_b"):
            if not g: answer(qid,"No game!",True); return
            if g.get("phase")!="joining": answer(qid,"Joining is closed!",True); return
            if uid==g.get("host"): answer(qid,"Host cannot join a team!",True); return
            team_idx=0 if d=="join_team_a" else 1
            team_name="🔵 Team A" if team_idx==0 else "🔴 Team B"
            for i,team in enumerate(g["teams"]):
                if any(p[0]==uid for p in team):
                    if i==team_idx: answer(qid,"⚠️ Already in "+team_name+"!",True); return
                    else: answer(qid,"⚠️ Already in other team!",True); return
            g["teams"][team_idx].append((uid,name))
            if not any(p[0]==uid for p in g["players"]): g["players"].append((uid,name))
            player_game[uid]=cid
            answer(qid,"✅ Joined "+team_name+"!")
            send(cid,"✅ "+name+" joined "+team_name+"!\n🔵 A("+str(len(g["teams"][0]))+"): "+", ".join([p[1] for p in g["teams"][0]])+"\n🔴 B("+str(len(g["teams"][1]))+"): "+", ".join([p[1] for p in g["teams"][1]]))
            return

        if d=="endgame_confirm":
            if not g: answer(qid,"No game!",True); return
            if not is_host_or_admin(g,cid,uid): answer(qid,"🚫 Only host or admin!",True); return
            answer(qid); remove_buttons(cid,mid)
            cleanup_game(cid,g); send(cid,"🏁 Game ended!")
            return

        if d=="endgame_cancel":
            if not g: answer(qid,"No game!",True); return
            if not is_host_or_admin(g,cid,uid): answer(qid,"🚫 Only host or admin!",True); return
            answer(qid); remove_buttons(cid,mid)
            send(cid,"✅ Game continues!")
            return

        if d=="set_host":
            if not g: answer(qid,"No game!",True); return
            g["host"]=uid; g["host_name"]=name
            if not any(p[0]==uid for p in g["players"]): g["players"].append((uid,name))
            player_game[uid]=cid
            answer(qid); remove_buttons(cid,mid)
            send_html(cid,
                "<b>🎮 Host: "+name+"</b>\n\n"
                "━━━━━━━━━━━━━━━━\n"
                "<b>👥 PLAYERS — JOIN NOW!</b>\n\n"
                "Tap buttons below or type:\n"
                "🔵 /join_a — Join Team A\n"
                "🔴 /join_b — Join Team B\n\n"
                "━━ HOST COMMANDS ━━\n"
                "• /add_a /add_b — Add to team\n"
                "• /swap — Swap between teams\n"
                "• /remove_player — Remove player\n"
                "• /extend — Add 30s join time\n"
                "• /startmatch — Force start\n"
                "• /choose_captain — Pick captains\n"
                "• /toss — Do toss\n"
                "• /swap_innings — Start innings 2\n"
                "• /change_host — Transfer host\n"
                "• /members — View all players\n"
                "• /status — Match status\n"
                "━━━━━━━━━━━━━━━━\n"
                "⏰ 5 min join window!\n\n"
                "🔵 Team A: Empty\n"
                "🔴 Team B: Empty",
                join_team_kb()
            )
            g["phase"]="joining"; g["join_deadline"]=time.time()+300; g["join_warned"]=False
            t=threading.Thread(target=join_timer_team,args=(cid,)); t.daemon=True; t.start()
            return

        if d.startswith("cap_a_"):
            if not g: return
            if not is_host(g,uid): answer(qid,"🚫 Only HOST!",True); return
            idx=int(d.split("_")[2])
            if 0<=idx<len(g["teams"][0]):
                cap=g["teams"][0][idx]; g["captains"][0]=cap[0]
                answer(qid); remove_buttons(cid,mid)
                send_html(cid,"✅ Team A Captain: "+mention(cap[0],cap[1])+"\n\nNow choose Team B Captain:",cap_b_kb(g["teams"]))
                g["phase"]="choose_cap_b"
            return

        if d.startswith("cap_b_"):
            if not g: return
            if not is_host(g,uid): answer(qid,"🚫 Only HOST!",True); return
            idx=int(d.split("_")[2])
            if 0<=idx<len(g["teams"][1]):
                cap=g["teams"][1][idx]; g["captains"][1]=cap[0]
                answer(qid); remove_buttons(cid,mid)
                cap_a_uid=g["captains"][0]
                cap_a_name=next((p[1] for p in g["teams"][0] if p[0]==cap_a_uid),"Captain A") if cap_a_uid else "?"
                g["phase"]="toss"
                send_html(cid,
                    "✅ Captains Set!\n👑 Team A: "+cap_a_name+"\n👑 Team B: "+cap[1]+"\n\n"
                    "🪙 TOSS TIME!\n"+mention(cap_a_uid,cap_a_name)+" (Team A) calls the toss!",
                    toss_kb()
                )
            return

        if d.startswith("chcap_a_"):
            if not g: return
            if not is_host(g,uid): answer(qid,"🚫 Only HOST!",True); return
            idx=int(d.split("_")[2])
            if 0<=idx<len(g["teams"][0]):
                cap=g["teams"][0][idx]; g["captains"][0]=cap[0]
                answer(qid); remove_buttons(cid,mid)
                send_html(cid,"✅ Team A Captain: "+mention(cap[0],cap[1]),change_cap_b_kb(g["teams"]))
            return

        if d.startswith("chcap_b_"):
            if not g: return
            if not is_host(g,uid): answer(qid,"🚫 Only HOST!",True); return
            idx=int(d.split("_")[2])
            if 0<=idx<len(g["teams"][1]):
                cap=g["teams"][1][idx]; g["captains"][1]=cap[0]
                answer(qid); remove_buttons(cid,mid)
                send_html(cid,"✅ Team B Captain: "+mention(cap[0],cap[1]))
            return

        if d.startswith("bat_uid_"):
            if not g or g.get("phase")!="batting": answer(qid,"Not batting phase!",True); return
            bi=g["batting"]; cap=g["captains"][bi]
            if uid!=cap and not is_host(g,uid): answer(qid,"🚫 Only BATTING CAPTAIN or HOST!",True); return
            chosen_uid=int(d.split("bat_uid_")[1])
            dismissed=g["dismissed"][bi]
            if chosen_uid in dismissed: answer(qid,"This player is OUT!",True); return
            chosen=next((p for p in g["teams"][bi] if p[0]==chosen_uid),None)
            if not chosen: answer(qid,"Player not found!",True); return
            init_bat_stats(g,chosen[0],chosen[1])
            g["striker"]=chosen[0]; g["waiting_striker"]=False
            answer(qid); remove_buttons(cid,mid)
            send_html(cid,"✅ Striker: "+mention(chosen[0],chosen[1]))
            ask_batter_inline(g,cid,for_nonstriker=True)
            return

        if d.startswith("ns_uid_"):
            if not g or g.get("phase")!="batting": answer(qid,"Not batting phase!",True); return
            bi=g["batting"]; cap=g["captains"][bi]
            if uid!=cap and not is_host(g,uid): answer(qid,"🚫 Only BATTING CAPTAIN or HOST!",True); return
            chosen_uid=int(d.split("ns_uid_")[1])
            dismissed=g["dismissed"][bi]
            if chosen_uid in dismissed: answer(qid,"This player is OUT!",True); return
            striker=get_striker(g)
            if striker and chosen_uid==striker[0]: answer(qid,"Already the striker!",True); return
            chosen=next((p for p in g["teams"][bi] if p[0]==chosen_uid),None)
            if not chosen: answer(qid,"Player not found!",True); return
            init_bat_stats(g,chosen[0],chosen[1])
            g["non_striker"]=chosen[0]; g["waiting_nonstriker"]=False
            answer(qid); remove_buttons(cid,mid)
            send_html(cid,"✅ Non-striker: "+mention(chosen[0],chosen[1]))
            if not g.get("waiting_striker") and not g.get("waiting_bowler"):
                next_ball_msg(g,cid)
            return

        if d.startswith("bowl_uid_"):
            if not g or g.get("phase")!="batting": answer(qid,"Not batting phase!",True); return
            wi=g["bowling"]; cap=g["captains"][wi]
            if uid!=cap and not is_host(g,uid): answer(qid,"🚫 Only BOWLING CAPTAIN or HOST!",True); return
            chosen_uid=int(d.split("bowl_uid_")[1])
            last=g.get("last_bowler"); team=g["teams"][wi]
            if len(team)>1 and chosen_uid==last: answer(qid,"⚠️ Same bowler cannot bowl 2 overs in a row!",True); return
            chosen=next((p for p in team if p[0]==chosen_uid),None)
            if not chosen: answer(qid,"Player not found!",True); return
            init_bowl_stats(g,chosen[0],chosen[1])
            g["current_bowler"]=chosen[0]; g["over_bowler_locked"]=True; g["waiting_bowler"]=False
            answer(qid); remove_buttons(cid,mid)
            send_html(cid,"✅ Bowler: "+mention(chosen[0],chosen[1])+" — this over!")
            if not g.get("waiting_striker") and not g.get("waiting_nonstriker"):
                next_ball_msg(g,cid)
            return

        if d.startswith("mode_"):
            mode=d.split("_")[1]
            if mode=="test":
                if cid in games: answer(qid,"Game running!",True); return
                answer(qid); remove_buttons(cid,mid)
                send(cid,"🏟️ Test Match — Choose format:",test_type_kb()); return
            if mode=="team":
                g=new_game("team"); g["creator"]=uid; g["host_name"]=name
                g["players"].append((uid,name)); player_game[uid]=cid
                games[cid]=g
                answer(qid); remove_buttons(cid,mid)
                send_html(cid,"<b>👥 TEAM MATCH</b>\n━━━━━━━━━━━━━━━━\n\nWho will host?\n(Anyone can tap)",host_kb())
                return
            g=new_game(mode); g["creator"]=uid; g["host_name"]=name
            g["players"].append((uid,name)); player_game[uid]=cid
            games[cid]=g
            answer(qid); remove_buttons(cid,mid)
            if mode=="solo": send(cid,"🏆 SOLO TOURNAMENT\n\nChoose overs:",over_kb())
            else: send(cid,"⚔️ 1v1 RIVALRY\n\nChoose overs:",over_kb())
            return

        if d.startswith("test_"):
            test_type=d.split("_")[1]
            g=new_game("test",test_type); g["creator"]=uid; g["host_name"]=name
            g["players"].append((uid,name)); player_game[uid]=cid
            games[cid]=g
            answer(qid); remove_buttons(cid,mid)
            if test_type=="team": send_html(cid,"<b>🏟️ TEAM TEST MATCH</b>\n\nWho will host?",host_kb())
            else: send(cid,"🏟️ 1v1 TEST MATCH\n\nChoose overs:",over_kb())
            return

        if not g: return

        if d.startswith("over_") and g.get("phase") in ("setup_over","setup_over_after_toss"):
            if not is_host(g,uid): answer(qid,"Only host!",True); return
            val=d.split("_")[1]
            if val=="inf": g["overs"]=999; g["infinity_overs"]=True
            else: g["overs"]=int(val); g["infinity_overs"]=False
            answer(qid); remove_buttons(cid,mid)
            ov="♾️" if g["infinity_overs"] else str(g["overs"])
            if g.get("phase")=="setup_over_after_toss":
                w_cap=g["captains"][g["toss_winner"]]
                wname=next((p[1] for p in g["teams"][g["toss_winner"]] if p[0]==w_cap),g["team_names"][g["toss_winner"]]) if w_cap else g["team_names"][g["toss_winner"]]
                send_html(cid,"✅ Overs: "+ov+"\n\n"+mention(w_cap,wname)+" choose Bat or Bowl:",bat_bowl_kb())
                g["phase"]="toss_choice"; return
            if g["mode"]=="solo":
                g["phase"]="waiting"; g["join_deadline"]=time.time()+120
                send(cid,"✅ Overs: "+ov+"\n\nPlayers join! (min 3)\n/join\n\n/extend for more time\n/startmatch when ready!")
                t=threading.Thread(target=join_timer_solo,args=(cid,)); t.daemon=True; t.start()
            elif g["mode"] in ("1v1","test") and g.get("test_type")!="team":
                g["phase"]="setup_wicket"
                send(cid,"✅ Overs: "+ov+"\n\nChoose wickets:",wicket_kb())
            elif is_team_mode(g):
                if g["teams"][0] and g["teams"][1]:
                    g["phase"]="choose_cap_a"
                    send(cid,"✅ Overs: "+ov+"\n\n👑 Choose Team A Captain:",cap_a_kb(g["teams"]))
                else:
                    send(cid,"✅ Overs: "+ov+"\n\nAdd players then /startmatch")
            return

        if d.startswith("wkt_") and g.get("phase")=="setup_wicket":
            if not is_host(g,uid): answer(qid,"Only host!",True); return
            g["max_wickets"]=int(d.split("_")[1])
            answer(qid); remove_buttons(cid,mid)
            ov="♾️" if g["infinity_overs"] else str(g.get("overs",0))
            g["phase"]="waiting"; g["join_deadline"]=time.time()+120
            label="🏟️ Test" if g["mode"]=="test" else "⚔️ 1v1"
            send(cid,label+"\n✅ Overs: "+ov+" | Wickets: "+str(g["max_wickets"])+"\n\nWaiting for opponent (2 min)\n/join\n\n/extend to add 30s")
            t=threading.Thread(target=join_timer,args=(cid,)); t.daemon=True; t.start()
            return

        if d in ("toss_heads","toss_tails") and g.get("phase")=="toss":
            if is_team_mode(g): caller=g["captains"][0]
            else: caller=g["players"][0][0] if g.get("players") else None
            if caller and uid!=caller: answer(qid,"🚫 Only Team A Captain calls toss!",True); return
            coin=random.choice(["heads","tails"]); called=d.split("_")[1]; won=coin==called
            answer(qid); remove_buttons(cid,mid)
            g["toss_winner"]=0 if won else 1
            if is_team_mode(g):
                w_cap=g["captains"][g["toss_winner"]]
                wname=next((p[1] for p in g["teams"][g["toss_winner"]] if p[0]==w_cap),g["team_names"][g["toss_winner"]]) if w_cap else g["team_names"][g["toss_winner"]]
                w_cap_id=w_cap
            else:
                wname=g["players"][g["toss_winner"]][1] if g["toss_winner"]<len(g["players"]) else "?"
                w_cap_id=g["players"][g["toss_winner"]][0] if g["toss_winner"]<len(g["players"]) else None
            result_msg="🪙 Coin: <b>"+coin.upper()+"</b>!\n<b>"+wname+"</b> won the toss!\n\n"
            if is_team_mode(g):
                if not g.get("overs"):
                    send_html(cid,result_msg+mention(g.get("host"),g.get("host_name","Host"))+" choose overs:",over_kb_team())
                    g["phase"]="setup_over_after_toss"
                else:
                    send_html(cid,result_msg+mention(w_cap_id,wname)+" choose Bat or Bowl:",bat_bowl_kb())
                    g["phase"]="toss_choice"
            else:
                send_html(cid,result_msg+mention(w_cap_id,wname)+" choose:",bat_bowl_kb())
                g["phase"]="toss_choice"
            return

        if d in ("choice_bat","choice_bowl") and g.get("phase")=="toss_choice":
            w=g.get("toss_winner",0)
            if is_team_mode(g): chooser=g["captains"][w]
            else: chooser=g["players"][w][0] if w<len(g.get("players",[])) else None
            if chooser and uid!=chooser: answer(qid,"🚫 Not your choice!",True); return
            if d=="choice_bat": g["batting"]=w; g["bowling"]=1-w
            else: g["bowling"]=w; g["batting"]=1-w
            g["phase"]="batting"; answer(qid); remove_buttons(cid,mid)
            bi=g["batting"]; wi=g["bowling"]
            bat_name=g["team_names"][bi] if is_team_mode(g) else (g["players"][bi][1] if bi<len(g["players"]) else "?")
            bowl_name=g["team_names"][wi] if is_team_mode(g) else (g["players"][wi][1] if wi<len(g["players"]) else "?")
            ov="♾️" if g.get("infinity_overs") else str(g.get("overs",0))
            send_sticker(cid,START_STICKER)
            if is_team_mode(g):
                max_wk=max_wkts_for_team(g,bi)
                txt=("🏏 MATCH STARTS!\n━━━━━━━━━━━━━━━━\n"
                     "Overs: "+ov+" | Wickets: "+str(max_wk)+"\n\n"
                     "🏏 BATTING: "+bat_name+"\n"+squad_text(g,bi)+"\n"
                     "⚾ BOWLING: "+bowl_name+"\n"+squad_text(g,wi))
                send(cid,txt)
                cap_bat=g["captains"][bi]; cap_bowl=g["captains"][wi]
                g["waiting_striker"]=True; g["waiting_nonstriker"]=True; g["waiting_bowler"]=True
                if cap_bat:
                    cbn=next((p[1] for p in g["teams"][bi] if p[0]==cap_bat),"Captain")
                    send_html(cid,"👑 "+mention(cap_bat,cbn)+" choose STRIKER:",batter_kb(g,bi,False))
                else:
                    send_html(cid,"👑 Host choose STRIKER:",batter_kb(g,bi,False))
                if cap_bowl:
                    cwn=next((p[1] for p in g["teams"][wi] if p[0]==cap_bowl),"Captain")
                    send_html(cid,"👑 "+mention(cap_bowl,cwn)+" choose opening BOWLER:",bowler_kb(g))
                else:
                    send_html(cid,"👑 Host choose opening BOWLER:",bowler_kb(g))
            else:
                send(cid,"🏏 MATCH STARTS!\n━━━━━━━━━━━━━━━━\n🏏 "+bat_name+" BATS\n⚾ "+bowl_name+" BOWLS\nOvers: "+ov)
                next_ball_msg(g,cid)
            return

        if d in ("followon_yes","followon_no"):
            if not is_host(g,uid): answer(qid,"Only host!",True); return
            answer(qid); remove_buttons(cid,mid)
            bi=g["batting"]
            if d=="followon_yes":
                send(cid,"📋 Follow-On enforced!")
                g["test_innings_num"]=3; g["innings"]=3
                g["balls"]=0; g["wickets"]=[0,0]; g["scores"]=[0,0]
                g["current_over_runs"]=0; g["ball_log"]=[]; g["last_bowler"]=None
                g["dismissed"]=[[],[]]; g["waiting_striker"]=False; g["waiting_nonstriker"]=False; g["waiting_bowler"]=False
                g["consecutive_miss"]=0; g["player_bat_stats"]={}; g["player_bowl_stats"]={}
                send_sticker(cid,INNINGS_STICKER)
                nm=g["players"][bi][1] if bi<len(g["players"]) else "?"
                send(cid,"🏟️ FOLLOW-ON — INN 3!\n"+nm+" bats again!\n"+simple_sb(g))
                next_ball_msg(g,cid)
            else:
                send(cid,"Follow-On skipped.")
                g["test_innings_num"]=3; g["innings"]=3
                g["batting"],g["bowling"]=g["bowling"],g["batting"]
                g["balls"]=0; g["wickets"]=[0,0]; g["scores"]=[0,0]
                g["current_over_runs"]=0; g["ball_log"]=[]; g["last_bowler"]=None
                g["dismissed"]=[[],[]]; g["waiting_striker"]=False; g["waiting_nonstriker"]=False; g["waiting_bowler"]=False
                g["consecutive_miss"]=0; g["player_bat_stats"]={}; g["player_bowl_stats"]={}
                send_sticker(cid,INNINGS_STICKER)
                send(cid,"🏟️ TEST — INN 3!\n"+simple_sb(g))
                next_ball_msg(g,cid)
            return

    except Exception as e:
        print("handle_callback error:",e)
        import traceback; traceback.print_exc()

# ================================================================
# MAIN LOOP
# ================================================================

init_db()
print("✅ Database ready!")
print("🏏 Bot running! Username: Cricketrivalrybot")

while True:
    try:
        updates=poll()
        for u in updates:
            offset=u["update_id"]+1
            if "message" in u: handle_message(u["message"])
            elif "callback_query" in u: handle_callback(u["callback_query"])
    except Exception as e:
        print("Main loop error:",e)
        import traceback; traceback.print_exc()
        time.sleep(5)

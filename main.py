from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import math, os, hashlib, io
from datetime import datetime

app = Flask(__name__)

THEMES = {
    "teal":   {"bg": (8,16,38),   "ac": (0,212,170),  "ac2": (0,255,153)},
    "purple": {"bg": (10,10,26),  "ac": (124,58,237), "ac2": (167,139,250)},
    "green":  {"bg": (8,20,10),   "ac": (0,204,85),   "ac2": (0,255,102)},
    "amber":  {"bg": (30,12,0),   "ac": (251,191,36), "ac2": (234,150,20)},
    "red":    {"bg": (35,5,5),    "ac": (239,68,68),  "ac2": (220,50,50)},
    "blue":   {"bg": (5,10,40),   "ac": (59,130,246), "ac2": (96,165,250)},
}

ICONS = {
    "tip":"🔐","career":"🌍","english":"🇬🇧","ctf":"⚡",
    "tool":"🛠","story":"☠️","quiz":"🧠","poll":"📊",
    "news":"📰","challenge":"🏆","default":"🛡"
}

def fnt(size, bold=False):
    try:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def make_image(title, subtitle, theme_name, post_type, platform="telegram"):
    W = H = 1080
    t = THEMES.get(theme_name, THEMES["teal"])
    bg, ac, ac2 = t["bg"], t["ac"], t["ac2"]
    bot = tuple(max(0,c-20) for c in bg)

    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # Gradient background
    for y in range(H):
        r = int(bg[0]+(bot[0]-bg[0])*y/H)
        g = int(bg[1]+(bot[1]-bg[1])*y/H)
        b = int(bg[2]+(bot[2]-bg[2])*y/H)
        d.line([(0,y),(W,y)], fill=(r,g,b))

    # Grid
    for x in range(0,W,80): d.line([(x,0),(x,H)], fill=(*ac,6))
    for y in range(0,H,80): d.line([(0,y),(W,y)], fill=(*ac,6))

    # Glow circles
    for r,a in [(300,6),(220,11),(140,18),(80,30)]:
        d.ellipse([W//2-r,200-r,W//2+r,200+r], outline=(*ac,a), width=2)

    # Corner dots
    for cx,cy in [(55,55),(W-55,55),(55,H-55),(W-55,H-55)]:
        d.ellipse([cx-6,cy-6,cx+6,cy+6], fill=(*ac,180))
        d.ellipse([cx-14,cy-14,cx+14,cy+14], outline=(*ac,50), width=1)

    # Platform badge
    pc = {"telegram":(0,136,204),"instagram":(193,53,132),"tiktok":(254,44,85),"youtube":(255,0,0)}.get(platform,(80,80,80))
    d.rounded_rectangle([W-185,28,W-28,76], radius=18, fill=(*pc,200))
    d.text((W-106,52), platform.upper(), font=fnt(20,True), fill=(255,255,255), anchor="mm")

    # Divider top
    d.line([(100,318),(W-100,318)], fill=(*ac,70), width=2)

    # Title
    title_u = title.upper()
    words = title_u.split()
    if len(words) <= 2:
        d.text((W//2,420), title_u, font=fnt(90,True), fill=(255,255,255), anchor="mm")
    elif len(words) <= 4:
        d.text((W//2,385), " ".join(words[:2]), font=fnt(78,True), fill=(255,255,255), anchor="mm")
        d.text((W//2,478), " ".join(words[2:]), font=fnt(78,True), fill=(*ac2,255), anchor="mm")
    else:
        d.text((W//2,390), " ".join(words[:3]), font=fnt(68,True), fill=(255,255,255), anchor="mm")
        d.text((W//2,470), " ".join(words[3:]), font=fnt(68,True), fill=(*ac2,255), anchor="mm")

    # Subtitle
    if subtitle:
        d.line([(100,545),(W-100,545)], fill=(*ac,40), width=1)
        words_sub = subtitle.split()
        line, lines = "", []
        for w in words_sub:
            test = (line+" "+w).strip()
            if d.textbbox((0,0),test,font=fnt(32))[2] <= W-200: line=test
            else:
                if line: lines.append(line)
                line=w
        if line: lines.append(line)
        sy = 580
        for sl in lines[:2]:
            d.text((W//2,sy), sl, font=fnt(32), fill=(*ac2,200), anchor="mm")
            sy += 46

    # Bottom strip
    d.rounded_rectangle([55,915,W-55,1005], radius=18, fill=(*ac,22), outline=(*ac,65), width=1)
    d.text((W//2,960), "t.me/ZirxUz  •  IT & Cybersecurity  •  O'zbek tilida",
           font=fnt(24), fill=(*ac,200), anchor="mm")

    # Brand & date
    d.text((68,H-46), "ZIRX", font=fnt(24,True), fill=(*ac,170))
    d.text((W-68,H-46), datetime.now().strftime("%d.%m.%Y"), font=fnt(22), fill=(100,120,140), anchor="ra")

    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    buf.seek(0)
    return buf

@app.route("/health")
def health():
    return jsonify({"status":"ok","service":"Zirx Image Server v1.0"})

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json or {}
    buf = make_image(
        title    = data.get("title","ZIRX IT"),
        subtitle = data.get("subtitle",""),
        theme_name = data.get("theme","teal"),
        post_type  = data.get("post_type","default"),
        platform   = data.get("platform","telegram")
    )
    return send_file(buf, mimetype="image/png",
                     download_name="post.png", as_attachment=False)

@app.route("/")
def index():
    return jsonify({
        "name": "Zirx Image Server",
        "endpoints": {
            "POST /generate": "Rasm yaratish",
            "GET /health": "Server holati"
        },
        "usage": {
            "title": "POST SARLAVHA",
            "subtitle": "kichik yozuv",
            "theme": "teal|purple|green|amber|red|blue",
            "post_type": "tip|career|english|ctf|tool|quiz|poll|challenge",
            "platform": "telegram|instagram|tiktok|youtube"
        }
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

import json
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DATA = Path(sys.argv[1])
OUT = Path("public")
OUT.mkdir(exist_ok=True)

with DATA.open(encoding="utf-8") as f:
    data = json.load(f)

weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

# Keep the last 52 weeks so the animation matches the familiar GitHub calendar.
weeks = weeks[-52:]

counts = []
for week in weeks:
    counts.append([d["contributionCount"] for d in week["contributionDays"]])

max_count = max((v for w in counts for v in w), default=1)

# GitHub-like compact calendar.
CELL = 12
GAP = 4
LEFT = 58
TOP = 70
GRID_W = len(weeks) * (CELL + GAP)
GRID_H = 7 * (CELL + GAP)
WIDTH = max(900, LEFT + GRID_W + 30)
HEIGHT = TOP + GRID_H + 70

BG = (13, 17, 23)
TEXT = (201, 209, 217)
MUTED = (139, 148, 158)

# Green contribution levels.
LEVELS = [
    (22, 27, 34),
    (14, 68, 41),
    (25, 109, 57),
    (46, 160, 67),
    (86, 211, 100),
]

try:
    font = ImageFont.truetype("DejaVuSans.ttf", 13)
    small = ImageFont.truetype("DejaVuSans.ttf", 11)
except:
    font = small = ImageFont.load_default()

def level(n):
    if n <= 0:
        return 0
    ratio = n / max_count
    if ratio < .20:
        return 1
    if ratio < .45:
        return 2
    if ratio < .70:
        return 3
    return 4

def draw_dragon(draw, x, y, scale=1.0, flip=False, fire=False):
    # Stylized dragon silhouette, drawn directly in Pillow so no external asset is required.
    s = scale
    direction = -1 if flip else 1

    def P(px, py):
        return (x + direction * px * s, y + py * s)

    # Tail
    draw.line([P(-65, 20), P(-105, 7), P(-132, 18), P(-150, 3)], fill=(90, 22, 18), width=max(2, int(5*s)))
    # Body
    draw.ellipse([P(-55, -5), P(50, 42)], fill=(55, 28, 25), outline=(150, 62, 36), width=max(1, int(2*s)))
    # Neck
    draw.polygon([P(25, 20), P(65, -35), P(88, -55), P(72, 8)], fill=(66, 30, 27))
    # Head
    draw.polygon([P(70, -55), P(105, -62), P(122, -45), P(105, -25), P(73, -31)], fill=(76, 32, 27))
    # Horns
    draw.polygon([P(83, -57), P(76, -78), P(91, -61)], fill=(115, 71, 49))
    draw.polygon([P(101, -58), P(110, -78), P(113, -50)], fill=(115, 71, 49))
    # Wings
    draw.polygon([P(10, 2), P(-5, -72), P(38, -40), P(64, -82), P(56, 10)], fill=(42, 25, 28), outline=(120, 48, 36))
    draw.polygon([P(-5, -72), P(12, -18), P(38, -40)], outline=(150, 58, 38), width=max(1, int(2*s)))
    # Legs
    for lx in (-25, 18):
        draw.line([P(lx, 30), P(lx-5, 57), P(lx-15, 62)], fill=(72, 33, 28), width=max(2, int(4*s)))
        draw.line([P(lx, 30), P(lx+8, 55), P(lx+17, 59)], fill=(72, 33, 28), width=max(2, int(4*s)))
    # Eye
    draw.ellipse([P(103, -49), P(108, -44)], fill=(255, 196, 0))
    # Fire
    if fire:
        fx = 135 if not flip else -135
        fy = -43
        sign = 1 if not flip else -1
        flame = [
            P(fx, fy),
            P(fx + sign*35, fy-12),
            P(fx + sign*58, fy),
            P(fx + sign*35, fy+9),
            P(fx + sign*62, fy+20),
            P(fx + sign*18, fy+15),
        ]
        draw.polygon(flame, fill=(255, 115, 25))
        inner = [
            P(fx, fy+1),
            P(fx + sign*23, fy-3),
            P(fx + sign*39, fy+4),
            P(fx + sign*20, fy+11),
        ]
        draw.polygon(inner, fill=(255, 225, 82))

def frame(frame_no):
    im = Image.new("RGB", (WIDTH, HEIGHT), BG)
    d = ImageDraw.Draw(im)

    d.text((25, 22), "MY GITHUB CONTRIBUTIONS", font=font, fill=TEXT)
    d.text((25, 43), "COMMIT  •  LEARN  •  BUILD  •  REPEAT", font=small, fill=MUTED)

    # Month labels (approximate positions).
    for i, name in enumerate(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]):
        x = LEFT + int(i * GRID_W / 12)
        d.text((x, TOP-22), name, font=small, fill=MUTED)

    # Weekday labels.
    for day, name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        d.text((8, TOP + day*(CELL+GAP)-1), name, font=small, fill=MUTED)

    # Contribution cells.
    for wi, week in enumerate(counts):
        for di, n in enumerate(week):
            x = LEFT + wi*(CELL+GAP)
            y = TOP + di*(CELL+GAP)
            col = LEVELS[level(n)]
            d.rounded_rectangle([x, y, x+CELL, y+CELL], radius=2, fill=col)

    # Animated dragon flies across the calendar.
    travel = WIDTH + 180
    x = -150 + (frame_no / 39.0) * travel
    y = TOP + GRID_H/2 - 5 + math.sin(frame_no/4.5) * 28
    fire = frame_no % 4 in (0, 1)
    draw_dragon(d, x, y, scale=0.75, flip=False, fire=fire)

    d.text((25, HEIGHT-32), "Aditya Kumar  •  github.com/adityakumar5492", font=small, fill=MUTED)
    return im

frames = [frame(i) for i in range(40)]
frames[0].save(
    OUT / "dragon-contribution.gif",
    save_all=True,
    append_images=frames[1:],
    duration=90,
    loop=0,
    optimize=True,
)
print("Generated", OUT / "dragon-contribution.gif")


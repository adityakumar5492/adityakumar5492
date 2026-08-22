import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# =========================================================
# INPUT / OUTPUT
# =========================================================

DATA = Path(sys.argv[1])
OUT = Path("public")
OUT.mkdir(exist_ok=True)

with DATA.open(encoding="utf-8") as f:
    data = json.load(f)

weeks = data["data"]["user"]["contributionsCollection"][
    "contributionCalendar"
]["weeks"]

weeks = weeks[-52:]


# =========================================================
# CONTRIBUTION DATA
# =========================================================

counts = []

for week in weeks:
    days = week["contributionDays"]
    counts.append([day["contributionCount"] for day in days])

# Make sure every week has 7 cells
for week in counts:
    while len(week) < 7:
        week.append(0)

max_count = max(
    (value for week in counts for value in week),
    default=1
)


# =========================================================
# CANVAS
# =========================================================

CELL = 12
GAP = 3

LEFT = 55
TOP = 55

GRID_W = 52 * (CELL + GAP)
GRID_H = 7 * (CELL + GAP)

WIDTH = LEFT + GRID_W + 25
HEIGHT = TOP + GRID_H + 55

BG = (13, 17, 23)
TEXT = (201, 209, 217)
MUTED = (139, 148, 158)

LEVELS = [
    (22, 27, 34),
    (14, 68, 41),
    (25, 109, 57),
    (46, 160, 67),
    (86, 211, 100),
]


# =========================================================
# FONTS
# =========================================================

try:
    font = ImageFont.truetype("DejaVuSans.ttf", 13)
    small = ImageFont.truetype("DejaVuSans.ttf", 10)
except:
    font = ImageFont.load_default()
    small = font


# =========================================================
# CONTRIBUTION LEVEL
# =========================================================

def get_level(value):

    if value <= 0:
        return 0

    ratio = value / max_count

    if ratio < 0.20:
        return 1

    if ratio < 0.45:
        return 2

    if ratio < 0.70:
        return 3

    return 4


# =========================================================
# DRAW DRAGON
# =========================================================

def draw_dragon(draw, cx, cy, direction=1, fire=True):

    # Very small dragon designed specifically
    # to fit inside a GitHub contribution cell.

    # Scale
    s = 0.55

    def P(x, y):
        return (
            cx + direction * x * s,
            cy + y * s
        )

    # -----------------------------------------------------
    # Tail
    # -----------------------------------------------------

    draw.line(
        [
            P(-5, 2),
            P(-9, 1),
            P(-13, 3),
        ],
        fill=(125, 45, 30),
        width=2
    )

    # -----------------------------------------------------
    # Body
    # -----------------------------------------------------

    draw.ellipse(
        [
            P(-7, -4),
            P(7, 5)
        ],
        fill=(105, 42, 30)
    )

    # -----------------------------------------------------
    # Neck
    # -----------------------------------------------------

    draw.line(
        [
            P(4, -1),
            P(8, -7),
            P(11, -10)
        ],
        fill=(125, 48, 32),
        width=3
    )

    # -----------------------------------------------------
    # Head
    # -----------------------------------------------------

    draw.ellipse(
        [
            P(9, -13),
            P(18, -7)
        ],
        fill=(145, 52, 32)
    )

    # -----------------------------------------------------
    # Horn
    # -----------------------------------------------------

    draw.polygon(
        [
            P(12, -12),
            P(11, -17),
            P(14, -13)
        ],
        fill=(180, 110, 60)
    )

    # -----------------------------------------------------
    # Wing
    # -----------------------------------------------------

    draw.polygon(
        [
            P(0, -2),
            P(-5, -13),
            P(4, -9),
            P(9, -15),
            P(8, -2)
        ],
        fill=(75, 30, 29),
        outline=(150, 55, 38)
    )

    # -----------------------------------------------------
    # Legs
    # -----------------------------------------------------

    draw.line(
        [
            P(-3, 4),
            P(-5, 9)
        ],
        fill=(110, 42, 30),
        width=2
    )

    draw.line(
        [
            P(4, 4),
            P(6, 9)
        ],
        fill=(110, 42, 30),
        width=2
    )

    # -----------------------------------------------------
    # Eye
    # -----------------------------------------------------

    draw.ellipse(
        [
            P(15, -11),
            P(17, -9)
        ],
        fill=(255, 210, 60)
    )

    # -----------------------------------------------------
    # Fire
    # -----------------------------------------------------

    if fire:

        fx = 20 * direction

        draw.polygon(
            [
                P(fx, -10),
                P(fx + 7 * direction, -8),
                P(fx + 11 * direction, -5),
                P(fx + 7 * direction, -3),
                P(fx + 13 * direction, 0),
                P(fx + 4 * direction, -1),
            ],
            fill=(255, 100, 20)
        )

        draw.polygon(
            [
                P(fx, -8),
                P(fx + 5 * direction, -6),
                P(fx + 8 * direction, -4),
                P(fx + 3 * direction, -3),
            ],
            fill=(255, 220, 70)
        )


# =========================================================
# CREATE SNAKE-LIKE PATH
# =========================================================

path = []

for week_index in range(52):

    if week_index % 2 == 0:

        # left -> right
        for day_index in range(7):
            path.append((week_index, day_index))

    else:

        # right -> left
        for day_index in range(6, -1, -1):
            path.append((week_index, day_index))


# =========================================================
# CELL CENTER
# =========================================================

def cell_position(week_index, day_index):

    x = (
        LEFT
        + week_index * (CELL + GAP)
        + CELL / 2
    )

    y = (
        TOP
        + day_index * (CELL + GAP)
        + CELL / 2
    )

    return x, y


# =========================================================
# DRAW FRAME
# =========================================================

def create_frame(frame_number):

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        BG
    )

    draw = ImageDraw.Draw(image)

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    draw.text(
        (18, 18),
        "MY GITHUB CONTRIBUTIONS",
        font=font,
        fill=TEXT
    )

    draw.text(
        (18, 36),
        "BUILD • LEARN • COMMIT • REPEAT",
        font=small,
        fill=MUTED
    )

    # -----------------------------------------------------
    # Month labels
    # -----------------------------------------------------

    months = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    for i, month in enumerate(months):

        x = LEFT + int(
            i * GRID_W / 12
        )

        draw.text(
            (x, TOP - 16),
            month,
            font=small,
            fill=MUTED
        )

    # -----------------------------------------------------
    # Weekday labels
    # -----------------------------------------------------

    for day, name in [
        (1, "Mon"),
        (3, "Wed"),
        (5, "Fri")
    ]:

        y = TOP + day * (CELL + GAP)

        draw.text(
            (8, y),
            name,
            font=small,
            fill=MUTED
        )

    # -----------------------------------------------------
    # Contribution grid
    # -----------------------------------------------------

    for wi in range(52):

        for di in range(7):

            value = 0

            if wi < len(counts):
                if di < len(counts[wi]):
                    value = counts[wi][di]

            color = LEVELS[get_level(value)]

            x = LEFT + wi * (CELL + GAP)
            y = TOP + di * (CELL + GAP)

            draw.rounded_rectangle(
                [
                    x,
                    y,
                    x + CELL,
                    y + CELL
                ],
                radius=2,
                fill=color
            )

    # =====================================================
    # DRAGON MOVEMENT
    # =====================================================

    # Move one cell at a time.
    # This keeps the dragon INSIDE the calendar.

    speed = 2

    current_index = (
        frame_number * speed
    ) % len(path)

    week, day = path[current_index]

    # Direction of movement
    if week % 2 == 0:
        direction = 1
    else:
        direction = -1

    cx, cy = cell_position(
        week,
        day
    )

    # Tiny vertical floating effect
    cy += math.sin(
        frame_number / 2
    ) * 1.2

    # Alternate fire animation
    fire = (
        frame_number % 4
        in [0, 1]
    )

    draw_dragon(
        draw,
        cx,
        cy,
        direction=direction,
        fire=fire
    )

    # =====================================================
    # FOOTER
    # =====================================================

    draw.text(
        (18, HEIGHT - 25),
        "Aditya Kumar  •  github.com/adityakumar5492",
        font=small,
        fill=MUTED
    )

    return image


# =========================================================
# GENERATE ANIMATION
# =========================================================

frames = []

TOTAL_FRAMES = len(path) // 2

for i in range(TOTAL_FRAMES):

    frames.append(
        create_frame(i)
    )


# =========================================================
# SAVE GIF
# =========================================================

output_file = OUT / "dragon-contribution.gif"

frames[0].save(
    output_file,
    save_all=True,
    append_images=frames[1:],
    duration=120,
    loop=0,
    optimize=True
)

print(
    f"Generated {output_file}"
)

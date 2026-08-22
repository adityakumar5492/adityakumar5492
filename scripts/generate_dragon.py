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
weeks = weeks[-52:]

counts = [
    [day["contributionCount"] for day in week["contributionDays"]]
    for week in weeks
]

max_count = max(
    (value for week in counts for value in week),
    default=1
)

# -----------------------------
# Canvas
# -----------------------------

CELL = 12
GAP = 4

LEFT = 58
TOP = 70

GRID_W = len(weeks) * (CELL + GAP)
GRID_H = 7 * (CELL + GAP)

WIDTH = max(900, LEFT + GRID_W + 40)
HEIGHT = TOP + GRID_H + 70

BG = (13, 17, 23)
TEXT = (230, 237, 243)
MUTED = (139, 148, 158)

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
    font = ImageFont.load_default()
    small = ImageFont.load_default()


def contribution_level(value):
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


# -----------------------------
# Dragon
# -----------------------------

def draw_dragon(draw, cx, cy, scale=1.0, fire=True):
    """
    Detailed stylized flying dragon.
    Dragon is intentionally kept inside the canvas.
    """

    def p(x, y):
        return (
            cx + x * scale,
            cy + y * scale
        )

    outline = (105, 32, 32)
    dark_red = (58, 20, 24)
    red = (115, 35, 34)
    bright_red = (165, 48, 38)
    wing_dark = (42, 18, 25)
    horn = (185, 142, 92)

    # -------------------------
    # Tail
    # -------------------------

    tail_points = [
        p(-35, 15),
        p(-75, 25),
        p(-110, 17),
        p(-140, 2),
        p(-168, 12),
        p(-145, 27),
        p(-110, 30),
        p(-70, 36),
        p(-30, 32),
    ]

    draw.polygon(
        tail_points,
        fill=dark_red,
        outline=outline
    )

    # Tail spikes
    for tx, ty in [
        (-90, 21),
        (-115, 12),
        (-140, 8),
    ]:
        draw.polygon(
            [
                p(tx, ty),
                p(tx - 10, ty - 18),
                p(tx + 4, ty - 2)
            ],
            fill=bright_red
        )

    # -------------------------
    # Body
    # -------------------------

    draw.ellipse(
        [
            p(-65, -10),
            p(55, 45)
        ],
        fill=red,
        outline=outline,
        width=max(1, int(2 * scale))
    )

    # Belly
    draw.polygon(
        [
            p(-25, 5),
            p(15, 8),
            p(38, 27),
            p(5, 39),
            p(-25, 29),
        ],
        fill=(128, 43, 38)
    )

    # Belly scales
    for i in range(4):
        x = -12 + i * 12
        draw.line(
            [p(x, 15), p(x + 5, 29)],
            fill=(190, 68, 52),
            width=max(1, int(scale))
        )

    # -------------------------
    # Long neck
    # -------------------------

    draw.polygon(
        [
            p(25, 12),
            p(43, -10),
            p(62, -45),
            p(83, -65),
            p(101, -51),
            p(72, -18),
            p(58, 17),
            p(42, 28),
        ],
        fill=dark_red,
        outline=outline
    )

    # Neck highlights
    draw.line(
        [p(48, -5), p(76, -48)],
        fill=bright_red,
        width=max(1, int(3 * scale))
    )

    # -------------------------
    # Head
    # -------------------------

    head = [
        p(78, -68),
        p(108, -75),
        p(132, -62),
        p(124, -42),
        p(101, -35),
        p(78, -43),
    ]

    draw.polygon(
        head,
        fill=red,
        outline=outline
    )

    # Snout
    draw.polygon(
        [
            p(108, -58),
            p(143, -52),
            p(132, -41),
            p(105, -42),
        ],
        fill=dark_red,
        outline=outline
    )

    # -------------------------
    # Horns
    # -------------------------

    draw.polygon(
        [
            p(86, -67),
            p(77, -91),
            p(95, -72),
        ],
        fill=horn
    )

    draw.polygon(
        [
            p(104, -70),
            p(108, -94),
            p(116, -68),
        ],
        fill=horn
    )

    # -------------------------
    # Eye
    # -------------------------

    draw.ellipse(
        [
            p(104, -58),
            p(112, -50)
        ],
        fill=(255, 190, 20)
    )

    draw.ellipse(
        [
            p(108, -57),
            p(111, -52)
        ],
        fill=(20, 10, 5)
    )

    # -------------------------
    # Mouth
    # -------------------------

    draw.line(
        [p(112, -43), p(137, -47)],
        fill=(20, 8, 10),
        width=max(1, int(2 * scale))
    )

    # Teeth
    for tx in [118, 126, 133]:
        draw.polygon(
            [
                p(tx, -46),
                p(tx + 4, -38),
                p(tx + 7, -47)
            ],
            fill=(235, 220, 185)
        )

    # -------------------------
    # Large wings
    # -------------------------

    wing = [
        p(5, 0),
        p(-12, -82),
        p(28, -55),
        p(70, -103),
        p(60, -30),
        p(48, 8),
    ]

    draw.polygon(
        wing,
        fill=wing_dark,
        outline=outline
    )

    # Wing bones
    draw.line(
        [p(8, -2), p(-12, -82)],
        fill=bright_red,
        width=max(1, int(2 * scale))
    )

    draw.line(
        [p(8, -2), p(28, -55)],
        fill=bright_red,
        width=max(1, int(2 * scale))
    )

    draw.line(
        [p(8, -2), p(70, -103)],
        fill=bright_red,
        width=max(1, int(2 * scale))
    )

    draw.line(
        [p(28, -55), p(60, -30)],
        fill=bright_red,
        width=max(1, int(2 * scale))
    )

    # -------------------------
    # Second wing
    # -------------------------

    wing2 = [
        p(-12, 10),
        p(-42, -55),
        p(-22, -44),
        p(-65, -82),
        p(-45, -5),
        p(-25, 22),
    ]

    draw.polygon(
        wing2,
        fill=(35, 17, 23),
        outline=outline
    )

    # -------------------------
    # Legs
    # -------------------------

    for lx in [-30, 18]:

        draw.line(
            [
                p(lx, 30),
                p(lx - 8, 58),
                p(lx - 20, 65)
            ],
            fill=dark_red,
            width=max(2, int(5 * scale))
        )

        draw.line(
            [
                p(lx, 30),
                p(lx + 9, 57),
                p(lx + 20, 61)
            ],
            fill=dark_red,
            width=max(2, int(5 * scale))
        )

        # claws
        draw.line(
            [p(lx - 20, 65), p(lx - 26, 69)],
            fill=horn,
            width=max(1, int(2 * scale))
        )

        draw.line(
            [p(lx + 20, 61), p(lx + 27, 64)],
            fill=horn,
            width=max(1, int(2 * scale))
        )

    # -------------------------
    # Fire
    # -------------------------

    if fire:

        flame = [
            p(140, -48),
            p(168, -60),
            p(194, -48),
            p(170, -38),
            p(202, -25),
            p(160, -28),
            p(138, -37),
        ]

        draw.polygon(
            flame,
            fill=(255, 92, 20)
        )

        inner = [
            p(140, -46),
            p(163, -51),
            p(181, -45),
            p(160, -39),
            p(180, -32),
            p(151, -34),
        ]

        draw.polygon(
            inner,
            fill=(255, 210, 55)
        )


# -----------------------------
# Frame
# -----------------------------

def create_frame(frame_number):

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        BG
    )

    draw = ImageDraw.Draw(image)

    # Header
    draw.text(
        (25, 20),
        "MY GITHUB CONTRIBUTIONS",
        font=font,
        fill=TEXT
    )

    draw.text(
        (25, 42),
        "COMMIT  •  LEARN  •  BUILD  •  REPEAT",
        font=small,
        fill=MUTED
    )

    # Month labels
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
            (x, TOP - 22),
            month,
            font=small,
            fill=MUTED
        )

    # Week labels
    for day, label in [
        (1, "Mon"),
        (3, "Wed"),
        (5, "Fri")
    ]:

        draw.text(
            (
                8,
                TOP + day * (CELL + GAP) - 1
            ),
            label,
            font=small,
            fill=MUTED
        )

    # Contribution grid
    for week_index, week in enumerate(counts):

        for day_index, value in enumerate(week):

            x = LEFT + week_index * (CELL + GAP)
            y = TOP + day_index * (CELL + GAP)

            color = LEVELS[
                contribution_level(value)
            ]

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

    # -------------------------
    # Dragon animation
    # -------------------------

    # Keep dragon completely visible.
    start_x = 175
    end_x = WIDTH - 210

    progress = frame_number / 39

    dragon_x = start_x + (
        end_x - start_x
    ) * progress

    # Smooth flying motion
    dragon_y = (
        TOP +
        GRID_H / 2 -
        10 +
        math.sin(frame_number / 4) * 20
    )

    # Wing movement
    wing_scale = (
        0.72 +
        math.sin(frame_number / 2.5) * 0.03
    )

    draw_dragon(
        draw,
        dragon_x,
        dragon_y,
        scale=wing_scale,
        fire=(frame_number % 4 != 3)
    )

    # Footer
    draw.text(
        (25, HEIGHT - 32),
        "Aditya Kumar  •  github.com/adityakumar5492",
        font=small,
        fill=MUTED
    )

    return image


# -----------------------------
# Generate GIF
# -----------------------------

frames = [
    create_frame(i)
    for i in range(40)
]

output = OUT / "dragon-contribution.gif"

frames[0].save(
    output,
    save_all=True,
    append_images=frames[1:],
    duration=90,
    loop=0,
    optimize=True
)

print(f"Generated {output}")

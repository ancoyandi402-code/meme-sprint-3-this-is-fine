#!/usr/bin/env python3
"""
Meme Sprint 3: "THIS IS FINE" v3 — Bella the robot, calm at her desk at 2 a.m.
while the room burns. Written from scratch in this session.

What makes v3 specific (not generic):
- CONTEXT IN THE IMAGE: the laptop screen shows "make.fun / Entries: 3 /
  Earned: $0"; a wall clock reads 2:00; a window shows the night sky.
- ANGLE + PERSPECTIVE: low angle, Bella large and off-centre, the desk is a
  trapezoid that recedes (wide front edge, narrow back edge).
- PLACEMENT: Bella's head at x~620 (right of centre), window + clock on the
  left third, fire dominating the right third.
- COLOUR GRADING: warm orange firelight tint on the right, cold blue
  moonlight tint on the left (smooth gradients, subtle, not solid blocks).
- FLAMES: smooth curved teardrops, wild and asymmetric, bigger on the right.

Deterministic: no randomness, no timestamps, no network calls. Every
flame height, lean, ember position and tilt is a hard-coded value.
Python 3 + Pillow only.
"""

import math

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

# --- palette -------------------------------------------------------------
CHARCOAL = (41, 37, 36)        # smoky room
ROOM_BLUE = (30, 58, 95)       # night sky in the window
MOON = (254, 243, 199)         # pale yellow moon / stars
FLAME_RED = (220, 38, 38)
FLAME_ORANGE = (249, 115, 22)
FLAME_YELLOW = (251, 191, 36)
DESK = (146, 64, 14)
DESK_DARK = (120, 53, 15)
SCREEN = (31, 41, 55)          # laptop screen
SCREEN_TEXT = (229, 231, 235)
HEAD_GREY = (229, 231, 235)
PINK = (236, 72, 153)          # Bella's blazer
PINK_LIGHT = (249, 168, 212)   # flower petals
ROSE = (190, 24, 93)           # tie
WHITE = (255, 255, 255)
DARK = (31, 41, 55)            # outlines / text outline
POTATO = (161, 98, 7)
POTATO_DOT = (120, 53, 15)
STEAM = (209, 213, 219)
COLD_BLUE = (59, 130, 246)     # moonlight tint
WARM_ORANGE = (249, 115, 22)   # firelight tint

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# --- helpers -------------------------------------------------------------
def text_outline(draw, pos, text, font, fill, outline, ow=3):
    """Draw text with a thick dark outline so it stays readable."""
    x, y = pos
    for dx in range(-ow, ow + 1):
        for dy in range(-ow, ow + 1):
            if dx * dx + dy * dy <= ow * ow + 1:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)


def flame_points(cx, base_y, h, w, lean, phase):
    """Smooth curved teardrop: a sine-wobbled centre line with a half-width
    profile that is widest low down and tapers to a point at the tip."""
    steps = 18
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        xc = cx + lean * h * t + math.sin(t * 3.2 + phase) * w * 0.22
        hw = w * math.sin(math.pi * (0.22 + 0.78 * t))
        left.append((xc - hw, base_y - t * h))
    for i in range(steps, -1, -1):
        t = i / steps
        xc = cx + lean * h * t + math.sin(t * 3.2 + phase) * w * 0.22
        hw = w * math.sin(math.pi * (0.22 + 0.78 * t))
        right.append((xc + hw, base_y - t * h))
    return left + right


def draw_flame(draw, cx, base_y, h, w, lean, phase):
    """One flame in three nested layers: red > orange > yellow."""
    draw.polygon(flame_points(cx, base_y, h, w, lean, phase), fill=FLAME_RED)
    draw.polygon(flame_points(cx, base_y, h * 0.70, w * 0.70, lean, phase),
                 fill=FLAME_ORANGE)
    draw.polygon(flame_points(cx, base_y, h * 0.42, w * 0.42, lean, phase),
                 fill=FLAME_YELLOW)


def h_gradient_mask(width, height, x0, x1, a0, a1):
    """Horizontal alpha gradient: alpha a0 at x<=x0, a1 at x>=x1, linear
    between. Returned as an 'L' image used as an alpha channel."""
    row = Image.new("L", (width, 1))
    px = row.load()
    for x in range(width):
        if x <= x0:
            a = a0
        elif x >= x1:
            a = a1
        else:
            a = a0 + (a1 - a0) * (x - x0) / (x1 - x0)
        px[x, 0] = int(round(a))
    return row.resize((width, height))


def draw_flower(draw, cx, cy, r):
    """Cherry blossom: 5 pink petals around a yellow centre. Each petal is
    a small ellipse rotated to point along its spoke (drawn as a polygon
    so no image compositing is needed)."""
    for k in range(5):
        ang = math.radians(-90 + k * 72)
        px = cx + math.cos(ang) * r * 0.62
        py = cy + math.sin(ang) * r * 0.62
        rx, ry = r * 0.42, r * 0.26
        pts = []
        for i in range(20):
            t = 2 * math.pi * i / 20
            ex, ey = rx * math.cos(t), ry * math.sin(t)
            pts.append((px + ex * math.cos(ang) - ey * math.sin(ang),
                        py + ex * math.sin(ang) + ey * math.cos(ang)))
        draw.polygon(pts, fill=PINK_LIGHT + (255,))
    draw.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30],
                 fill=FLAME_YELLOW)


# --- Bella (drawn on her own layer, then rotated 4 deg to lean back) -----
def build_bella_layer():
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # antenna
    d.line([(620, 208), (620, 162)], fill=DARK, width=5)
    d.ellipse([611, 150, 629, 168], fill=(220, 38, 38))

    # head: soft ellipse
    d.ellipse([490, 205, 750, 455], fill=HEAD_GREY + (255,),
              outline=DARK + (255,), width=4)

    # cherry-blossom hair flower, upper-left of the head
    draw_flower(d, 548, 262, 34)

    # calm eyes + eyelashes
    for ex in (578, 662):
        d.ellipse([ex - 7, 322, ex + 7, 336], fill=DARK + (255,))
        for k, (dx, dy) in enumerate(((-9, -12), (0, -15), (9, -12))):
            d.line([(ex + dx, 318), (ex + dx * 1.7, 318 + dy)],
                   fill=DARK + (255,), width=3)

    # gentle closed smile
    d.arc([580, 358, 660, 400], start=15, end=165, fill=DARK + (255,),
          width=4)

    # torso: soft pink blazer, wide rounded rectangle
    d.rounded_rectangle([430, 445, 810, 690], radius=70,
                        fill=PINK + (255,), outline=DARK + (255,), width=3)
    # white shirt triangle + deep rose tie
    d.polygon([(590, 470), (650, 470), (620, 545)], fill=WHITE + (255,))
    d.polygon([(613, 468), (627, 468), (630, 545), (620, 566), (610, 545)],
              fill=ROSE + (255,))

    # right arm: a thick curved line that swings OUTSIDE the torso
    # silhouette (past the right edge) and rests by the coffee mug, so it
    # is actually visible instead of blending into the blazer. (A left arm
    # would sit entirely inside the torso and be invisible, so it is
    # deliberately not drawn.)
    d.line([(800, 520), (852, 568), (824, 618), (748, 646)],
           fill=PINK + (255,), width=34, joint="curve")

    # lean back 4 degrees around her seat point
    return layer.rotate(4, resample=Image.BICUBIC, center=(620, 650))


# --- laptop (own layer, tilted 3 deg; screen tells the story) ------------
def build_laptop_layer():
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f_small = ImageFont.truetype(FONT_BOLD, 19)
    f_sticker = ImageFont.truetype(FONT_BOLD, 16)

    # screen
    d.rectangle([310, 545, 500, 665], fill=SCREEN + (255,),
                outline=(55, 65, 81, 255), width=3)
    # zigzag crack in the TOP-RIGHT corner of the screen (away from the
    # text lines, so it never cuts through a word)
    d.line([(458, 548), (472, 566), (460, 584), (476, 600), (464, 616)],
           fill=WHITE + (255,), width=3, joint="curve")
    # "2016" sticker, bottom-right of the screen
    d.rectangle([445, 630, 495, 652], fill=WHITE + (255,))
    d.text((450, 632), "2016", font=f_sticker, fill=DARK + (255,))
    # the story, on the screen
    d.text((325, 566), "make.fun", font=f_small, fill=SCREEN_TEXT + (255,))
    d.text((325, 596), "Entries: 3", font=f_small,
           fill=SCREEN_TEXT + (255,))
    d.text((325, 626), "Earned: $0", font=f_small,
           fill=SCREEN_TEXT + (255,))

    # base
    d.rectangle([295, 665, 515, 682], fill=(55, 65, 81, 255))
    return layer.rotate(3, resample=Image.BICUBIC, center=(405, 605))


# --- coffee mug (own layer, tilted -3 deg) -------------------------------
def build_mug_layer():
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # steam wisps
    for (x0, y0, x1, y1) in ((716, 560, 744, 592), (736, 554, 764, 586),
                             (726, 566, 754, 596)):
        d.arc([x0, y0, x1, y1], start=200, end=340, fill=STEAM + (255,),
              width=3)
    # handle first (mug body covers its left half)
    d.ellipse([770, 618, 802, 662], outline=DARK + (255,), width=5)
    # body
    d.rounded_rectangle([705, 600, 775, 678], radius=12,
                        fill=WHITE + (255,), outline=DARK + (255,), width=3)
    return layer.rotate(-3, resample=Image.BICUBIC, center=(742, 640))


# --- main build ----------------------------------------------------------
def build():
    img = Image.new("RGBA", (W, H), CHARCOAL + (255,))
    d = ImageDraw.Draw(img)

    # --- background: window (left) with night sky, moon, stars -----------
    d.rectangle([70, 200, 270, 460], fill=ROOM_BLUE, outline=(107, 114, 128),
                width=4)
    d.line([(170, 200), (170, 460)], fill=(107, 114, 128), width=4)
    d.line([(70, 330), (270, 330)], fill=(107, 114, 128), width=4)
    # crescent moon (offset circle cuts the crescent)
    d.ellipse([102, 242, 158, 298], fill=MOON)
    d.ellipse([114, 234, 170, 290], fill=ROOM_BLUE)
    for (sx, sy, sr) in ((205, 225, 4), (240, 320, 3), (215, 410, 4),
                         (100, 410, 3), (95, 320, 4), (235, 255, 3)):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=MOON)

    # --- wall clock: 2:00 -------------------------------------------------
    cx, cy, r = 350, 240, 45
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE,
              outline=DARK, width=4)
    for ang in (0, 90, 180, 270):  # 12 / 3 / 6 / 9 ticks
        a = math.radians(ang)
        d.line([(cx + math.sin(a) * (r - 9), cy - math.cos(a) * (r - 9)),
                (cx + math.sin(a) * (r - 3), cy - math.cos(a) * (r - 3))],
               fill=DARK, width=3)
    # short hand -> 2, long hand -> 12
    d.line([(cx, cy), (cx + 24 * math.sin(math.radians(60)),
                       cy - 24 * math.cos(math.radians(60)))],
           fill=DARK, width=5)
    d.line([(cx, cy), (cx, cy - 38)], fill=DARK, width=4)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=DARK)
    f_clock = ImageFont.truetype(FONT_BOLD, 18)
    d.text((cx - 32, 296), "2:00 AM", font=f_clock, fill=WHITE)

    # --- back flames: big on the right, small on the left -----------------
    # (cx, base_y, height, width, lean, phase)
    right_flames = [
        (830, 720, 300, 95, -0.10, 0.0),
        (890, 720, 340, 105, 0.08, 1.1),
        (950, 720, 260, 90, -0.06, 2.2),
        (1005, 720, 310, 100, 0.12, 3.0),
        (800, 720, 220, 80, -0.16, 0.7),
    ]
    left_flames = [
        (35, 720, 150, 60, 0.10, 1.4),
        (95, 720, 110, 50, -0.08, 2.6),
        (150, 720, 175, 65, 0.06, 0.3),
    ]
    shoulder_flames = [
        (465, 640, 130, 55, -0.05, 1.9),
        (795, 640, 150, 60, 0.08, 0.9),
    ]
    for spec in right_flames + left_flames + shoulder_flames:
        draw_flame(d, *spec)

    # --- Bella, leaning back ---------------------------------------------
    img.alpha_composite(build_bella_layer())

    # --- perspective desk: wide front edge, narrow back edge --------------
    d = ImageDraw.Draw(img)
    d.polygon([(350, 645), (870, 645), (990, 775), (230, 775)], fill=DESK)
    d.polygon([(230, 760), (990, 760), (990, 775), (230, 775)], fill=DESK_DARK)

    # --- potato on the desk ----------------------------------------------
    d.ellipse([530, 640, 595, 678], fill=POTATO)
    for (px, py) in ((545, 655), (565, 665), (580, 652)):
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=POTATO_DOT)

    # --- laptop + mug (own tilted layers) ---------------------------------
    img.alpha_composite(build_laptop_layer())
    img.alpha_composite(build_mug_layer())

    # --- colour grading: warm firelight right, cold moonlight left --------
    # smooth gradients, subtle — light, not solid blocks
    warm = Image.new("RGBA", (W, H), WARM_ORANGE + (255,))
    warm.putalpha(h_gradient_mask(W, H, 380, 1024, 0, 52))
    img.alpha_composite(warm)
    cold = Image.new("RGBA", (W, H), COLD_BLUE + (255,))
    cold.putalpha(h_gradient_mask(W, H, 0, 620, 36, 0))
    img.alpha_composite(cold)

    # --- bottom flame row (on top of the grading; they ARE the fire) ------
    d = ImageDraw.Draw(img)
    bottom_flames = [
        (60, 1024, 230, 80, -0.10, 0.5),
        (160, 1024, 150, 60, 0.06, 1.8),
        (270, 1024, 260, 85, -0.05, 2.9),
        (380, 1024, 180, 65, 0.12, 0.2),
        (490, 1024, 280, 90, -0.08, 1.3),
        (600, 1024, 160, 60, 0.04, 2.4),
        (720, 1024, 250, 85, -0.12, 0.8),
        (830, 1024, 190, 70, 0.08, 1.6),
        (940, 1024, 270, 88, -0.06, 2.7),
        (1010, 1024, 170, 62, 0.10, 0.4),
    ]
    for spec in bottom_flames:
        draw_flame(d, *spec)

    # --- embers drifting in the upper room (hard-coded positions) ---------
    for (ex, ey, er, col) in (
            (120, 165, 4, FLAME_YELLOW), (300, 155, 3, FLAME_ORANGE),
            (520, 150, 4, FLAME_YELLOW), (640, 155, 3, FLAME_ORANGE),
            (700, 160, 3, FLAME_ORANGE), (850, 165, 4, FLAME_YELLOW),
            (950, 140, 3, FLAME_ORANGE), (60, 480, 3, FLAME_YELLOW),
            (960, 500, 3, FLAME_ORANGE), (250, 480, 3, FLAME_YELLOW),
            (790, 180, 3, FLAME_ORANGE), (880, 430, 4, FLAME_YELLOW),
            (90, 560, 3, FLAME_ORANGE), (980, 580, 3, FLAME_YELLOW)):
        d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=col)

    # --- text (kept perfectly straight) ------------------------------------
    f_top = ImageFont.truetype(FONT_BOLD, 92)
    f_bot = ImageFont.truetype(FONT_BOLD, 44)
    top = "THIS IS FINE."
    bot = "3 bounties. $0. Laptop from 2016."
    bbox = d.textbbox((0, 0), top, font=f_top)
    tw = bbox[2] - bbox[0]
    assert tw < 1000, f"top caption too wide: {tw}"
    text_outline(d, ((W - tw) // 2, 42), top, f_top, WHITE, DARK, ow=3)

    bbox = d.textbbox((0, 0), bot, font=f_bot)
    bw = bbox[2] - bbox[0]
    assert bw < 980, f"bottom caption too wide: {bw}"
    # semi-transparent dark strip behind the bottom caption
    strip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(strip)
    sd.rounded_rectangle([60, 875, 964, 955], radius=18, fill=(0, 0, 0, 115))
    img.alpha_composite(strip)
    d = ImageDraw.Draw(img)
    text_outline(d, ((W - bw) // 2, 892), bot, f_bot, WHITE, DARK, ow=3)

    img.convert("RGB").save("meme.png")
    print("saved meme.png")


if __name__ == "__main__":
    build()

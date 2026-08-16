from pathlib import Path
import math
import random
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

out_dir = Path(sys.argv[1])
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / "cover.webp"

W, H = 1600, 686
img = Image.new("RGB", (W, H), "#f5e5c6")
pix = img.load()

# Warm, bright luxury-retail gradient.
for y in range(H):
    t = y / max(1, H - 1)
    r = int(248 - 88 * t)
    g = int(232 - 108 * t)
    b = int(198 - 112 * t)
    for x in range(W):
        edge = abs(x - W / 2) / (W / 2)
        lift = int(22 * (1 - edge) * (1 - t))
        pix[x, y] = (min(255, r + lift), min(255, g + lift), min(255, b + lift))

draw = ImageDraw.Draw(img, "RGBA")

# Architectural frames and illuminated display walls.
draw.rectangle((0, 0, W, 90), fill=(92, 55, 28, 115))
for x in (80, 270, 1330, 1520):
    draw.rectangle((x - 22, 60, x + 22, H), fill=(78, 46, 27, 155))
for x0, x1 in ((105, 245), (300, 430), (1170, 1300), (1360, 1490)):
    draw.rectangle((x0, 115, x1, 355), fill=(255, 225, 149, 120), outline=(174, 112, 41, 190), width=5)
    for row in range(5):
        yy = 145 + row * 42
        for col in range(3):
            xx = x0 + 28 + col * 34
            draw.ellipse((xx, yy, xx + 17, yy + 17), fill=(245, 189, 72, 235))

# Central elegant landscape-style wall panel.
draw.rounded_rectangle((565, 105, 1035, 345), radius=18, fill=(126, 82, 46, 145), outline=(218, 164, 79, 210), width=4)
for i in range(8):
    base_x = 610 + i * 53
    height = 45 + (i % 4) * 22
    draw.arc((base_x, 205 - height, base_x + 125, 330), 190, 345, fill=(232, 190, 103, 210), width=5)

# Soft chandelier / focal glow.
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow, "RGBA")
for radius, alpha in ((150, 18), (100, 28), (65, 42)):
    gd.ellipse((800 - radius, 20 - radius / 3, 800 + radius, 20 + radius * 1.3), fill=(255, 231, 166, alpha))
glow = glow.filter(ImageFilter.GaussianBlur(18))
img = Image.alpha_composite(img.convert("RGBA"), glow)
draw = ImageDraw.Draw(img, "RGBA")
draw.rounded_rectangle((735, 48, 865, 128), radius=22, fill=(248, 220, 157, 215), outline=(156, 102, 42, 170), width=4)

# Perspective jewelry counters.
left_poly = [(0, 475), (520, 405), (720, 686), (0, 686)]
right_poly = [(1600, 475), (1080, 405), (880, 686), (1600, 686)]
draw.polygon(left_poly, fill=(226, 197, 145, 190), outline=(124, 83, 45, 220))
draw.polygon(right_poly, fill=(226, 197, 145, 190), outline=(124, 83, 45, 220))

# Gold jewelry highlights on counters.
rng = random.Random(6181)
for side in ("left", "right"):
    for _ in range(48):
        if side == "left":
            x = rng.randint(40, 600)
        else:
            x = rng.randint(1000, 1560)
        y = rng.randint(470, 645)
        rad = rng.randint(5, 12)
        draw.ellipse((x - rad, y - rad, x + rad, y + rad), outline=(248, 190, 45, 235), width=3)

# Crowd silhouettes: dense but lively, avoiding an oppressive mood.
def person(cx, cy, scale, coat):
    head_r = int(12 * scale)
    draw.ellipse((cx - head_r, cy - int(58 * scale), cx + head_r, cy - int(34 * scale)), fill=(123, 86, 65, 240))
    draw.rounded_rectangle((cx - int(21 * scale), cy - int(35 * scale), cx + int(21 * scale), cy + int(38 * scale)), radius=int(10 * scale), fill=coat)

coats = [(47, 48, 50, 235), (71, 58, 48, 235), (91, 70, 58, 235), (65, 70, 82, 235), (117, 84, 57, 235), (132, 96, 78, 235)]
for row, (y, count, scale) in enumerate(((410, 24, 0.72), (455, 22, 0.86), (515, 18, 1.02))):
    spacing = 1000 / max(1, count - 1)
    for i in range(count):
        cx = int(300 + i * spacing + rng.randint(-16, 16))
        person(cx, y + rng.randint(-9, 9), scale, coats[(i + row) % len(coats)])

# Subtle brand plaque rather than giant signage.
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except Exception:
    font = small = ImageFont.load_default()

draw.rounded_rectangle((655, 18, 945, 76), radius=10, fill=(79, 49, 28, 210), outline=(209, 155, 75, 180), width=2)
label = "LAOPU GOLD"
bbox = draw.textbbox((0, 0), label, font=font)
draw.text(((W - (bbox[2]-bbox[0]))/2, 28), label, font=font, fill=(244, 205, 128, 245))

# Gentle filmic finishing without darkness.
img = img.convert("RGB").filter(ImageFilter.GaussianBlur(0.35))
img.save(out, "WEBP", quality=88, method=6)

# Hard validation: fail before publisher if asset is not a real image.
with Image.open(out) as check:
    check.verify()
with Image.open(out) as check:
    assert check.size == (W, H)

print(f"generated and verified {out} ({W}x{H})")

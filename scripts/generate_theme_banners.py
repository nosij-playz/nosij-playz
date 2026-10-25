import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH = 1100
HEIGHT = 320
NUM_FRAMES = 36
FPS = 16

FONT_DIR = r"C:\Windows\Fonts"
FONT_TITLE = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 46)
FONT_SUBTITLE = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 17)
FONT_BADGE = ImageFont.truetype(os.path.join(FONT_DIR, "consola.ttf"), 11)

# Exact Palette (Shared Brand Identity)
DARK_BG = (11, 13, 16)       # #0B0D10 (Dark graphite)
DARK_SURFACE = (20, 24, 30)  # #14181E (Panels/cards)
DARK_BORDER = (43, 48, 56)   # #2B3038 (Subtle border)
DARK_TEXT = (245, 243, 238)  # #F5F3EE (Clear ivory)
DARK_MUTED = (167, 173, 181) # #A7ADB5 (Muted text)

LIGHT_BG = (246, 244, 239)   # #F6F4EF (Warm off-white)
LIGHT_SURFACE = (235, 232, 224)
LIGHT_BORDER = (215, 210, 200)
LIGHT_TEXT = (11, 13, 16)    # #0B0D10
LIGHT_MUTED = (90, 98, 110)  # #5A626E

GOLD = (214, 181, 109)       # #D6B56D (Signature gold)
GOLD_LIGHT = (245, 230, 185) # warm highlight
GOLD_DARK = (158, 125, 55)

# Load portrait
portrait_src = Image.open("assets/jison-portrait.png").convert("RGBA")
scale = 295.0 / portrait_src.height
pw = int(portrait_src.width * scale)
ph = 295
portrait_scaled = portrait_src.resize((pw, ph), Image.Resampling.LANCZOS)

# Create bottom fade
fade_mask = Image.new("L", (pw, ph))
fade_mask.paste(portrait_scaled.split()[3])
for y in range(ph - 45, ph):
    factor = 1.0 - (y - (ph - 45)) / 45.0
    for x in range(pw):
        v = int(fade_mask.getpixel((x, y)) * factor)
        fade_mask.putpixel((x, y), v)
portrait_dark = portrait_scaled.copy()
portrait_dark.putalpha(fade_mask)
portrait_light = portrait_scaled.copy()
portrait_light.putalpha(fade_mask)

# Constellation Nodes (Gold tones, zero blue/cyan)
np.random.seed(137)
NUM_NODES = 24
node_bases = []
for i in range(NUM_NODES):
    if i < 18:
        bx = np.random.uniform(430, WIDTH - 50)
    else:
        bx = np.random.uniform(340, 480)
        
    by = np.random.uniform(35, HEIGHT - 35)
    rx = np.random.uniform(6, 14)
    ry = np.random.uniform(5, 12)
    phase = np.random.uniform(0, 2 * math.pi)
    speed = np.random.choice([1, 2])
    color_type = np.random.choice(["gold", "gold_light", "gold_dim"], p=[0.55, 0.25, 0.20])
    size = np.random.uniform(1.8, 2.6)
    node_bases.append({
        "bx": bx, "by": by, "rx": rx, "ry": ry,
        "phase": phase, "speed": speed, "color_type": color_type, "size": size
    })

def render_banner(frame_idx, mode="dark"):
    t = frame_idx / NUM_FRAMES
    theta = 2 * math.pi * t
    pulse = math.sin(theta) * 0.15 + 0.85
    
    is_dark = (mode == "dark")
    bg_col = DARK_BG if is_dark else LIGHT_BG
    text_col = DARK_TEXT if is_dark else LIGHT_TEXT
    muted_col = DARK_MUTED if is_dark else LIGHT_MUTED
    border_col = DARK_BORDER if is_dark else LIGHT_BORDER
    surface_col = DARK_SURFACE if is_dark else LIGHT_SURFACE

    # Base Canvas
    base = Image.new("RGBA", (WIDTH, HEIGHT), bg_col + (255,))
    
    # Grid lines
    grid_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid_layer)
    grid_alpha = 18 if is_dark else 25
    grid_color = (border_col[0], border_col[1], border_col[2], grid_alpha)
    for gx in range(0, WIDTH, 40):
        gdraw.line([(gx, 0), (gx, HEIGHT)], fill=grid_color, width=1)
    for gy in range(0, HEIGHT, 40):
        gdraw.line([(0, gy), (WIDTH, gy)], fill=grid_color, width=1)
    base = Image.alpha_composite(base, grid_layer)
    
    # Ambient Gold Glow
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.ellipse([70, 35, 300, HEIGHT - 15], fill=(GOLD[0], GOLD[1], GOLD[2], int((28 if is_dark else 20) * pulse)))
    glow_draw.ellipse([500, 50, 960, HEIGHT - 30], fill=(GOLD[0], GOLD[1], GOLD[2], int((15 if is_dark else 12) * pulse)))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(40))
    base = Image.alpha_composite(base, glow_layer)
    
    # Constellation Network
    net_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ndraw = ImageDraw.Draw(net_layer)
    current_nodes = []
    for node in node_bases:
        cur_x = node["bx"] + node["rx"] * math.cos(theta * node["speed"] + node["phase"])
        cur_y = node["by"] + node["ry"] * math.sin(theta * node["speed"] + node["phase"])
        current_nodes.append((cur_x, cur_y, node["color_type"], node["size"]))
        
    for i in range(len(current_nodes)):
        x1, y1, c1, _ = current_nodes[i]
        for j in range(i + 1, len(current_nodes)):
            x2, y2, c2, _ = current_nodes[j]
            dist = math.hypot(x2 - x1, y2 - y1)
            if dist < 120:
                alpha = int((38 if is_dark else 28) * (1 - dist / 120))
                ndraw.line([(x1, y1), (x2, y2)], fill=(GOLD[0], GOLD[1], GOLD[2], alpha), width=1)
                
    for cur_x, cur_y, ctype, sz in current_nodes:
        in_title = (350 <= cur_x <= 960 and 85 <= cur_y <= 145)
        fade = 0.15 if in_title else 1.0
        if is_dark:
            halo_col = (GOLD[0], GOLD[1], GOLD[2], int(60 * fade))
            core_col = (GOLD_LIGHT[0], GOLD_LIGHT[1], GOLD_LIGHT[2], int(220 * fade))
        else:
            halo_col = (GOLD_DARK[0], GOLD_DARK[1], GOLD_DARK[2], int(50 * fade))
            core_col = (GOLD[0], GOLD[1], GOLD[2], int(220 * fade))
        ndraw.ellipse([cur_x - sz - 2, cur_y - sz - 2, cur_x + sz + 2, cur_y + sz + 2], fill=halo_col)
        ndraw.ellipse([cur_x - sz, cur_y - sz, cur_x + sz, cur_y + sz], fill=core_col)
    base = Image.alpha_composite(base, net_layer)
    
    # Portrait
    port_x = 85
    port_y = HEIGHT - ph + 4
    if is_dark:
        base.paste(portrait_dark, (port_x, port_y), portrait_dark)
    else:
        port_bg = Image.new("RGBA", (pw + 20, ph), (0, 0, 0, 0))
        pbg_draw = ImageDraw.Draw(port_bg)
        pbg_draw.rounded_rectangle([0, 10, pw + 18, ph], radius=16, fill=(11, 13, 16, 230), outline=(GOLD[0], GOLD[1], GOLD[2], 120), width=2)
        base.paste(port_bg, (port_x - 10, port_y), port_bg)
        base.paste(portrait_light, (port_x, port_y), portrait_light)
        
    # Typography
    ui_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    uidraw = ImageDraw.Draw(ui_layer)
    content_x = 345
    
    # Pill Badge
    badge_text = "AI SYSTEMS & FULL-STACK ENGINEERING"
    bbox_b = FONT_BADGE.getbbox(badge_text)
    bw = bbox_b[2] - bbox_b[0]
    bh = bbox_b[3] - bbox_b[1]
    pill_y = 48
    pill_h = bh + 14
    pill_w = bw + 38
    uidraw.rounded_rectangle([content_x, pill_y, content_x + pill_w, pill_y + pill_h], radius=10,
                            fill=surface_col + (220,), outline=border_col + (200,), width=1)
    
    dot_pulse = (math.sin(theta) + 1) / 2
    dot_x = content_x + 13
    dot_y = pill_y + pill_h // 2
    uidraw.ellipse([dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5],
                   fill=(GOLD[0], GOLD[1], GOLD[2], int(50 + 90 * dot_pulse)))
    uidraw.ellipse([dot_x - 2.5, dot_y - 2.5, dot_x + 2.5, dot_y + 2.5],
                   fill=(GOLD[0], GOLD[1], GOLD[2], 255))
    uidraw.text((content_x + 24, pill_y + 3), badge_text, font=FONT_BADGE, fill=(GOLD[0], GOLD[1], GOLD[2], 255))
    
    # Name
    name_str = "JISON JOSEPH SEBASTIAN"
    name_y = 90
    if is_dark:
        uidraw.text((content_x, name_y + 1), name_str, font=FONT_TITLE, fill=(0, 0, 0, 190))
        uidraw.text((content_x, name_y), name_str, font=FONT_TITLE, fill=(GOLD[0], GOLD[1], GOLD[2], int(40 * pulse)))
        uidraw.text((content_x, name_y), name_str, font=FONT_TITLE, fill=text_col + (255,))
    else:
        uidraw.text((content_x, name_y + 1), name_str, font=FONT_TITLE, fill=(215, 210, 200, 180))
        uidraw.text((content_x, name_y), name_str, font=FONT_TITLE, fill=text_col + (255,))
        
    # Gold Divider
    div_y = 158
    div_w = 680
    uidraw.line([(content_x, div_y), (content_x + div_w, div_y)], fill=(GOLD[0], GOLD[1], GOLD[2], 55), width=1)
    beam_center = content_x + div_w * ((math.sin(theta) + 1) / 2)
    beam_w = 55
    uidraw.line([(max(content_x, beam_center - beam_w), div_y),
                 (min(content_x + div_w, beam_center + beam_w), div_y)],
                fill=(GOLD[0], GOLD[1], GOLD[2], 200), width=1)
    uidraw.line([(max(content_x, beam_center - 15), div_y),
                 (min(content_x + div_w, beam_center + 15), div_y)],
                fill=(255, 255, 255 if is_dark else 11, 255), width=1)
    
    # Roles
    role_text = "AI/ML Engineer   ·   Agentic AI Developer   ·   Full-Stack Developer"
    uidraw.text((content_x, 178), role_text, font=FONT_SUBTITLE, fill=muted_col + (255,))
    
    # Badges
    meta_badges = [
        ("CS GRADUATE", GOLD),
        ("GATE QUALIFIED", GOLD_LIGHT if is_dark else GOLD_DARK),
        ("SRISHTI 2026 WINNER", GOLD),
        ("AGENTIC SYSTEMS", text_col)
    ]
    mb_x = content_x
    mb_y = 224
    for label, col in meta_badges:
        bbox = FONT_BADGE.getbbox(label)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        pw_b = lw + 18
        ph_b = lh + 10
        uidraw.rounded_rectangle([mb_x, mb_y, mb_x + pw_b, mb_y + ph_b], radius=5,
                                fill=surface_col + (210,), outline=border_col + (180,), width=1)
        uidraw.text((mb_x + 9, mb_y + 2), label, font=FONT_BADGE, fill=col + (240,))
        mb_x += pw_b + 12

    # Border framing
    uidraw.rectangle([1, 1, WIDTH - 2, HEIGHT - 2], outline=(GOLD[0], GOLD[1], GOLD[2], 40 if is_dark else 50), width=1)
    uidraw.rectangle([3, 3, WIDTH - 4, HEIGHT - 4], outline=border_col + (30,), width=1)
    blen = 14
    for cx, cy, sx, sy in [(10, 10, 1, 1), (WIDTH - 11, 10, -1, 1),
                           (10, HEIGHT - 11, 1, -1), (WIDTH - 11, HEIGHT - 11, -1, -1)]:
        uidraw.line([(cx, cy), (cx + sx * blen, cy)], fill=(GOLD[0], GOLD[1], GOLD[2], 190), width=1)
        uidraw.line([(cx, cy), (cx, cy + sy * blen)], fill=(GOLD[0], GOLD[1], GOLD[2], 190), width=1)

    base = Image.alpha_composite(base, ui_layer)
    return base.convert("RGB")

print("Rendering banner-dark.gif...")
dark_frames = []
for i in range(NUM_FRAMES):
    f = render_banner(i, mode="dark")
    dark_frames.append(f.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
dark_frames[0].save("assets/banner-dark.gif", save_all=True, append_images=dark_frames[1:], optimize=True, duration=int(1000/FPS), loop=0)
dark_frames[0].save("assets/banner-dark.png")
dark_frames[0].save("assets/profile-banner.gif", save_all=True, append_images=dark_frames[1:], optimize=True, duration=int(1000/FPS), loop=0)

print("Rendering banner-light.gif...")
light_frames = []
for i in range(NUM_FRAMES):
    f = render_banner(i, mode="light")
    light_frames.append(f.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
light_frames[0].save("assets/banner-light.gif", save_all=True, append_images=light_frames[1:], optimize=True, duration=int(1000/FPS), loop=0)
light_frames[0].save("assets/banner-light.png")

print("Theme banners generated successfully!")

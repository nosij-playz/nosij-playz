import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 2X Supersampling Dimensions for razor-sharp typography
BASE_W, BASE_H = 1100, 320
SCALE = 2
WIDTH, HEIGHT = BASE_W * SCALE, BASE_H * SCALE

NUM_FRAMES = 36
FPS = 16

FONT_DIR = r"C:\Windows\Fonts"
FONT_TITLE = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 48 * SCALE)
FONT_SUBTITLE = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 18 * SCALE)
FONT_BADGE = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 11 * SCALE)
FONT_TAGS = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 11 * SCALE)

# Palette
DARK_BG = (10, 13, 19)
DARK_SURFACE = (18, 22, 32)
DARK_BORDER = (42, 50, 68)
TEXT_WHITE = (255, 255, 255)
TEXT_MUTED = (203, 213, 225) # high-contrast light slate
GOLD = (214, 181, 109)
GOLD_LIGHT = (245, 230, 185)
CYAN_ACCENT = (56, 189, 248)

# Load portrait at 2X
portrait_src = Image.open("assets/jison-portrait.png").convert("RGBA")
scale = (295.0 * SCALE) / portrait_src.height
pw = int(portrait_src.width * scale)
ph = int(295 * SCALE)
portrait_scaled = portrait_src.resize((pw, ph), Image.Resampling.LANCZOS)

# Create soft bottom fade
fade_mask = Image.new("L", (pw, ph))
fade_mask.paste(portrait_scaled.split()[3])
fade_len = int(45 * SCALE)
for y in range(ph - fade_len, ph):
    factor = 1.0 - (y - (ph - fade_len)) / float(fade_len)
    for x in range(pw):
        v = int(fade_mask.getpixel((x, y)) * factor)
        fade_mask.putpixel((x, y), v)
portrait_dark = portrait_scaled.copy()
portrait_dark.putalpha(fade_mask)

# Constellation nodes
np.random.seed(137)
NUM_NODES = 24
node_bases = []
for i in range(NUM_NODES):
    if i < 18:
        bx = np.random.uniform(430 * SCALE, (BASE_W - 50) * SCALE)
    else:
        bx = np.random.uniform(340 * SCALE, 480 * SCALE)
        
    by = np.random.uniform(35 * SCALE, (BASE_H - 35) * SCALE)
    rx = np.random.uniform(6 * SCALE, 14 * SCALE)
    ry = np.random.uniform(5 * SCALE, 12 * SCALE)
    phase = np.random.uniform(0, 2 * math.pi)
    speed = np.random.choice([1, 2])
    color_type = np.random.choice(["gold", "cyan", "gold_dim"], p=[0.55, 0.25, 0.20])
    size = np.random.uniform(2.2 * SCALE, 3.4 * SCALE)
    node_bases.append({
        "bx": bx, "by": by, "rx": rx, "ry": ry,
        "phase": phase, "speed": speed, "color_type": color_type, "size": size
    })

def render_frame_2x(frame_idx):
    t = frame_idx / NUM_FRAMES
    theta = 2 * math.pi * t
    pulse = math.sin(theta) * 0.15 + 0.85
    
    # 1. Base Navy Canvas
    base = Image.new("RGBA", (WIDTH, HEIGHT), DARK_BG + (255,))
    
    # Subtle technical grid
    grid_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid_layer)
    grid_step = 40 * SCALE
    for gx in range(0, WIDTH, grid_step):
        gdraw.line([(gx, 0), (gx, HEIGHT)], fill=(56, 189, 248, 10), width=1 * SCALE)
    for gy in range(0, HEIGHT, grid_step):
        gdraw.line([(0, gy), (WIDTH, gy)], fill=(56, 189, 248, 10), width=1 * SCALE)
    base = Image.alpha_composite(base, grid_layer)
    
    # 2. Ambient Glows
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.ellipse([70 * SCALE, 35 * SCALE, 300 * SCALE, HEIGHT - 15 * SCALE],
                      fill=(GOLD[0], GOLD[1], GOLD[2], int(30 * pulse)))
    glow_draw.ellipse([500 * SCALE, 50 * SCALE, 960 * SCALE, HEIGHT - 30 * SCALE],
                      fill=(56, 189, 248, int(15 * (1.1 - 0.2 * pulse))))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(38 * SCALE))
    base = Image.alpha_composite(base, glow_layer)
    
    # 3. Constellation Filaments
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
            thresh = 120 * SCALE
            if dist < thresh:
                alpha = int(35 * (1 - dist / thresh))
                line_col = (GOLD[0], GOLD[1], GOLD[2], alpha) if c1 == "gold" else (56, 189, 248, alpha)
                ndraw.line([(x1, y1), (x2, y2)], fill=line_col, width=1 * SCALE)
                
    for cur_x, cur_y, ctype, sz in current_nodes:
        # Keep entire text & role zone clean of overlapping nodes
        in_text_zone = (330 * SCALE <= cur_x <= 1020 * SCALE and 40 * SCALE <= cur_y <= 270 * SCALE)
        if in_text_zone:
            continue
        if ctype == "gold":
            halo_col = (GOLD[0], GOLD[1], GOLD[2], 65)
            core_col = (GOLD_LIGHT[0], GOLD_LIGHT[1], GOLD_LIGHT[2], 230)
        else:
            halo_col = (56, 189, 248, 70)
            core_col = (255, 255, 255, 240)
        ndraw.ellipse([cur_x - sz - 2*SCALE, cur_y - sz - 2*SCALE, cur_x + sz + 2*SCALE, cur_y + sz + 2*SCALE], fill=halo_col)
        ndraw.ellipse([cur_x - sz, cur_y - sz, cur_x + sz, cur_y + sz], fill=core_col)
    base = Image.alpha_composite(base, net_layer)
    
    # 4. Portrait
    port_x = 85 * SCALE
    port_y = HEIGHT - ph + 4 * SCALE
    base.paste(portrait_dark, (port_x, port_y), portrait_dark)
    
    # 5. Crisp UI / Typography Layer
    ui_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    uidraw = ImageDraw.Draw(ui_layer)
    content_x = 345 * SCALE
    
    # Top Pill Badge
    badge_text = "AI SYSTEMS & INTELLIGENCE ARCHITECTURE"
    bbox_b = FONT_BADGE.getbbox(badge_text)
    bw = bbox_b[2] - bbox_b[0]
    bh = bbox_b[3] - bbox_b[1]
    pill_y = int(48 * SCALE)
    pill_h = bh + int(14 * SCALE)
    pill_w = bw + int(42 * SCALE)
    uidraw.rounded_rectangle([content_x, pill_y, content_x + pill_w, pill_y + pill_h],
                            radius=10 * SCALE,
                            fill=DARK_SURFACE + (230,),
                            outline=(GOLD[0], GOLD[1], GOLD[2], 120),
                            width=1 * SCALE)
    
    dot_pulse = (math.sin(theta) + 1) / 2
    dot_x = content_x + int(14 * SCALE)
    dot_y = pill_y + pill_h // 2
    uidraw.ellipse([dot_x - 5*SCALE, dot_y - 5*SCALE, dot_x + 5*SCALE, dot_y + 5*SCALE],
                   fill=(CYAN_ACCENT[0], CYAN_ACCENT[1], CYAN_ACCENT[2], int(50 + 90 * dot_pulse)))
    uidraw.ellipse([dot_x - 2.5*SCALE, dot_y - 2.5*SCALE, dot_x + 2.5*SCALE, dot_y + 2.5*SCALE],
                   fill=CYAN_ACCENT + (255,))
    uidraw.text((content_x + int(27 * SCALE), pill_y + int(3.5 * SCALE)), badge_text, font=FONT_BADGE, fill=(GOLD[0], GOLD[1], GOLD[2], 255))
    
    # Main Title: JISON JOSEPH SEBASTIAN
    name_str = "JISON JOSEPH SEBASTIAN"
    name_y = int(88 * SCALE)
    
    # Soft text shadow for depth
    uidraw.text((content_x + 2*SCALE, name_y + 2*SCALE), name_str, font=FONT_TITLE, fill=(0, 0, 0, 220))
    uidraw.text((content_x, name_y), name_str, font=FONT_TITLE, fill=(GOLD[0], GOLD[1], GOLD[2], int(40 * pulse)))
    # Crisp soft white lettering
    uidraw.text((content_x, name_y), name_str, font=FONT_TITLE, fill=TEXT_WHITE + (255,))
    
    # Telemetry divider line with sweeping glint
    div_y = int(158 * SCALE)
    div_w = int(680 * SCALE)
    uidraw.line([(content_x, div_y), (content_x + div_w, div_y)], fill=(GOLD[0], GOLD[1], GOLD[2], 55), width=1 * SCALE)
    beam_center = content_x + div_w * ((math.sin(theta) + 1) / 2)
    beam_w = int(55 * SCALE)
    uidraw.line([(max(content_x, beam_center - beam_w), div_y),
                 (min(content_x + div_w, beam_center + beam_w), div_y)],
                fill=(CYAN_ACCENT[0], CYAN_ACCENT[1], CYAN_ACCENT[2], 200), width=1 * SCALE)
    uidraw.line([(max(content_x, beam_center - 15 * SCALE), div_y),
                 (min(content_x + div_w, beam_center + 15 * SCALE), div_y)],
                fill=(255, 255, 255, 255), width=1 * SCALE)
    
    # Roles: crisp high-contrast text with gold dots
    role_text = "AI/ML Engineer   ·   Agentic AI Developer   ·   Full-Stack Developer"
    uidraw.text((content_x, int(176 * SCALE)), role_text, font=FONT_SUBTITLE, fill=TEXT_MUTED + (255,))
    
    # Metadata Badges
    meta_badges = [
        ("CS GRADUATE", CYAN_ACCENT),
        ("GATE QUALIFIED", GOLD),
        ("SRISHTI 2026 WINNER", GOLD_LIGHT),
        ("AGENTIC SYSTEMS", TEXT_WHITE)
    ]
    mb_x = content_x
    mb_y = int(224 * SCALE)
    for label, col in meta_badges:
        bbox = FONT_TAGS.getbbox(label)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        pw_b = lw + int(20 * SCALE)
        ph_b = lh + int(11 * SCALE)
        uidraw.rounded_rectangle([mb_x, mb_y, mb_x + pw_b, mb_y + ph_b],
                                radius=5 * SCALE,
                                fill=DARK_SURFACE + (220,),
                                outline=DARK_BORDER + (220,),
                                width=1 * SCALE)
        uidraw.text((mb_x + int(10 * SCALE), mb_y + int(2.5 * SCALE)), label, font=FONT_TAGS, fill=col + (255,))
        mb_x += pw_b + int(12 * SCALE)

    # Frame & L-bracket accents
    uidraw.rectangle([1 * SCALE, 1 * SCALE, WIDTH - 2 * SCALE, HEIGHT - 2 * SCALE],
                     outline=(GOLD[0], GOLD[1], GOLD[2], 50), width=1 * SCALE)
    uidraw.rectangle([4 * SCALE, 4 * SCALE, WIDTH - 5 * SCALE, HEIGHT - 5 * SCALE],
                     outline=DARK_BORDER + (40,), width=1 * SCALE)
    blen = int(14 * SCALE)
    for cx, cy, sx, sy in [(10 * SCALE, 10 * SCALE, 1, 1),
                           (WIDTH - 11 * SCALE, 10 * SCALE, -1, 1),
                           (10 * SCALE, HEIGHT - 11 * SCALE, 1, -1),
                           (WIDTH - 11 * SCALE, HEIGHT - 11 * SCALE, -1, -1)]:
        uidraw.line([(cx, cy), (cx + sx * blen, cy)], fill=(GOLD[0], GOLD[1], GOLD[2], 210), width=1 * SCALE)
        uidraw.line([(cx, cy), (cx, cy + sy * blen)], fill=(GOLD[0], GOLD[1], GOLD[2], 210), width=1 * SCALE)

    frame = Image.alpha_composite(base, ui_layer)
    
    # Downscale with LANCZOS for flawless anti-aliasing
    final_frame = frame.resize((BASE_W, BASE_H), Image.Resampling.LANCZOS)
    return final_frame.convert("RGB")

print("Rendering high-quality master frames with 2X supersampling...")
frames = []
for i in range(NUM_FRAMES):
    f = render_frame_2x(i)
    # Quantize with 256 colors for maximum gradient and typography fidelity
    f_p = f.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    frames.append(f_p)
    if (i + 1) % 10 == 0:
        print(f"Rendered {i + 1}/{NUM_FRAMES} frames")

out_path = "assets/profile-banner.gif"
print("Saving ultra-sharp master GIF to", out_path)
duration_ms = int(1000 / FPS)
frames[0].save(
    out_path,
    save_all=True,
    append_images=frames[1:],
    optimize=True,
    duration=duration_ms,
    loop=0
)
file_size = os.path.getsize(out_path)
print(f"Done! File size: {file_size / 1024:.1f} KB")

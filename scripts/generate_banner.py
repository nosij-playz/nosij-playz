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

# Load portrait
portrait_src = Image.open("assets/jison-portrait.png").convert("RGBA")
scale = 295.0 / portrait_src.height
pw = int(portrait_src.width * scale)
ph = 295
portrait_scaled = portrait_src.resize((pw, ph), Image.Resampling.LANCZOS)

# Create soft fade at the bottom of portrait so it blends seamlessly into the navy floor
orig_a = portrait_scaled.split()[3]
comb_a = Image.new("L", (pw, ph))
comb_a.paste(orig_a)
for y in range(ph - 45, ph):
    factor = 1.0 - (y - (ph - 45)) / 45.0
    for x in range(pw):
        v = int(comb_a.getpixel((x, y)) * factor)
        comb_a.putpixel((x, y), v)
portrait_scaled.putalpha(comb_a)

np.random.seed(137)
NUM_NODES = 24
node_bases = []
for i in range(NUM_NODES):
    # Cluster on right wing and perimeter
    if i < 18:
        bx = np.random.uniform(430, WIDTH - 50)
    else:
        bx = np.random.uniform(340, 480)
        
    by = np.random.uniform(35, HEIGHT - 35)
    rx = np.random.uniform(6, 14)
    ry = np.random.uniform(5, 12)
    phase = np.random.uniform(0, 2 * math.pi)
    speed = np.random.choice([1, 2])
    color_type = np.random.choice(["cyan", "gold", "cyan_dim"], p=[0.5, 0.35, 0.15])
    size = np.random.uniform(1.8, 2.6)
    node_bases.append({
        "bx": bx, "by": by, "rx": rx, "ry": ry,
        "phase": phase, "speed": speed, "color_type": color_type, "size": size
    })

def create_smooth_gradient_bg():
    y_coords, x_coords = np.ogrid[:HEIGHT, :WIDTH]
    cx, cy = WIDTH / 2, HEIGHT / 2
    
    dx = (x_coords - cx) / (WIDTH / 2)
    dy = (y_coords - cy) / (HEIGHT / 2)
    dist = np.sqrt(dx**2 * 0.6 + dy**2 * 1.4)
    dist = np.clip(dist, 0, 1.4)
    
    r = (12 - (12 - 5) * (dist / 1.4)).astype(np.uint8)
    g = (20 - (20 - 8) * (dist / 1.4)).astype(np.uint8)
    b = (38 - (38 - 16) * (dist / 1.4)).astype(np.uint8)
    
    base_arr = np.dstack([r, g, b, np.full((HEIGHT, WIDTH), 255, dtype=np.uint8)])
    base_img = Image.fromarray(base_arr, mode="RGBA")
    
    # Subtle technical grid
    grid_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid_layer)
    grid_size = 40
    for gx in range(0, WIDTH, grid_size):
        gdraw.line([(gx, 0), (gx, HEIGHT)], fill=(56, 189, 248, 10), width=1)
    for gy in range(0, HEIGHT, grid_size):
        gdraw.line([(0, gy), (WIDTH, gy)], fill=(56, 189, 248, 10), width=1)
        
    return Image.alpha_composite(base_img, grid_layer)

PRECOMPUTED_BG = create_smooth_gradient_bg()

def render_frame(frame_idx):
    t = frame_idx / NUM_FRAMES
    theta = 2 * math.pi * t
    pulse = math.sin(theta) * 0.15 + 0.85
    
    frame = PRECOMPUTED_BG.copy()
    
    # Ambient glows
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)
    
    # Warm gold backlight glow behind portrait
    gdraw.ellipse([70, 35, 300, HEIGHT - 15], fill=(201, 169, 110, int(30 * pulse)))
    # Cyan ambient glow on right
    gdraw.ellipse([500, 50, 960, HEIGHT - 30], fill=(56, 189, 248, int(18 * (1.1 - 0.2 * pulse))))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(38))
    frame = Image.alpha_composite(frame, glow_layer)
    
    # Constellation filaments
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
                alpha = int(38 * (1 - dist / 120))
                line_col = (201, 169, 110, alpha) if (c1 == "gold" or c2 == "gold") else (56, 189, 248, alpha)
                ndraw.line([(x1, y1), (x2, y2)], fill=line_col, width=1)
                
    for cur_x, cur_y, ctype, sz in current_nodes:
        # Avoid cluttering over text zone
        in_title = (350 <= cur_x <= 960 and 85 <= cur_y <= 145)
        fade = 0.15 if in_title else 1.0
        
        if ctype == "gold":
            halo_col = (201, 169, 110, int(60 * fade))
            core_col = (245, 230, 200, int(220 * fade))
        elif ctype == "cyan":
            halo_col = (56, 189, 248, int(65 * fade))
            core_col = (248, 250, 252, int(230 * fade))
        else:
            halo_col = (30, 95, 130, int(45 * fade))
            core_col = (56, 189, 248, int(170 * fade))
            
        ndraw.ellipse([cur_x - sz - 2, cur_y - sz - 2, cur_x + sz + 2, cur_y + sz + 2], fill=halo_col)
        ndraw.ellipse([cur_x - sz, cur_y - sz, cur_x + sz, cur_y + sz], fill=core_col)
        
    frame = Image.alpha_composite(frame, net_layer)
    
    # Place portrait cleanly on left
    port_x = 85
    port_y = HEIGHT - ph + 4
    frame.paste(portrait_scaled, (port_x, port_y), portrait_scaled)
    
    # Typography & Telemetry Layer
    ui_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    uidraw = ImageDraw.Draw(ui_layer)
    
    content_x = 345
    
    # Top Pill Badge
    badge_text = "AI SYSTEMS & INTELLIGENCE ARCHITECTURE"
    bbox_b = FONT_BADGE.getbbox(badge_text)
    bw = bbox_b[2] - bbox_b[0]
    bh = bbox_b[3] - bbox_b[1]
    
    pill_y = 48
    pill_h = bh + 14
    pill_w = bw + 38
    uidraw.rounded_rectangle([content_x, pill_y, content_x + pill_w, pill_y + pill_h], radius=10,
                            fill=(10, 18, 36, 210), outline=(201, 169, 110, 90), width=1)
    
    dot_pulse = (math.sin(theta) + 1) / 2
    dot_x = content_x + 13
    dot_y = pill_y + pill_h // 2
    uidraw.ellipse([dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5],
                   fill=(56, 189, 248, int(50 + 90 * dot_pulse)))
    uidraw.ellipse([dot_x - 2.5, dot_y - 2.5, dot_x + 2.5, dot_y + 2.5],
                   fill=(56, 189, 248, 255))
    uidraw.text((content_x + 24, pill_y + 3), badge_text, font=FONT_BADGE, fill=(201, 169, 110, 240))
    
    # Main Title: JISON JOSEPH SEBASTIAN
    name_str = "JISON JOSEPH SEBASTIAN"
    name_y = 90
    uidraw.text((content_x, name_y + 1), name_str, font=FONT_TITLE, fill=(0, 0, 0, 190))
    uidraw.text((content_x, name_y), name_str, font=FONT_TITLE, fill=(201, 169, 110, int(50 * pulse)))
    uidraw.text((content_x, name_y), name_str, font=FONT_TITLE, fill=(248, 250, 252, 255))
    
    # Sweeping Divider Line
    div_y = 158
    div_w = 680
    uidraw.line([(content_x, div_y), (content_x + div_w, div_y)], fill=(201, 169, 110, 50), width=1)
    
    beam_center = content_x + div_w * ((math.sin(theta) + 1) / 2)
    beam_w = 55
    uidraw.line([(max(content_x, beam_center - beam_w), div_y),
                 (min(content_x + div_w, beam_center + beam_w), div_y)],
                fill=(56, 189, 248, 200), width=1)
    uidraw.line([(max(content_x, beam_center - 15), div_y),
                 (min(content_x + div_w, beam_center + 15), div_y)],
                fill=(248, 250, 252, 255), width=1)
    
    # Roles
    role_text = "AI/ML Engineer   ·   Agentic AI Developer   ·   Full-Stack Developer"
    uidraw.text((content_x, 178), role_text, font=FONT_SUBTITLE, fill=(226, 232, 240, 240))
    
    # Credentials / Focus Badges
    meta_badges = [
        ("CS GRADUATE", (56, 189, 248)),
        ("GATE QUALIFIED", (201, 169, 110)),
        ("SRISHTI 2026 WINNER", (245, 230, 200)),
        ("AGENTIC SYSTEMS", (148, 163, 184))
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
                                fill=(13, 22, 42, 190), outline=(col[0], col[1], col[2], 80), width=1)
        uidraw.text((mb_x + 9, mb_y + 2), label, font=FONT_BADGE, fill=(col[0], col[1], col[2], 230))
        mb_x += pw_b + 12

    # Sleek Framing & Corner Accents
    uidraw.rectangle([1, 1, WIDTH - 2, HEIGHT - 2], outline=(201, 169, 110, 45), width=1)
    uidraw.rectangle([4, 4, WIDTH - 5, HEIGHT - 5], outline=(56, 189, 248, 20), width=1)
    blen = 14
    for cx, cy, sx, sy in [(10, 10, 1, 1), (WIDTH - 11, 10, -1, 1),
                           (10, HEIGHT - 11, 1, -1), (WIDTH - 11, HEIGHT - 11, -1, -1)]:
        uidraw.line([(cx, cy), (cx + sx * blen, cy)], fill=(201, 169, 110, 200), width=1)
        uidraw.line([(cx, cy), (cx, cy + sy * blen)], fill=(201, 169, 110, 200), width=1)

    frame = Image.alpha_composite(frame, ui_layer)
    return frame.convert("RGB")

print(f"Rendering all {NUM_FRAMES} frames of master banner...")
frames = []
for i in range(NUM_FRAMES):
    f = render_frame(i)
    f_p = f.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    frames.append(f_p)
    if (i + 1) % 10 == 0:
        print(f"Rendered {i + 1}/{NUM_FRAMES} frames")

out_path = "assets/profile-banner.gif"
print("Saving master GIF to", out_path)
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

import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH = 1000
HEIGHT = 280
NUM_FRAMES = 36
FPS = 16

FONT_DIR = r"C:\Windows\Fonts"
FONT_TITLE = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 44)
FONT_SUBTITLE = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 16)
FONT_BADGE = ImageFont.truetype(os.path.join(FONT_DIR, "consola.ttf"), 11)
FONT_META = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 12)

# Colors
COLOR_GOLD = (201, 169, 110)
COLOR_GOLD_LIGHT = (245, 230, 200)
COLOR_CYAN = (56, 189, 248)

np.random.seed(137)
NUM_NODES = 26
node_bases = []
for i in range(NUM_NODES):
    # Keep center clean: clusters on left and right wings
    if i < 12:
        bx = np.random.uniform(35, 250)
    elif i < 24:
        bx = np.random.uniform(750, 965)
    else:
        # A couple at the very top or bottom edge only
        bx = np.random.uniform(250, 750)
        
    if i >= 24:
        by = np.random.choice([np.random.uniform(18, 38), np.random.uniform(HEIGHT - 45, HEIGHT - 20)])
    else:
        by = np.random.uniform(30, HEIGHT - 30)
        
    rx = np.random.uniform(6, 15)
    ry = np.random.uniform(5, 12)
    phase = np.random.uniform(0, 2 * math.pi)
    speed = np.random.choice([1, 2])
    color_type = np.random.choice(["cyan", "gold", "cyan_dim"], p=[0.45, 0.40, 0.15])
    size = np.random.uniform(1.8, 2.8)
    node_bases.append({
        "bx": bx, "by": by, "rx": rx, "ry": ry,
        "phase": phase, "speed": speed, "color_type": color_type, "size": size
    })

def create_smooth_gradient_bg():
    y_coords, x_coords = np.ogrid[:HEIGHT, :WIDTH]
    cx, cy = WIDTH / 2, HEIGHT / 2
    
    dx = (x_coords - cx) / (WIDTH / 2)
    dy = (y_coords - cy) / (HEIGHT / 2)
    dist = np.sqrt(dx**2 * 0.7 + dy**2 * 1.3)
    dist = np.clip(dist, 0, 1.4)
    
    # Center: (13, 22, 42) -> Edges: (6, 9, 18)
    r = (13 - (13 - 6) * (dist / 1.4)).astype(np.uint8)
    g = (22 - (22 - 9) * (dist / 1.4)).astype(np.uint8)
    b = (42 - (42 - 18) * (dist / 1.4)).astype(np.uint8)
    
    base_arr = np.dstack([r, g, b, np.full((HEIGHT, WIDTH), 255, dtype=np.uint8)])
    base_img = Image.fromarray(base_arr, mode="RGBA")
    
    # Subtle technical grid
    grid_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid_layer)
    grid_size = 40
    for gx in range(0, WIDTH, grid_size):
        gdraw.line([(gx, 0), (gx, HEIGHT)], fill=(56, 189, 248, 12), width=1)
    for gy in range(0, HEIGHT, grid_size):
        gdraw.line([(0, gy), (WIDTH, gy)], fill=(56, 189, 248, 12), width=1)
        
    return Image.alpha_composite(base_img, grid_layer)

PRECOMPUTED_BG = create_smooth_gradient_bg()

def draw_tracked_text(draw, font, text, center_x, center_y, fill, tracking=3):
    chars = list(text)
    widths = []
    for ch in chars:
        bbox = font.getbbox(ch)
        widths.append(bbox[2] - bbox[0])
    
    total_w = sum(widths) + (len(chars) - 1) * tracking
    bbox_sample = font.getbbox("A")
    h = bbox_sample[3] - bbox_sample[1]
    
    cur_x = center_x - total_w / 2
    y = center_y - h / 2
    for i, ch in enumerate(chars):
        draw.text((cur_x, y), ch, font=font, fill=fill)
        cur_x += widths[i] + tracking
    return total_w

def render_frame(frame_idx):
    t = frame_idx / NUM_FRAMES
    theta = 2 * math.pi * t
    pulse = math.sin(theta) * 0.15 + 0.85
    
    frame = PRECOMPUTED_BG.copy()
    
    # 1. Ambient Glow Layer
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)
    
    gdraw.ellipse([WIDTH//2 - 270, HEIGHT//2 - 75, WIDTH//2 + 270, HEIGHT//2 + 75],
                  fill=(201, 169, 110, int(22 * pulse)))
    gdraw.ellipse([40, 30, 350, HEIGHT - 30],
                  fill=(56, 189, 248, int(18 * (1.1 - 0.2 * pulse))))
    gdraw.ellipse([WIDTH - 350, 30, WIDTH - 40, HEIGHT - 30],
                  fill=(56, 189, 248, int(18 * pulse)))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(35))
    frame = Image.alpha_composite(frame, glow_layer)
    
    # 2. Orbital Ring & Satellite Beacon
    orbit_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(orbit_layer)
    orbit_cx, orbit_cy = WIDTH // 2, HEIGHT // 2
    orbit_a, orbit_b = 430, 85
    tilt = -0.08
    
    orbit_pts = []
    for ang_deg in range(0, 360, 3):
        ang = math.radians(ang_deg)
        x0 = orbit_a * math.cos(ang)
        y0 = orbit_b * math.sin(ang)
        xr = x0 * math.cos(tilt) - y0 * math.sin(tilt) + orbit_cx
        yr = x0 * math.sin(tilt) + y0 * math.cos(tilt) + orbit_cy
        orbit_pts.append((xr, yr))
        
    odraw.line(orbit_pts + [orbit_pts[0]], fill=(201, 169, 110, 26), width=1)
    
    sat_ang = theta + math.pi / 4
    sat_x0 = orbit_a * math.cos(sat_ang)
    sat_y0 = orbit_b * math.sin(sat_ang)
    sat_x = sat_x0 * math.cos(tilt) - sat_y0 * math.sin(tilt) + orbit_cx
    sat_y = sat_x0 * math.sin(tilt) + sat_y0 * math.cos(tilt) + orbit_cy
    
    odraw.ellipse([sat_x - 7, sat_y - 7, sat_x + 7, sat_y + 7], fill=(56, 189, 248, 60))
    odraw.ellipse([sat_x - 3, sat_y - 3, sat_x + 3, sat_y + 3], fill=(248, 250, 252, 230))
    frame = Image.alpha_composite(frame, orbit_layer)
    
    # 3. Constellation Nodes & Connecting Filaments
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
                alpha = int(45 * (1 - dist / 120))
                if c1 == "gold" or c2 == "gold":
                    line_col = (201, 169, 110, alpha)
                else:
                    line_col = (56, 189, 248, alpha)
                ndraw.line([(x1, y1), (x2, y2)], fill=line_col, width=1)
                
    for cur_x, cur_y, ctype, sz in current_nodes:
        dist_to_center = math.hypot((cur_x - WIDTH/2)/1.4, cur_y - HEIGHT/2)
        fade = min(1.0, max(0.15, (dist_to_center - 110) / 90))
        
        if ctype == "gold":
            halo_col = (201, 169, 110, int(70 * fade))
            core_col = (245, 230, 200, int(230 * fade))
        elif ctype == "cyan":
            halo_col = (56, 189, 248, int(75 * fade))
            core_col = (248, 250, 252, int(240 * fade))
        else:
            halo_col = (30, 95, 130, int(50 * fade))
            core_col = (56, 189, 248, int(180 * fade))
            
        ndraw.ellipse([cur_x - sz - 2, cur_y - sz - 2, cur_x + sz + 2, cur_y + sz + 2], fill=halo_col)
        ndraw.ellipse([cur_x - sz, cur_y - sz, cur_x + sz, cur_y + sz], fill=core_col)
        
    frame = Image.alpha_composite(frame, net_layer)
    
    # 4. Typography & Studio Badge
    ui_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    uidraw = ImageDraw.Draw(ui_layer)
    
    # Pill badge: [ • AI SYSTEMS STUDIO ]
    badge_text = "AI SYSTEMS STUDIO"
    bbox_b = FONT_BADGE.getbbox(badge_text)
    bw = bbox_b[2] - bbox_b[0]
    bh = bbox_b[3] - bbox_b[1]
    
    pill_cx = WIDTH // 2
    pill_cy = 46
    pill_w = bw + 44
    pill_h = bh + 14
    p_x1 = pill_cx - pill_w // 2
    p_y1 = pill_cy - pill_h // 2
    p_x2 = p_x1 + pill_w
    p_y2 = p_y1 + pill_h
    
    uidraw.rounded_rectangle([p_x1, p_y1, p_x2, p_y2], radius=11,
                            fill=(10, 18, 36, 210), outline=(201, 169, 110, 100), width=1)
    
    dot_pulse = (math.sin(theta) + 1) / 2
    dot_x = p_x1 + 14
    dot_y = pill_cy
    uidraw.ellipse([dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5],
                   fill=(56, 189, 248, int(50 + 90 * dot_pulse)))
    uidraw.ellipse([dot_x - 2.5, dot_y - 2.5, dot_x + 2.5, dot_y + 2.5],
                   fill=(56, 189, 248, 255))
    uidraw.text((p_x1 + 25, pill_cy - bh // 2 - 1), badge_text, font=FONT_BADGE, fill=(201, 169, 110, 240))
    
    # Main Title: JISON JOSEPH SEBASTIAN
    name_str = "JISON JOSEPH SEBASTIAN"
    draw_tracked_text(uidraw, FONT_TITLE, name_str, WIDTH // 2, 106, (0, 0, 0, 190), tracking=4)
    draw_tracked_text(uidraw, FONT_TITLE, name_str, WIDTH // 2, 105, (201, 169, 110, int(60 * pulse)), tracking=4)
    draw_tracked_text(uidraw, FONT_TITLE, name_str, WIDTH // 2, 105, (248, 250, 252, 255), tracking=4)
    
    # Fine Divider Line with Sweeping Cyan Light
    div_y = 158
    div_w = 440
    div_x1 = (WIDTH - div_w) // 2
    div_x2 = div_x1 + div_w
    uidraw.line([(div_x1, div_y), (div_x2, div_y)], fill=(201, 169, 110, 50), width=1)
    
    beam_center = div_x1 + div_w * ((math.sin(theta) + 1) / 2)
    beam_w = 45
    b_start = max(div_x1, beam_center - beam_w)
    b_end = min(div_x2, beam_center + beam_w)
    uidraw.line([(b_start, div_y), (b_end, div_y)], fill=(56, 189, 248, 190), width=1)
    uidraw.line([(max(div_x1, beam_center - 15), div_y), (min(div_x2, beam_center + 15), div_y)],
                fill=(248, 250, 252, 255), width=1)
    uidraw.polygon([(WIDTH//2, div_y - 3), (WIDTH//2 + 3, div_y),
                    (WIDTH//2, div_y + 3), (WIDTH//2 - 3, div_y)],
                   fill=(201, 169, 110, 230))
    
    # Subtitle / Roles with custom gold bullets
    r1 = "AI/ML Engineer"
    r2 = "Agentic AI Developer"
    r3 = "Full-Stack Developer"
    
    b1 = FONT_SUBTITLE.getbbox(r1)
    w1 = b1[2] - b1[0]
    b2 = FONT_SUBTITLE.getbbox(r2)
    w2 = b2[2] - b2[0]
    b3 = FONT_SUBTITLE.getbbox(r3)
    w3 = b3[2] - b3[0]
    
    spacing = 26
    bullet_size = 3
    total_role_w = w1 + spacing + w2 + spacing + w3
    start_rx = (WIDTH - total_role_w) // 2
    role_y = 176
    
    uidraw.text((start_rx, role_y), r1, font=FONT_SUBTITLE, fill=(226, 232, 240, 240))
    bx1 = start_rx + w1 + spacing // 2
    by1 = role_y + 11
    uidraw.ellipse([bx1 - bullet_size, by1 - bullet_size, bx1 + bullet_size, by1 + bullet_size],
                   fill=(201, 169, 110, 220))
    
    tx2 = start_rx + w1 + spacing
    uidraw.text((tx2, role_y), r2, font=FONT_SUBTITLE, fill=(226, 232, 240, 240))
    bx2 = tx2 + w2 + spacing // 2
    by2 = role_y + 11
    uidraw.ellipse([bx2 - bullet_size, by2 - bullet_size, bx2 + bullet_size, by2 + bullet_size],
                   fill=(201, 169, 110, 220))
    
    tx3 = tx2 + w2 + spacing
    uidraw.text((tx3, role_y), r3, font=FONT_SUBTITLE, fill=(226, 232, 240, 240))
    
    # Bottom Meta line
    meta_text = "RESEARCH & PRODUCTION AI   |   GATE 2026 QUALIFIED   |   SRISHTI 2026 BEST PROJECT AWARD"
    bbox_m = FONT_META.getbbox(meta_text)
    mw = bbox_m[2] - bbox_m[0]
    meta_x = (WIDTH - mw) // 2
    meta_y = 222
    uidraw.text((meta_x, meta_y), meta_text, font=FONT_META, fill=(185, 200, 225, 210))
    
    # Outer Framing & Corners
    uidraw.rectangle([1, 1, WIDTH - 2, HEIGHT - 2], outline=(201, 169, 110, 45), width=1)
    uidraw.rectangle([4, 4, WIDTH - 5, HEIGHT - 5], outline=(56, 189, 248, 20), width=1)
    
    blen = 14
    for cx, cy, sx, sy in [(10, 10, 1, 1), (WIDTH - 11, 10, -1, 1),
                           (10, HEIGHT - 11, 1, -1), (WIDTH - 11, HEIGHT - 11, -1, -1)]:
        uidraw.line([(cx, cy), (cx + sx * blen, cy)], fill=(201, 169, 110, 200), width=1)
        uidraw.line([(cx, cy), (cx, cy + sy * blen)], fill=(201, 169, 110, 200), width=1)

    frame = Image.alpha_composite(frame, ui_layer)
    return frame.convert("RGB")

print(f"Rendering all {NUM_FRAMES} frames...")
frames = []
for i in range(NUM_FRAMES):
    f = render_frame(i)
    # Quantize to 128 colors for optimal GIF size and crisp color
    f_p = f.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    frames.append(f_p)
    if (i + 1) % 10 == 0:
        print(f"Rendered {i + 1}/{NUM_FRAMES} frames")

out_path = "assets/profile-banner.gif"
print("Saving GIF to", out_path)
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

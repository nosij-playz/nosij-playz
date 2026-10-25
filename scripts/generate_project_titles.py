"""
Generates high-DPI (2x retina) title headers for the 4 featured projects:
- 01 NeuroWave: Gold & Solar Amber (#D6B56D / #F59E0B)
- 02 Sustain_AI: Emerald & Mint (#10B981 / #34D399)
- 03 Retrace AI: Electric Cyan & Sky Blue (#38BDF8 / #0284C7)
- 04 CureCart: Rose & Coral (#FB7185 / #E11D48)
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PROJECTS = [
    {
        "filename": "neurowave.png",
        "num": "01",
        "name": "NeuroWave (CAIRS)",
        "domain": "CLIMATE AI",
        "accent": (214, 181, 109),       # Signature Gold
        "accent_light": (245, 228, 184), # Warm Ivory
        "glow": (214, 181, 109, 120),
    },
    {
        "filename": "sustain-ai.png",
        "num": "02",
        "name": "Sustain_AI",
        "domain": "AGENTIC AI",
        "accent": (16, 185, 129),        # Emerald Green
        "accent_light": (110, 231, 183), # Mint Green
        "glow": (16, 185, 129, 130),
    },
    {
        "filename": "retrace-ai.png",
        "num": "03",
        "name": "Retrace AI",
        "domain": "COMPUTER VISION",
        "accent": (56, 189, 248),        # Electric Cyan
        "accent_light": (186, 230, 253), # Light Sky
        "glow": (56, 189, 248, 130),
    },
    {
        "filename": "curecart.png",
        "num": "04",
        "name": "CureCart",
        "domain": "FULL STACK",
        "accent": (251, 113, 133),       # Rose
        "accent_light": (254, 205, 211), # Soft Coral
        "glow": (251, 113, 133, 130),
    }
]

WIDTH = 800
HEIGHT = 90
SCALE = 2

FONT_PATH_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_PATH_REG = r"C:\Windows\Fonts\segoeui.ttf"

def render_project_title(proj, out_path):
    accent = proj["accent"]
    accent_light = proj["accent_light"]
    
    font_num = ImageFont.truetype(FONT_PATH_BOLD, 18 * SCALE)
    font_name = ImageFont.truetype(FONT_PATH_BOLD, 22 * SCALE)
    font_domain = ImageFont.truetype(FONT_PATH_BOLD, 12 * SCALE)
    
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    
    # 1. Background Pill Container (Dark Card Surface #14181E with border)
    pill_x0 = 4 * SCALE
    pill_y0 = 6 * SCALE
    pill_w = WIDTH - 8 * SCALE
    pill_h = HEIGHT - 12 * SCALE
    
    # Glow layer for ambient border
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)
    gdraw.rounded_rectangle([pill_x0, pill_y0, pill_x0 + pill_w, pill_y0 + pill_h], 
                            radius=12 * SCALE, 
                            outline=proj["glow"], 
                            width=3 * SCALE)
    glow_blurred = glow_layer.filter(ImageFilter.GaussianBlur(radius=5 * SCALE))
    img = Image.alpha_composite(img, glow_blurred)
    draw = ImageDraw.Draw(img)
    
    # Card surface fill + subtle border
    draw.rounded_rectangle([pill_x0, pill_y0, pill_x0 + pill_w, pill_y0 + pill_h], 
                           radius=12 * SCALE, 
                           fill=(20, 24, 30, 240), 
                           outline=accent + (160,), 
                           width=1 * SCALE)
    
    # 2. Number Badge on Left (e.g. 01, 02)
    num_box_w = 42 * SCALE
    num_box_h = pill_h
    draw.rounded_rectangle([pill_x0, pill_y0, pill_x0 + num_box_w, pill_y0 + num_box_h],
                           radius=12 * SCALE,
                           fill=accent + (35,))
    # Right border of number box
    draw.line([(pill_x0 + num_box_w, pill_y0), (pill_x0 + num_box_w, pill_y0 + num_box_h)], 
              fill=accent + (80,), width=1 * SCALE)
    
    # Text in Number Box
    num_str = proj["num"]
    bbox_n = font_num.getbbox(num_str)
    nw = bbox_n[2] - bbox_n[0]
    nh = bbox_n[3] - bbox_n[1]
    nx = pill_x0 + (num_box_w - nw) // 2
    ny = pill_y0 + (num_box_h - nh) // 2 - 2 * SCALE
    draw.text((nx, ny), num_str, font=font_num, fill=accent + (255,))
    
    # 3. Project Name (e.g. NeuroWave (CAIRS))
    name_str = proj["name"]
    name_x = pill_x0 + num_box_w + 14 * SCALE
    bbox_m = font_name.getbbox(name_str)
    mh = bbox_m[3] - bbox_m[1]
    name_y = pill_y0 + (pill_h - mh) // 2 - 2 * SCALE
    
    # High-contrast subtle text shadow
    draw.text((name_x + 1 * SCALE, name_y + 1 * SCALE), name_str, font=font_name, fill=(0, 0, 0, 220))
    # Gradient text
    name_w = bbox_m[2] - bbox_m[0]
    cur_x = name_x
    for ch in name_str:
        bbox_c = font_name.getbbox(ch)
        cw = bbox_c[2] - bbox_c[0]
        prog = (cur_x - name_x) / max(1, name_w)
        r = int(accent[0] + (accent_light[0] - accent[0]) * prog)
        g = int(accent[1] + (accent_light[1] - accent[1]) * prog)
        b = int(accent[2] + (accent_light[2] - accent[2]) * prog)
        draw.text((cur_x, name_y), ch, font=font_name, fill=(r, g, b, 255))
        cur_x += cw
        
    # 4. Domain Tag Pill on Far Right (e.g. [CLIMATE AI])
    domain_str = proj["domain"]
    bbox_d = font_domain.getbbox(domain_str)
    dw = bbox_d[2] - bbox_d[0]
    dh = bbox_d[3] - bbox_d[1]
    dpill_w = dw + 16 * SCALE
    dpill_h = dh + 10 * SCALE
    dpill_x = (pill_x0 + pill_w) - dpill_w - 12 * SCALE
    dpill_y = pill_y0 + (pill_h - dpill_h) // 2
    
    draw.rounded_rectangle([dpill_x, dpill_y, dpill_x + dpill_w, dpill_y + dpill_h],
                           radius=6 * SCALE,
                           fill=accent + (30,),
                           outline=accent + (120,),
                           width=1 * SCALE)
    draw.text((dpill_x + 8 * SCALE, dpill_y + 4 * SCALE), domain_str, font=font_domain, fill=accent_light + (255,))
    
    img.save(out_path, format="PNG", optimize=True)
    print(f"Generated Project Title: {out_path} ({img.size[0]}x{img.size[1]})")

def main():
    out_dir = r"c:\Users\lenovo\Desktop\Potfolio\gitaccound\assets\projects"
    os.makedirs(out_dir, exist_ok=True)
    for p in PROJECTS:
        out_file = os.path.join(out_dir, p["filename"])
        render_project_title(p, out_file)

if __name__ == "__main__":
    main()

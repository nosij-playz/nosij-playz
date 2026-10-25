"""
Renders high-DPI (2x supersampled) PNG headlines matching the portfolio theme:
- Base dark: #0B0D10
- Signature gold: #D6B56D
- Light gold highlight: #F5E4B8
- Subtle border: #2B3038
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HEADERS = [
    {
        "filename": "about.png",
        "title": "CORE FOCUS & BACKGROUND",
    },
    {
        "filename": "selected-works.png",
        "title": "SELECTED WORKS & SYSTEMS",
    },
    {
        "filename": "technical-toolkit.png",
        "title": "TECHNICAL TOOLKIT & SKILLS",
    },
    {
        "filename": "github-analytics.png",
        "title": "GITHUB ANALYTICS & ACTIVITY",
    },
    {
        "filename": "recognition.png",
        "title": "HONORS & RECOGNITION",
    },
    {
        "filename": "connect.png",
        "title": "COLLABORATE & CONNECT",
    }
]

WIDTH = 1600
HEIGHT = 100
SCALE = 2  # 2X supersampling for crisp Retina displays

FONT_PATH = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_SIZE = 36 * SCALE // 2  # 36px in 2X canvas -> 18pt visual

GOLD = (214, 181, 109)
LIGHT_GOLD = (245, 228, 184)
DARK_BORDER = (43, 48, 56)

def render_png(item, out_path):
    title = item["title"]
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    
    # 1. Base transparent image
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 2. Pill on the left
    pill_x0 = 0
    pill_y0 = int(HEIGHT * 0.28)
    pill_w = int(10 * SCALE // 2)
    pill_h = int(44 * SCALE // 2)
    pill_x1 = pill_x0 + pill_w
    pill_y1 = pill_y0 + pill_h
    
    # Glow for pill
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)
    gdraw.rounded_rectangle([pill_x0, pill_y0, pill_x1, pill_y1], radius=pill_w//2, fill=(GOLD[0], GOLD[1], GOLD[2], 140))
    glow_blurred = glow_layer.filter(ImageFilter.GaussianBlur(radius=4 * SCALE))
    img = Image.alpha_composite(img, glow_blurred)
    draw = ImageDraw.Draw(img)
    
    # Solid pill
    draw.rounded_rectangle([pill_x0, pill_y0, pill_x1, pill_y1], radius=pill_w//2, fill=GOLD + (255,))
    
    # 3. Text with tracked spacing
    text_x = pill_x1 + int(24 * SCALE // 2)
    text_y = int(HEIGHT * 0.30)
    
    # Draw letter-spaced text
    cur_x = text_x
    char_spacing = int(3 * SCALE // 2)
    
    # Subtle drop shadow
    shadow_offset = int(2 * SCALE // 2)
    for ch in title:
        bbox = font.getbbox(ch)
        cw = bbox[2] - bbox[0]
        draw.text((cur_x + shadow_offset, text_y + shadow_offset), ch, font=font, fill=(0, 0, 0, 200))
        cur_x += cw + char_spacing
    
    # Text gradient from GOLD to LIGHT_GOLD to GOLD
    cur_x = text_x
    total_text_w = 0
    for ch in title:
        bbox = font.getbbox(ch)
        cw = bbox[2] - bbox[0]
        total_text_w += cw + char_spacing
        
    cur_x = text_x
    for i, ch in enumerate(title):
        bbox = font.getbbox(ch)
        cw = bbox[2] - bbox[0]
        progress = (cur_x - text_x) / max(1, total_text_w)
        # Interpolate gold to light gold and back
        factor = 1.0 - abs(progress - 0.5) * 2  # 0 at edges, 1 in center
        r = int(GOLD[0] + (LIGHT_GOLD[0] - GOLD[0]) * factor)
        g = int(GOLD[1] + (LIGHT_GOLD[1] - GOLD[1]) * factor)
        b = int(GOLD[2] + (LIGHT_GOLD[2] - GOLD[2]) * factor)
        draw.text((cur_x, text_y), ch, font=font, fill=(r, g, b, 255))
        cur_x += cw + char_spacing
        
    text_end_x = cur_x + int(20 * SCALE // 2)
    
    # 4. Trailing subtle line and accent dot
    line_y = text_y + int(FONT_SIZE * 0.65)
    line_end_x = WIDTH - int(30 * SCALE // 2)
    
    if text_end_x < line_end_x:
        # Draw dashed line
        dash_len = int(8 * SCALE // 2)
        gap_len = int(6 * SCALE // 2)
        lx = text_end_x
        while lx < line_end_x - int(15 * SCALE // 2):
            draw.line([(lx, line_y), (min(lx + dash_len, line_end_x - int(15 * SCALE // 2)), line_y)], fill=DARK_BORDER + (255,), width=int(2 * SCALE // 2))
            lx += dash_len + gap_len
            
        # Accent gold terminal bead
        dot_r = int(4 * SCALE // 2)
        draw.ellipse([line_end_x - dot_r, line_y - dot_r, line_end_x + dot_r, line_y + dot_r], fill=GOLD + (220,))
        
    img.save(out_path, format="PNG", optimize=True)
    print(f"Rendered PNG: {out_path} ({img.size[0]}x{img.size[1]})")

def main():
    out_dir = r"c:\Users\lenovo\Desktop\Potfolio\gitaccound\assets\headers"
    os.makedirs(out_dir, exist_ok=True)
    for h in HEADERS:
        out_file = os.path.join(out_dir, h["filename"])
        render_png(h, out_file)

if __name__ == "__main__":
    main()


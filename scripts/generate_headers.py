"""
Generates high-resolution vector SVG section headlines with signature gold theme.
Brand palette:
- Base dark: #0B0D10
- Accent gold: #D6B56D
- Light gold: #F7E7C4
- Subtle border: #2B3038
"""
import os

HEADERS = [
    {
        "filename": "about.svg",
        "title": "CORE FOCUS & BACKGROUND",
        "tag": "PROFILE",
    },
    {
        "filename": "selected-works.svg",
        "title": "SELECTED WORKS & SYSTEMS",
        "tag": "PORTFOLIO",
    },
    {
        "filename": "technical-toolkit.svg",
        "title": "TECHNICAL TOOLKIT & SKILLS",
        "tag": "STACK",
    },
    {
        "filename": "github-analytics.svg",
        "title": "GITHUB ANALYTICS & ACTIVITY",
        "tag": "METRICS",
    },
    {
        "filename": "recognition.svg",
        "title": "HONORS & RECOGNITION",
        "tag": "AWARDS",
    },
    {
        "filename": "connect.svg",
        "title": "COLLABORATE & CONNECT",
        "tag": "CONTACT",
    }
]

def generate_svg(item):
    title = item["title"]
    tag = item["tag"]
    
    # Calculate estimated text width for dynamic line positioning
    char_len = len(title)
    approx_width = 30 + (char_len * 14.5)
    line_start = min(750, int(approx_width + 25))
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 64" width="100%" height="auto" fill="none">
  <defs>
    <linearGradient id="goldTextGrad_{tag}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#D6B56D" />
      <stop offset="60%" stop-color="#F5E4B8" />
      <stop offset="100%" stop-color="#D6B56D" />
    </linearGradient>
    <linearGradient id="goldBarGrad_{tag}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#E5C77F" />
      <stop offset="100%" stop-color="#B89445" />
    </linearGradient>
    <filter id="subtleGlow_{tag}" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#D6B56D" flood-opacity="0.3" />
    </filter>
  </defs>

  <!-- Left Accent Pill -->
  <rect x="0" y="16" width="6" height="32" rx="3" fill="url(#goldBarGrad_{tag})" filter="url(#subtleGlow_{tag})" />
  
  <!-- Section Title -->
  <text x="24" y="39" 
        font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif" 
        font-size="22" 
        font-weight="800" 
        letter-spacing="2" 
        fill="url(#goldTextGrad_{tag})">{title}</text>
        
  <!-- Trailing Border Accent -->
  <line x1="{line_start}" y1="34" x2="790" y2="34" stroke="#2B3038" stroke-width="1.5" stroke-dasharray="4 4" />
  <circle cx="795" cy="34" r="2.5" fill="#D6B56D" opacity="0.8" />
</svg>"""
    return svg

def main():
    out_dir = r"c:\Users\lenovo\Desktop\Potfolio\gitaccound\assets\headers"
    os.makedirs(out_dir, exist_ok=True)
    
    for h in HEADERS:
        filepath = os.path.join(out_dir, h["filename"])
        content = generate_svg(h)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    main()


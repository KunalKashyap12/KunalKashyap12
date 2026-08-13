import os
import datetime
import requests

# -------------------------------------------------------------
# 1. YOUR CONFIGURATION
# -------------------------------------------------------------
GITHUB_USERNAME = "KunalKashyap12"
BIRTH_DATE = datetime.datetime(2002, 3, 15)  # (YYYY, MM, DD)

# Your converted ASCII art
ASCII_ART = [
    "          g@M%@x%%@N%Nw,,      ",
    "       ,.M*'||*%gNM=|mM%g|%N,  ",
    "       p!'|'''|  '`'''|jhlj%w  ",
    "     ,@L. ''         ''!|j%M%X ",
    "    ]j' .,wp@pw,          '%Wg ",
    "  /{||]j@@@@@@@@@pp.           ",
    "      '1@@@@@@@@@@@@p          ",
    "    . :]XX@@@@@@@@%%%kH ' *|mkr",
    "    j%M'    |jkk' ~nrn=i       ",
    "  ! jrr*^           \"! L'':!   ",
    "  j 1p;,. ./ @@  ,  ,;\\nmy ~   ",
    "  i r @@@@mMH @@@@  ^*****M* p j",
    "  | ]@@@@HH]p%%%%%%H,jmgpmh% j ",
    "  ;;%XXXX%@] ,n|.;j%kK|%kXX',| ",
    "  H%kXXXXXj%k||,,;;j!'%i3j]@   ",
    "  \"djjmkl,\"]]||,,,,wwxw|#kjk`  ",
    "    %;%km%%%%M%|%%jkkii|||[    ",
    "    kjj%xKkk1||,,||||j]||'`    ",
    "    |jm@@@@b%%kkmk%i||,[       ",
    "    @p|j%XXXXjkk||j*';j[       ",
    "    ]@00g|    .  ...;j%k       ",
    "    @@@@@@mgmp;,,,,;;jj%%k%    "
]

# -------------------------------------------------------------
# 2. CALCULATE DYNAMIC VALUES
# -------------------------------------------------------------
now = datetime.datetime.now()
years = now.year - BIRTH_DATE.year - ((now.month, now.day) < (BIRTH_DATE.month, BIRTH_DATE.day))
days = (now - BIRTH_DATE.replace(year=now.year if (now.month, now.day) >= (BIRTH_DATE.month, BIRTH_DATE.day)) else now.year - 1)).days
uptime_str = f"{years} years, {days} days"

# Fetch GitHub Stats
headers = {"Authorization": f"token {os.getenv('GH_TOKEN', '')}"} if os.getenv('GH_TOKEN') else {}
user_data = requests.get(f"https://api.github.com/users/{GITHUB_USERNAME}", headers=headers).json()

repos_count = user_data.get("public_repos", 0)
followers_count = user_data.get("followers", 0)

# Right-hand details (Padded to stretch across the box nicely)
RIGHT_TEXT = [
    f"{GITHUB_USERNAME}@github ----------------------------------",
    ". OS: .......................... Windows 11, Linux",
    f". Uptime: ....................... {uptime_str}",
    ". Host: ......................... Full-Stack Developer",
    ". IDE: .......................... VS Code, Neovim",
    "",
    ". Languages.Prog: .............. Python, JavaScript, C++, Java",
    ". Languages.Real: .............. English",
    "",
    ". Hobbies.Software: ............ Open Source, Jailbreaking",
    ". Hobbies.Hardware: ............ Overclocking",
    "",
    "- Contact -------------------------------------------------",
    ". Email: ....................... hello@example.com",
    ". Discord: ..................... @yourdiscord",
    "",
    "- GitHub Stats --------------------------------------------",
    f". Repos: .... {repos_count:<5} | Followers: ... {followers_count}"
]

# -------------------------------------------------------------
# 3. BUILD COMBINED TEXT & GENERATE HIGH-DENSITY SVG
# -------------------------------------------------------------
max_lines = max(len(ASCII_ART), len(RIGHT_TEXT))
lines = []

for i in range(max_lines):
    left = ASCII_ART[i] if i < len(ASCII_ART) else " " * 31
    right = RIGHT_TEXT[i] if i < len(RIGHT_TEXT) else ""
    line = f"{left:<33} {right}".replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    lines.append(line)

def create_svg(filename, bg_color, text_color, border_color):
    tspan_elements = "\n".join(
        [f'  <tspan x="25" dy="18">{line}</tspan>' for line in lines]
    )
    
    # Adjusted canvas height (450) and larger bold font (14px bold) to fill the box
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="950" height="450" viewBox="0 0 950 450">
  <style>
    .terminal {{
      font-family: 'Consolas', 'Fira Code', 'Courier New', monospace;
      font-size: 14px;
      font-weight: 700;
      fill: {text_color};
      white-space: pre;
    }}
  </style>
  <rect width="100%" height="100%" rx="12" fill="{bg_color}" stroke="{border_color}" stroke-width="2"/>
  <text x="25" y="15" class="terminal">
{tspan_elements}
  </text>
</svg>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg_content)

create_svg("dark_mode_preview.svg", "#0d1117", "#c9d1d9", "#30363d")
create_svg("light_mode_preview.svg", "#ffffff", "#24292f", "#d0d7de")

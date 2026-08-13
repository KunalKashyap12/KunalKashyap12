import os
import datetime
import requests

# -------------------------------------------------------------
# 1. YOUR CONFIGURATION
# -------------------------------------------------------------
GITHUB_USERNAME = "KunalKashyap12"
BIRTH_DATE = datetime.datetime(2002, 3, 15)  # (YYYY, MM, DD)

# Your ASCII Art (Padded to 40 characters wide)
ASCII_ART = [
    "      --=+++=--:                        ",
    "               -*%######%%%%#%%#*-      ",
    "             *%%%%%%%%%%%%%%@%%%%%#.    ",
    "            %#%%%%%#%@@@@%%@@@%%%%#*-.  ",
    "           .#%@%%%%@%@@@@@@@@@@@@@@@%#*.",
    "           #%@@@%%%%@@@@@%##%%@@@@@@@%#*:",
    "          .#%%@@@@%%####*=====++##%@@%%%#-",
    "          -%@%@@%#*+++==-----====++#%@%%#-",
    "           -%%@@#+++=-----:::---===*%@%%*:",
    "           .%%@#++++==------=+*****+#@%%: ",
    "            =%@##*+++-=+*##*+-.=====%*%#  ",
    "            :%@*+*+#*=++#==#++=*+++=**%=  ",
    "            :**#==++===+=--==------=+-*-  ",
    "            .++=++---=*=-::--+++++==--*:  ",
    "             =*=====--+*#*+**=:----===+.  ",
    "             .#=+===--===-===-----=====.  ",
    "             .+=+++==+=******=========.   ",
    "              .-++++++++=======+=====.    ",
    "              ..=+++++*++=-==+++++==:.    ",
    "              ...++**+++=======++++-..    ",
    "              ..:+*#**************+-..    ",
    "              ..=+**##########***+++.     ",
    "             ...+++++**********+++++.     ",
    "              .:+++++****+++++===+-.      ",
    "         ..     .+++++++++++++==++=.      "
]

# -------------------------------------------------------------
# 2. CALCULATE DYNAMIC VALUES
# -------------------------------------------------------------
now = datetime.datetime.now()
years = now.year - BIRTH_DATE.year - ((now.month, now.day) < (BIRTH_DATE.month, BIRTH_DATE.day))
days = (now - BIRTH_DATE.replace(year=now.year if (now.month, now.day) >= (BIRTH_DATE.month, BIRTH_DATE.day) else now.year - 1)).days
uptime_str = f"{years} years, {days} days"

# Fetch GitHub Stats
headers = {"Authorization": f"token {os.getenv('GH_TOKEN', '')}"} if os.getenv('GH_TOKEN') else {}
user_data = requests.get(f"https://api.github.com/users/{KunalKashyap12}", headers=headers).json()

repos_count = user_data.get("public_repos", 0)
followers_count = user_data.get("followers", 0)

# Right-hand details (Padded with dots and dashes to stretch across the box)
RIGHT_TEXT = [
    f"{KunalKashyap12}@github ---------------------------------------",
    ". OS: .......................... Windows 11, Linux",
    f". Uptime: ....................... {uptime_str}",
    ". Host: ......................... Full-Stack Developer",
    ". Kernel: ....................... Software Engineer",
    ". IDE: .......................... VS Code, Neovim",
    "",
    ". Languages.Prog: .............. Python, JavaScript, C++, Java",
    ". Languages.Real: .............. English",
    "",
    ". Hobbies.Software: ............ Open Source, Jailbreaking",
    ". Hobbies.Hardware: ............ Overclocking",
    "",
    "- Contact ------------------------------------------------------",
    ". Email: ....................... hello@example.com",
    ". Discord: ..................... @yourdiscord",
    "",
    "- GitHub Stats -------------------------------------------------",
    f". Repos: .... {repos_count:<5} | Followers: ... {followers_count}"
]

# -------------------------------------------------------------
# 3. BUILD COMBINED TEXT & GENERATE HIGH-DENSITY SVG
# -------------------------------------------------------------
max_lines = max(len(ASCII_ART), len(RIGHT_TEXT))
lines = []

for i in range(max_lines):
    left = ASCII_ART[i] if i < len(ASCII_ART) else " " * 40
    right = RIGHT_TEXT[i] if i < len(RIGHT_TEXT) else ""
    # Escape special XML characters
    line = f"{left:<42} {right}".replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    lines.append(line)

def create_svg(filename, bg_color, text_color, border_color):
    tspan_elements = "\n".join(
        [f'  <tspan x="25" dy="18">{line}</tspan>' for line in lines]
    )
    
    # Custom width (1050), height (500), and bold font family (14px)
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="500" viewBox="0 0 1050 500">
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

# Generate SVGs
create_svg("dark_mode_preview.svg", "#0d1117", "#c9d1d9", "#30363d")
create_svg("light_mode_preview.svg", "#ffffff", "#24292f", "#d0d7de")

print("Successfully generated dark_mode_preview.svg and light_mode_preview.svg!")

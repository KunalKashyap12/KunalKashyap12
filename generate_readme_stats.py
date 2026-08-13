#!/usr/bin/env python3
"""
generate_readme_stats.py

Pulls live stats for a GitHub user (repos, stars, followers, commits,
lines of code added/removed) and renders two SVG cards -- light_mode.svg
and dark_mode.svg -- styled like a neofetch terminal output, with an
ASCII-art avatar on the left and a colorful "fetch" block on the right
(OS / Host / Kernel / Languages / Hobbies / Contact / GitHub Stats).

Requires:
    - Environment variable GH_TOKEN (a GitHub Personal Access Token with
      `read:user` and `repo` scopes) so it can query the GraphQL API and
      read commit stats, including for private repos you own.
    - Environment variable GH_USERNAME (your GitHub username).

Usage:
    GH_TOKEN=xxx GH_USERNAME=yourusername python generate_readme_stats.py
"""

import os
import sys
import html
import datetime
import requests
from PIL import Image

GITHUB_API = "https://api.github.com/graphql"
USERNAME = os.environ.get("GH_USERNAME", "KunalKashyap12")
TOKEN = os.environ.get("GH_TOKEN")

# Path to your profile picture. Drop a photo named "profile.png" (or .jpg)
# in the repo root and it will be converted to ASCII art automatically.
# Falls back to placeholder_profile.png if nothing else is found.
PROFILE_IMAGE_CANDIDATES = ["profile.png", "profile.jpg", "profile.jpeg"]
PLACEHOLDER_IMAGE = "placeholder_profile.png"


# --------------------------------------------------------------------------
# EDIT ME -- everything below is the static "fetch" info shown on the card.
# Nothing here is pulled from the GitHub API; fill in your own details.
# Any field can be left as an empty string "" to hide that row.
# --------------------------------------------------------------------------
CONFIG = {
    "os": "Windows 10, Linux",
    "host": "Company / Machine name",
    "kernel": "Your job title / role",
    "ide": "VSCode, PyCharm",
    "languages_programming": "Python, JavaScript, Java, C++",
    "languages_computer": "HTML, CSS, JSON, YAML",
    "languages_real": "English, Hindi",
    "hobbies_software": "Open source, Web dev",
    "hobbies_hardware": "PC building",
    "email_personal": "you@example.com",
    "linkedin": "yourhandle",
    "discord": "yourhandle",
}

if not TOKEN:
    print("ERROR: GH_TOKEN environment variable is not set.", file=sys.stderr)
    sys.exit(1)

HEADERS = {"Authorization": f"bearer {TOKEN}"}


# --------------------------------------------------------------------------
# Data fetching
# --------------------------------------------------------------------------

def run_graphql(query, variables=None):
    resp = requests.post(
        GITHUB_API,
        json={"query": query, "variables": variables or {}},
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


def get_user_overview():
    """Pull profile-level info: followers, repo count, stars, contributions."""
    query = """
    query($login: String!) {
      user(login: $login) {
        createdAt
        followers { totalCount }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes {
            name
            stargazerCount
            isPrivate
            primaryLanguage { name }
          }
        }
        repositoriesContributedTo(first: 1) { totalCount }
        contributionsCollection {
          totalCommitContributions
          restrictedContributionsCount
        }
      }
    }
    """
    data = run_graphql(query, {"login": USERNAME})
    return data["user"]


def get_total_commits():
    """Sum commit contributions across every year the account has existed."""
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          restrictedContributionsCount
        }
      }
    }
    """
    user = get_user_overview()
    created = datetime.datetime.strptime(
        user["createdAt"], "%Y-%m-%dT%H:%M:%SZ"
    )
    now = datetime.datetime.utcnow()

    total = 0
    year_start = created
    while year_start < now:
        year_end = min(
            year_start + datetime.timedelta(days=365), now
        )
        data = run_graphql(
            query,
            {
                "login": USERNAME,
                "from": year_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "to": year_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )
        cc = data["user"]["contributionsCollection"]
        total += cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
        year_start = year_end

    return total, created


def get_lines_of_code():
    """
    Approximate lines added/removed across owned repos using the REST
    'stats/contributors' endpoint (fast, cached by GitHub server-side).
    Falls back gracefully if a repo's stats aren't ready yet.
    """
    user = get_user_overview()
    additions, deletions = 0, 0

    for repo in user["repositories"]["nodes"]:
        if repo["isPrivate"]:
            continue
        url = (
            f"https://api.github.com/repos/{USERNAME}/{repo['name']}"
            f"/stats/contributors"
        )
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            continue
        contributors = r.json()
        if not isinstance(contributors, list):
            continue
        for c in contributors:
            if c.get("author", {}).get("login") == USERNAME:
                for week in c.get("weeks", []):
                    additions += week.get("a", 0)
                    deletions += week.get("d", 0)

    return additions, deletions


def format_uptime(created):
    now = datetime.datetime.utcnow()
    delta_days = (now - created).days
    years, rem = divmod(delta_days, 365)
    months, days = divmod(rem, 30)
    return f"{years} years, {months} months, {days} days"


def collect_stats():
    user = get_user_overview()
    commits, created = get_total_commits()
    additions, deletions = get_lines_of_code()

    stars = sum(r["stargazerCount"] for r in user["repositories"]["nodes"])

    return {
        "username": USERNAME,
        "uptime": format_uptime(created),
        "repos": user["repositories"]["totalCount"],
        "contributed_to": user["repositoriesContributedTo"]["totalCount"],
        "stars": stars,
        "followers": user["followers"]["totalCount"],
        "commits": commits,
        "additions": additions,
        "deletions": deletions,
    }


# --------------------------------------------------------------------------
# ASCII art
# --------------------------------------------------------------------------

# Dense-to-light character ramp (dark/detailed style, like the example).
ASCII_RAMP = "@%#*+=-:. "


def find_profile_image():
    for candidate in PROFILE_IMAGE_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    return PLACEHOLDER_IMAGE if os.path.exists(PLACEHOLDER_IMAGE) else None


def image_to_ascii(path, cols=48):
    """Convert an image to a dense ASCII-art grid of strings."""
    img = Image.open(path).convert("L")  # grayscale

    # Characters are roughly twice as tall as they are wide, so compress
    # vertically to keep the art from looking stretched.
    char_aspect = 0.5
    width, height = img.size
    row_count = max(1, int(cols * (height / width) * char_aspect))
    img = img.resize((cols, row_count))

    pixels = list(img.getdata())
    ramp_len = len(ASCII_RAMP) - 1
    lines = []
    for row in range(row_count):
        line = []
        for col in range(cols):
            brightness = pixels[row * cols + col]  # 0 (black) - 255 (white)
            # darker pixel -> denser character
            idx = int((255 - brightness) / 255 * ramp_len)
            line.append(ASCII_RAMP[idx])
        lines.append("".join(line))
    return lines


# --------------------------------------------------------------------------
# SVG rendering -- neofetch-style terminal block
# --------------------------------------------------------------------------

THEMES = {
    "light": {
        "bg": "#ffffff",
        "border": "#e1e4e8",
        "title": "#24292e",
        "label": "#953800",       # burnt orange, like the reference image
        "section": "#8250df",     # purple section headers
        "value": "#24292e",
        "dot": "#c9ccd1",
        "accent": "#0969da",
        "add": "#1a7f37",
        "del": "#cf222e",
    },
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "title": "#58a6ff",
        "label": "#e3b341",       # amber labels
        "section": "#d2a8ff",     # light purple section headers
        "value": "#c9d1d9",
        "dot": "#484f58",
        "accent": "#58a6ff",
        "add": "#3fb950",
        "del": "#f85149",
    },
}

ASCII_FONT_SIZE = 8
ASCII_LINE_HEIGHT = ASCII_FONT_SIZE * 1.0
ASCII_CHAR_WIDTH = ASCII_FONT_SIZE * 0.6  # approx monospace advance width

TERM_FONT_SIZE = 13
TERM_LINE_HEIGHT = 19
TERM_CHAR_WIDTH = TERM_FONT_SIZE * 0.6  # approx monospace advance width
LINE_CHARS = 56  # target label+dots+value width, in characters


def esc(s):
    return html.escape(str(s))


def render_ascii_block(ascii_lines, x, top, t):
    """Render ASCII art as a block of <text>/<tspan> elements."""
    if not ascii_lines:
        return "", 0, 0
    out = [
        f'<text x="{x}" y="{top}" font-size="{ASCII_FONT_SIZE}" '
        f'font-family="Consolas, Menlo, monospace" fill="{t["accent"]}" '
        f'xml:space="preserve">'
    ]
    for i, line in enumerate(ascii_lines):
        escaped = esc(line).replace(" ", "\u00A0")
        dy = 0 if i == 0 else ASCII_LINE_HEIGHT
        out.append(f'<tspan x="{x}" dy="{dy}">{escaped}</tspan>')
    out.append("</text>")

    block_width = max(len(l) for l in ascii_lines) * ASCII_CHAR_WIDTH
    block_height = len(ascii_lines) * ASCII_LINE_HEIGHT
    return "\n".join(out), block_width, block_height


def dot_leader(label, value, total_chars=LINE_CHARS):
    """Return the number of '.' characters to pad label..value to width."""
    used = len(label) + len(value) + 2  # +2 for ": " and a trailing space
    return max(3, total_chars - used)


class TermBlock:
    """Builds up a list of monospaced terminal lines as SVG tspans."""

    def __init__(self, t):
        self.t = t
        self.tspans = []
        self.line_count = 0

    def _push(self, content):
        dy = 0 if self.line_count == 0 else TERM_LINE_HEIGHT
        self.tspans.append(f'<tspan x="0" dy="{dy}">{content}</tspan>')
        self.line_count += 1

    def blank(self):
        self._push("")

    def header(self, text):
        t = self.t
        rule = "-" * 3
        self._push(
            f'<tspan fill="{t["section"]}" font-weight="700">{rule} {esc(text)} {rule}</tspan>'
        )

    def row(self, label, value, value_color=None):
        if value in (None, ""):
            return
        t = self.t
        vcolor = value_color or t["value"]
        dots = "." * dot_leader(label, str(value))
        self._push(
            f'<tspan fill="{t["label"]}">{esc(label)}:</tspan>'
            f'<tspan fill="{t["dot"]}"> {dots} </tspan>'
            f'<tspan fill="{vcolor}">{esc(value)}</tspan>'
        )

    def raw(self, content):
        self._push(content)

    def render(self, x, y):
        body = "\n".join(self.tspans)
        return (
            f'<text x="{x}" y="{y}" font-size="{TERM_FONT_SIZE}" '
            f'font-family="Consolas, Menlo, monospace" xml:space="preserve">'
            f'{body}</text>'
        )

    def height_px(self):
        return self.line_count * TERM_LINE_HEIGHT


def build_term_block(stats, t):
    tb = TermBlock(t)
    tb.raw(
        f'<tspan fill="{t["title"]}" font-weight="700" font-size="16">'
        f'{esc(stats["username"])}@github</tspan>'
    )
    tb.raw(f'<tspan fill="{t["dot"]}">{"-" * (LINE_CHARS - 2)}</tspan>')
    tb.line_count += 1  # the raw() header line above

    tb.row("OS", CONFIG.get("os", ""))
    tb.row("Uptime", stats["uptime"])
    tb.row("Host", CONFIG.get("host", ""))
    tb.row("Kernel", CONFIG.get("kernel", ""))
    tb.row("IDE", CONFIG.get("ide", ""))
    tb.blank()

    tb.row("Languages.Programming", CONFIG.get("languages_programming", ""))
    tb.row("Languages.Computer", CONFIG.get("languages_computer", ""))
    tb.row("Languages.Real", CONFIG.get("languages_real", ""))
    tb.blank()

    tb.row("Hobbies.Software", CONFIG.get("hobbies_software", ""))
    tb.row("Hobbies.Hardware", CONFIG.get("hobbies_hardware", ""))

    if CONFIG.get("email_personal") or CONFIG.get("linkedin") or CONFIG.get("discord"):
        tb.blank()
        tb.header("Contact")
        tb.row("Email", CONFIG.get("email_personal", ""))
        tb.row("LinkedIn", CONFIG.get("linkedin", ""))
        tb.row("Discord", CONFIG.get("discord", ""))

    tb.blank()
    tb.header("GitHub Stats")
    tb.row(
        "Repos",
        f"{stats['repos']} {{Contributed: {stats['contributed_to']}}}",
    )
    tb.row("Stars", str(stats["stars"]), t["accent"])
    tb.row("Commits", f"{stats['commits']:,}")
    tb.row("Followers", str(stats["followers"]), t["accent"])

    loc_total = stats["additions"] + stats["deletions"]
    dots = "." * dot_leader("Lines of Code", f"{loc_total:,}")
    tb._push(
        f'<tspan fill="{t["label"]}">Lines of Code:</tspan>'
        f'<tspan fill="{t["dot"]}"> {dots} </tspan>'
        f'<tspan fill="{t["value"]}">{loc_total:,} (</tspan>'
        f'<tspan fill="{t["add"]}">+{stats["additions"]:,}</tspan>'
        f'<tspan fill="{t["value"]}">, </tspan>'
        f'<tspan fill="{t["del"]}">-{stats["deletions"]:,}</tspan>'
        f'<tspan fill="{t["value"]}">)</tspan>'
    )

    return tb


def render_svg(stats, theme_name, ascii_lines=None):
    t = THEMES[theme_name]

    tb = build_term_block(stats, t)
    term_width = LINE_CHARS * TERM_CHAR_WIDTH
    term_height = tb.height_px()

    ascii_x, ascii_top = 24, 38
    ascii_svg, ascii_w, ascii_h = render_ascii_block(ascii_lines or [], ascii_x, ascii_top, t)

    term_x = ascii_x + ascii_w + 40 if ascii_lines else 24
    term_y = 38

    total_width = int(term_x + term_width + 24)
    total_height = int(max(ascii_top + ascii_h, term_y + term_height) + 30)

    lines = []
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" '
        f'height="{total_height}" viewBox="0 0 {total_width} {total_height}">'
    )
    lines.append(
        f'<rect width="{total_width}" height="{total_height}" rx="10" '
        f'fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1"/>'
    )
    lines.append(
        '<style>'
        'text{font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;}'
        '</style>'
    )

    if ascii_lines:
        lines.append(ascii_svg)
        lines.append(
            f'<line x1="{term_x - 20}" y1="20" x2="{term_x - 20}" '
            f'y2="{total_height - 20}" stroke="{t["border"]}" stroke-width="1"/>'
        )

    lines.append(f'<g transform="translate({term_x},{term_y})">')
    lines.append(tb.render(0, 0))
    lines.append("</g>")

    lines.append("</svg>")
    return "\n".join(lines)


def main():
    stats = collect_stats()

    image_path = find_profile_image()
    ascii_lines = image_to_ascii(image_path, cols=48) if image_path else None

    for theme in ("light", "dark"):
        svg = render_svg(stats, theme, ascii_lines)
        filename = f"{theme}_mode.svg"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Wrote {filename}")


if __name__ == "__main__":
    main()

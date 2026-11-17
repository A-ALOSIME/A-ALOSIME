#!/usr/bin/env python3
"""Fetch total stars earned across owned public repositories and generate theme-aware inline SVGs."""

import json
import math
import os
import urllib.request
from pathlib import Path

USERNAME = "A-ALOSIME"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": {
        "star": "#E3B341",
        "num": "#E6EDF3",
        "label": "#8B949E",
    },
    "light": {
        "star": "#D49B00",
        "num": "#1F2328",
        "label": "#656D76",
    },
}

FONT_SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def star_polygon_points(cx: float, cy: float, outer_r: float, inner_r: float) -> str:
    pts = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        pts.append(f"{x:.2f},{y:.2f}")
    return " ".join(pts)


def fetch_owned_public_stars(username: str) -> int:
    total = 0
    page = 1
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{username}-profile-stars-updater",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    while True:
        url = f"https://api.github.com/users/{username}/repos?type=owner&per_page=100&page={page}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            repos = json.loads(resp.read().decode("utf-8"))
        if not repos:
            break
        for repo in repos:
            if not repo.get("private", False) and repo.get("owner", {}).get("login", "").lower() == username.lower():
                total += int(repo.get("stargazers_count", 0))
        if len(repos) < 100:
            break
        page += 1
    return total


def render_stars_svg(count: int, mode: str) -> str:
    t = THEMES[mode]
    num_text = f"{count:,}"
    num_width = max(10, len(num_text) * 9)
    num_x = 22
    label_x = num_x + num_width + 5
    total_w = label_x + 76
    pts = star_polygon_points(8.5, 11.4, 7.2, 3.15)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="22" viewBox="0 0 {total_w} 22" role="img" aria-label="{num_text} stars earned">
  <title>{num_text} stars earned across owned public repositories</title>
  <polygon points="{pts}" fill="{t['star']}" />
  <text x="{num_x}" y="16.8" font-family="{FONT_SANS}" font-size="15" font-weight="600" fill="{t['num']}">{num_text}</text>
  <text x="{label_x}" y="16.4" font-family="{FONT_SANS}" font-size="12.5" font-weight="400" fill="{t['label']}">stars earned</text>
</svg>
'''


def main() -> None:
    total = fetch_owned_public_stars(USERNAME)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for mode in ("dark", "light"):
        out = ASSETS_DIR / f"stars-{mode}.svg"
        out.write_text(render_stars_svg(total, mode), encoding="utf-8")
    print(f"Updated borderless inline stars SVGs for {USERNAME}: {total} stars earned")


if __name__ == "__main__":
    main()

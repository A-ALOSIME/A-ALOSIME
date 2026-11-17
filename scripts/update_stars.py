#!/usr/bin/env python3
"""Fetch total stars earned across owned public repositories and generate theme-aware SVGs."""

import json
import os
import urllib.request
from pathlib import Path

USERNAME = "A-ALOSIME"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": {
        "bg": "#0D1117",
        "border": "#30363D",
        "star": "#E3B341",
        "num": "#E6EDF3",
        "label": "#8B949E",
    },
    "light": {
        "bg": "#FFFFFF",
        "border": "#D0D7DE",
        "star": "#BF8700",
        "num": "#1F2328",
        "label": "#656D76",
    },
}

FONT_SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


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
    num_width = max(9, len(num_text) * 8)
    num_x = 29
    label_x = num_x + num_width + 6
    total_w = label_x + 76

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="26" viewBox="0 0 {total_w} 26" role="img" aria-label="{num_text} Stars earned">
  <title>{num_text} Stars earned across owned public repositories</title>
  <rect x="0.5" y="0.5" width="{total_w - 1}" height="25" rx="6" fill="{t['bg']}" stroke="{t['border']}" stroke-width="1" />
  <path d="M16.5 6.8l1.68 3.4 3.75.55-2.71 2.64.64 3.74L16.5 15.36l-3.36 1.77.64-3.74-2.71-2.64 3.75-.55 1.68-3.4z" fill="{t['star']}" />
  <text x="{num_x}" y="17.3" font-family="{FONT_SANS}" font-size="13" font-weight="600" fill="{t['num']}">{num_text}</text>
  <text x="{label_x}" y="17.1" font-family="{FONT_SANS}" font-size="11.5" font-weight="400" fill="{t['label']}">Stars earned</text>
</svg>
'''


def main() -> None:
    total = fetch_owned_public_stars(USERNAME)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for mode in ("dark", "light"):
        out = ASSETS_DIR / f"stars-{mode}.svg"
        out.write_text(render_stars_svg(total, mode), encoding="utf-8")
    print(f"Updated stars SVGs for {USERNAME}: {total} stars earned")


if __name__ == "__main__":
    main()

"""Render a neofetch-style profile card (dark + light SVG) with live stats.

Sources: GitHub GraphQL (GITHUB_TOKEN, required), Zenn public API,
HackTheBox API (HTB_APP_TOKEN, optional). Optional sources fall back to "-".
"""

import calendar
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from html import escape

sys.path.insert(0, os.path.dirname(__file__))
import htb_stats  # noqa: E402

USER = os.environ.get("GH_USERNAME", "long-910")
ZENN_USER = "long910"
OUT_DIR = "assets"
WIDTH = 60  # info column width in characters

ART = [
    "██       ██████  ███    ██  ██████ ",
    "██      ██    ██ ████   ██ ██      ",
    "██      ██    ██ ██ ██  ██ ██   ███",
    "██      ██    ██ ██  ██ ██ ██    ██",
    "███████  ██████  ██   ████  ██████ ",
    "",
    "         █████   ██  ██████ ",
    "        ██   ██ ███ ██  ████",
    "         ██████  ██ ██ ██ ██",
    "             ██  ██ ████  ██",
    "         █████   ██  ██████ ",
    "",
    "",
    " [ automotive :: embedded ]",
    " [ offensive  :: security ]",
]

THEMES = {
    "dark": {
        "bg": "#0d1117", "bar": "#161b22", "border": "#30363d", "text": "#c9d1d9",
        "key": "#ffa657", "value": "#a5d6ff", "dots": "#484f58", "accent": "#9fef00",
    },
    "light": {
        "bg": "#f6f8fa", "bar": "#eaeef2", "border": "#d0d7de", "text": "#24292f",
        "key": "#953800", "value": "#0a3069", "dots": "#afb8c1", "accent": "#2b7a0b",
    },
}

GQL = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, REPOSITORY]) { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes { stargazerCount }
    }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar { totalContributions }
    }
  }
}
"""


def http_json(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "long-910-profile-readme", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)


def github_stats(token):
    body = json.dumps({"query": GQL, "variables": {"login": USER}}).encode()
    res = http_json("https://api.github.com/graphql", body, {"Authorization": f"bearer {token}"})
    if "errors" in res:
        raise RuntimeError(res["errors"])
    u = res["data"]["user"]
    cc = u["contributionsCollection"]
    return {
        "created": datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00")),
        "repos": u["repositories"]["totalCount"],
        "stars": sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        "contributed": u["repositoriesContributedTo"]["totalCount"],
        "followers": u["followers"]["totalCount"],
        "prs": u["pullRequests"]["totalCount"],
        "commits": cc["totalCommitContributions"],
        "contribs": cc["contributionCalendar"]["totalContributions"],
    }


def zenn_stats():
    try:
        u = http_json(f"https://zenn.dev/api/users/{ZENN_USER}")["user"]
        return {"articles": u["articles_count"], "likes": u["total_liked_count"]}
    except Exception as e:  # optional source
        print(f"::warning::Zenn stats unavailable: {e}")
        return {}


def htb_profile():
    token = os.environ.get("HTB_APP_TOKEN")
    if not token:
        return {}
    try:
        return htb_stats.fetch_profile(token)
    except Exception as e:  # optional source
        print(f"::warning::HTB stats unavailable: {e}")
        return {}


def uptime(since):
    now = datetime.now(timezone.utc)
    months = (now.year - since.year) * 12 + now.month - since.month
    days = now.day - since.day
    if days < 0:
        months -= 1
        prev_year, prev_month = (now.year, now.month - 1) if now.month > 1 else (now.year - 1, 12)
        days += calendar.monthrange(prev_year, prev_month)[1]
    return f"{months // 12} years, {months % 12} months, {days} days"


def fmt(n):
    return "-" if n in (None, "") else f"{n:,}" if isinstance(n, int) else str(n)


# Line items: ("title", text) | ("section", text) | ("kv", key, value) |
# ("pair", key1, value1, key2, value2) | ("blank",)
def build_lines(gh, zenn, htb):
    rank_progress = htb.get("rank_ownership")
    next_rank = htb.get("next_rank")
    return [
        ("title", f"{USER}@automotive"),
        ("kv", "OS", "Linux, macOS, RTOS"),
        ("kv", "Uptime", uptime(gh["created"])),
        ("kv", "Host", "Automotive Embedded / ADAS / AD"),
        ("kv", "Kernel", "NVIDIA Orin, Renesas R-Car, Visconti"),
        ("kv", "IDE", "VS Code, Claude Code, tmux"),
        ("blank",),
        ("kv", "Languages.Programming", "Rust, C++, TypeScript, Python"),
        ("kv", "Languages.Web", "Next.js, React, Tailwind"),
        ("kv", "Hobbies.Hacking", "HackTheBox, CTF, Pentest"),
        ("kv", "Hobbies.Writing", "Zenn, 910.jp"),
        ("blank",),
        ("section", "Contact"),
        ("kv", "Blog", "910.jp"),
        ("kv", "Zenn", f"zenn.dev/{ZENN_USER}"),
        ("kv", "HackTheBox", "910long (#698457)"),
        ("kv", "Marketplace", "long-kudo"),
        ("blank",),
        ("section", "GitHub Stats"),
        ("pair", "Repos", f"{fmt(gh['repos'])} {{Contrib: {fmt(gh['contributed'])}}}", "Stars", fmt(gh["stars"])),
        ("pair", "Commits (yr)", fmt(gh["commits"]), "Followers", fmt(gh["followers"])),
        ("pair", "Contribs (yr)", fmt(gh["contribs"]), "PRs", fmt(gh["prs"])),
        ("pair", "Zenn Articles", fmt(zenn.get("articles")), "Likes", fmt(zenn.get("likes"))),
        ("blank",),
        ("section", "HackTheBox"),
        ("pair", "Rank", fmt(htb.get("rank")), "Global", f"#{fmt(htb.get('ranking'))}"),
        ("pair", "Owns", f"{fmt(htb.get('user_owns'))} usr / {fmt(htb.get('system_owns'))} sys",
         "Respect", fmt(htb.get("respects"))),
        ("kv", "Progress", f"{rank_progress}% -> {next_rank}" if rank_progress is not None else "-"),
    ]


def kv_spans(key, value, width):
    dots = max(width - len(key) - len(value) - 3, 1)
    return (
        f'<tspan class="k">{escape(key)}</tspan>:<tspan class="d"> {"." * dots} </tspan>'
        f'<tspan class="v">{escape(value)}</tspan>'
    )


def render_line(item):
    kind = item[0]
    if kind == "title":
        rule = "—" * (WIDTH - len(item[1]) - 1)
        return f'<tspan class="a">{escape(item[1])}</tspan><tspan class="d"> {rule}</tspan>'
    if kind == "section":
        rule = "—" * (WIDTH - len(item[1]) - 3)
        return f'<tspan class="d">- </tspan><tspan class="a">{escape(item[1])}</tspan><tspan class="d"> {rule}</tspan>'
    if kind == "kv":
        return kv_spans(item[1], item[2], WIDTH)
    if kind == "pair":
        left_w = 34
        return kv_spans(item[1], item[2], left_w) + '<tspan class="d"> | </tspan>' + kv_spans(item[3], item[4], WIDTH - left_w - 3)
    return ""


def render_svg(lines, theme):
    c = THEMES[theme]
    line_h, font = 20, 15
    art_x, info_x, top = 24, 400, 62
    height = top + len(lines) * line_h + 20
    width = 985
    art_top = top + (len(lines) - len(ART)) * line_h // 2
    art = "\n".join(
        f'<text x="{art_x}" y="{art_top + i * line_h}" class="a">{escape(row)}</text>' for i, row in enumerate(ART) if row
    )
    info = "\n".join(
        f'<text x="{info_x}" y="{top + i * line_h}">{render_line(item)}</text>' for i, item in enumerate(lines)
    )
    synced = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ConsolasFallback,Consolas,'SF Mono',Menlo,'DejaVu Sans Mono',monospace" font-size="{font}px">
<style>
text {{ fill: {c['text']}; white-space: pre; }}
.k {{ fill: {c['key']}; }}
.v {{ fill: {c['value']}; }}
.d {{ fill: {c['dots']}; }}
.a {{ fill: {c['accent']}; }}
</style>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{c['bg']}" stroke="{c['border']}"/>
<path d="M0.5 30 V10.5 a10 10 0 0 1 10 -10 H{width - 10.5} a10 10 0 0 1 10 10 V30 Z" fill="{c['bar']}" stroke="{c['border']}"/>
<circle cx="20" cy="15" r="6" fill="#ff5f56"/><circle cx="40" cy="15" r="6" fill="#ffbd2e"/><circle cx="60" cy="15" r="6" fill="#27c93f"/>
<text x="{width / 2}" y="20" text-anchor="middle" class="d">{USER}@automotive: ~ — neofetch · synced {synced}</text>
{art}
{info}
</svg>
"""


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("::error::GITHUB_TOKEN is required")
        return 1
    lines = build_lines(github_stats(token), zenn_stats(), htb_profile())
    os.makedirs(OUT_DIR, exist_ok=True)
    for theme in THEMES:
        path = os.path.join(OUT_DIR, f"neofetch-{theme}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render_svg(lines, theme))
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

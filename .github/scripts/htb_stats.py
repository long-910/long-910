"""Fetch HackTheBox profile stats and render them into the HTB section of all READMEs.

Requires the HTB_APP_TOKEN env var (HTB > Profile Settings > App Tokens).
Exits 0 without changes when the token is missing so the workflow stays green
until the secret is configured; exits 1 on API errors (e.g. expired token).
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

USER_ID = os.environ.get("HTB_USER_ID", "698457")
API_URL = f"https://labs.hackthebox.com/api/v4/user/profile/basic/{USER_ID}"
READMES = ["README.md", "README.ja.md", "README.zh.md"]
MARKER_START = "<!--START_SECTION:htb-->"
MARKER_END = "<!--END_SECTION:htb-->"


def fetch_profile(token):
    req = urllib.request.Request(
        API_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "long-910-profile-readme",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)["profile"]


def val(profile, key, default="-"):
    v = profile.get(key)
    return default if v in (None, "") else v


def render(p):
    team = p.get("team") or {}
    progress = val(p, "rank_ownership", None)
    next_rank = val(p, "next_rank", None)
    lines = [
        "```txt",
        f"root@kali:~# htb-cli profile --id {USER_ID}",
        "",
        f"  ┌─[ HackTheBox :: {val(p, 'name')} ]",
        f"  │  Rank       : {val(p, 'rank')}",
        f"  │  Global     : #{val(p, 'ranking')}",
        f"  │  Points     : {val(p, 'points')}",
        f"  │  Owns       : {val(p, 'user_owns', 0)} user / {val(p, 'system_owns', 0)} system",
        f"  │  Bloods     : {val(p, 'user_bloods', 0)} user / {val(p, 'system_bloods', 0)} system",
        f"  │  Respect    : {val(p, 'respects', 0)}",
    ]
    if progress is not None:
        target = f" -> {next_rank}" if next_rank else ""
        lines.append(f"  │  Progress   : {progress}%{target}")
    if team.get("name"):
        lines.append(f"  │  Team       : {team['name']}")
    if p.get("country_name"):
        lines.append(f"  │  Country    : {p['country_name']}")
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines += [
        f"  └─ synced {updated}",
        "",
        "root@kali:~# _",
        "```",
    ]
    return "\n".join(lines)


def main():
    token = os.environ.get("HTB_APP_TOKEN")
    if not token:
        print("::warning::HTB_APP_TOKEN is not set; skipping HTB stats update")
        return 0

    try:
        profile = fetch_profile(token)
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as e:
        print(f"::error::Failed to fetch HTB profile: {e}")
        return 1

    block = f"{MARKER_START}\n{render(profile)}\n{MARKER_END}"
    pattern = re.compile(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END), re.DOTALL)
    for path in READMES:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        if not pattern.search(content):
            print(f"::warning::HTB section not found in {path}")
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(pattern.sub(lambda _: block, content))
        print(f"Updated {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Render the last three full months of GitHub contributions as a dark-themed SVG."""

import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta

USER = os.environ.get("GH_USER", "ojeeeeedev")
TOKEN = os.environ["GITHUB_TOKEN"]
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/contributions.svg"

BG, BORDER, TEXT, MUTED = "#0d1117", "#30363d", "#e6edf3", "#7d8590"
LEVELS = {
    "NONE": "#161b22",
    "FIRST_QUARTILE": "#0e4429",
    "SECOND_QUARTILE": "#006d32",
    "THIRD_QUARTILE": "#26a641",
    "FOURTH_QUARTILE": "#39d353",
}
CELL, GAP, PAD, LEFT, TOP = 16, 4, 20, 34, 64
STEP = CELL + GAP

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel weekday } }
      }
    }
  }
}
"""


def month_back(d, n):
    y, m = d.year, d.month - n
    while m < 1:
        y, m = y - 1, m + 12
    return date(y, m, 1)


def window(today):
    start = month_back(today, 3)
    end = today.replace(day=1) - timedelta(days=1)
    return start, end


def fetch(start, end):
    body = json.dumps({
        "query": QUERY,
        "variables": {
            "login": USER,
            "from": f"{start}T00:00:00Z",
            "to": f"{end}T23:59:59Z",
        },
    }).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as res:
        data = json.load(res)
    if "errors" in data:
        sys.exit(json.dumps(data["errors"]))
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def render(cal, start, end):
    weeks = cal["weeks"]
    width = LEFT + len(weeks) * STEP - GAP + PAD * 2
    height = TOP + 7 * STEP - GAP + 44
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{cal["totalContributions"]} contributions, {start:%b %Y} to {end:%b %Y}">',
        f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
        '<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">',
        f'<text x="{PAD}" y="30" font-size="15" font-weight="600" fill="{TEXT}">'
        f'{cal["totalContributions"]} contributions in the last 3 months</text>',
    ]
    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        out.append(
            f'<text x="{PAD}" y="{TOP + row * STEP + CELL - 3}" font-size="11" fill="{MUTED}">{label}</text>'
        )
    last_month = None
    for i, week in enumerate(weeks):
        x = PAD + LEFT + i * STEP
        for day in week["contributionDays"]:
            d = datetime.strptime(day["date"], "%Y-%m-%d").date()
            if d < start or d > end:
                continue
            y = TOP + day["weekday"] * STEP
            fill = LEVELS[day["contributionLevel"]]
            out.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{fill}">'
                f'<title>{day["contributionCount"]} on {d:%b %-d, %Y}</title></rect>'
            )
        first = next(
            (datetime.strptime(x["date"], "%Y-%m-%d").date() for x in week["contributionDays"]
             if start <= datetime.strptime(x["date"], "%Y-%m-%d").date() <= end),
            None,
        )
        if first and first.month != last_month and (first.day <= 7 or last_month is None):
            out.append(f'<text x="{x}" y="{TOP - 10}" font-size="11" fill="{MUTED}">{first:%b}</text>')
            last_month = first.month
    ly = height - 22
    out.append(f'<text x="{width - PAD - 5 * STEP - 62}" y="{ly + 12}" font-size="11" fill="{MUTED}">Less</text>')
    for i, color in enumerate(LEVELS.values()):
        out.append(
            f'<rect x="{width - PAD - (5 - i) * STEP - 30}" y="{ly}" width="{CELL}" height="{CELL}" rx="3" fill="{color}"/>'
        )
    out.append(f'<text x="{width - PAD - 24}" y="{ly + 12}" font-size="11" fill="{MUTED}">More</text>')
    out += ["</g>", "</svg>"]
    return "\n".join(out) + "\n"


def main():
    start, end = window(date.today())
    svg = render(fetch(start, end), start, end)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT} for {start} to {end}")


if __name__ == "__main__":
    main()

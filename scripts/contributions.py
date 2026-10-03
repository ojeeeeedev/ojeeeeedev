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
PANEL_GAP, PANEL_W = 30, 236

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      commitContributionsByRepository(maxRepositories: 100) { repository { nameWithOwner } }
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
    return data["data"]["user"]["contributionsCollection"]


def stats(col, start, end):
    days = [
        (datetime.strptime(d["date"], "%Y-%m-%d").date(), d["contributionCount"])
        for w in col["contributionCalendar"]["weeks"]
        for d in w["contributionDays"]
    ]
    days = [(d, n) for d, n in days if start <= d <= end]
    streak = best = 0
    for _, n in days:
        streak = streak + 1 if n else 0
        best = max(best, streak)
    return [
        (col["totalCommitContributions"], "Commits"),
        (col["totalPullRequestContributions"], "Pull requests"),
        (len(col["commitContributionsByRepository"]), "Repositories"),
        (sum(1 for _, n in days if n), "Active days"),
        (best, "Longest streak"),
        (max((n for _, n in days), default=0), "Busiest day"),
    ]


def render(col, start, end):
    cal = col["contributionCalendar"]
    weeks = cal["weeks"]
    grid_right = PAD + LEFT + len(weeks) * STEP - GAP
    width = grid_right + PANEL_GAP + PANEL_W + PAD
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
    out.append(f'<text x="{grid_right - 5 * STEP - 62 - 10}" y="{ly + 12}" font-size="11" fill="{MUTED}">Less</text>')
    for i, color in enumerate(LEVELS.values()):
        out.append(
            f'<rect x="{grid_right - (5 - i) * STEP - 40}" y="{ly}" width="{CELL}" height="{CELL}" rx="3" fill="{color}"/>'
        )
    out.append(f'<text x="{grid_right - 36}" y="{ly + 12}" font-size="11" fill="{MUTED}">More</text>')
    px = grid_right + PANEL_GAP
    out.append(f'<line x1="{px - 15}" y1="{TOP - 14}" x2="{px - 15}" y2="{height - 20}" stroke="{BORDER}"/>')
    for i, (value, label) in enumerate(stats(col, start, end)):
        cx = px + (i % 2) * (PANEL_W // 2)
        cy = TOP - 6 + (i // 2) * 56
        out.append(f'<text x="{cx}" y="{cy + 22}" font-size="24" font-weight="600" fill="{TEXT}">{value}</text>')
        out.append(f'<text x="{cx}" y="{cy + 40}" font-size="11" fill="{MUTED}">{label}</text>')
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

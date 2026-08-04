#!/usr/bin/env python3

import base64
import functools
import json
import math
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

API = "https://api.github.com/graphql"

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount } }
      }
    }
  }
}
"""

LIGHT = dict(data="#57606a", emph="#424a53", dim="#656d76",
             surface="#ffffff", graph="#2ea043", graph_peak="#56d364",
             graph_fill_bottom="#238636", graph_fill_mid="#2ea043",
             graph_fill_top="#56d364")
DARK = dict(data="#c9d1d9", emph="#f0f6fc", dim="#8b949e",
            surface="#0d1117", graph="#3fb950", graph_peak="#56d364",
            graph_fill_bottom="#238636", graph_fill_mid="#3fb950",
            graph_fill_top="#56d364")
THEMES = dict(light=LIGHT, dark=DARK)
MONO = ("JBMono,ui-monospace,SFMono-Regular,Menlo,Consolas,"
        "&apos;Liberation Mono&apos;,monospace")
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

OUT_DIR = os.path.join(os.path.dirname(HERE), "assets", "stats")

WIDTH = 620
REVEAL = 1.30                       # seconds the line takes to draw itself
GRAPH_IN = 0.45                     # when the line starts drawing
DRAW_END = GRAPH_IN + REVEAL
DOT_R = 5                           
DOT_RING = 2.2                      # stroke-width, since the plot inset is derived from it
PAD_R = DOT_R + DOT_RING / 2        # room so the endpoint ring lands flush, not clipped

EASE_OUT = "0.22 1 0.36 1"          
EASE_IN_OUT = "0.4 0 0.2 1"


@functools.lru_cache(maxsize=None)
def face(filename, weight):
    path = os.path.join(FONT_DIR, filename)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return (f"@font-face{{font-family:JBMono;font-style:normal;"
            f"font-weight:{weight};font-display:block;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")


def font_text():
    return face("jbmono-400.woff2", 400) + face("jbmono-600.woff2", 600)


def window():
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=364)
    return (f"{start.isoformat()}T00:00:00Z", f"{today.isoformat()}T23:59:59Z")


def fetch(login, token):
    since, until = window()
    body = json.dumps({"query": QUERY,
                       "variables": {"login": login,
                                     "from": since, "to": until}}).encode()
    req = urllib.request.Request(
        API, data=body,
        headers={"Authorization": f"bearer {token}",
                 "Content-Type": "application/json",
                 "User-Agent": f"{login}-profile-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise SystemExit(f"GraphQL errors: {payload['errors']}")
    user = (payload.get("data") or {}).get("user")
    if not user:
        raise SystemExit(f"no such user: {login}")
    return user


def summarise(user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = [w["contributionDays"] for w in cal["weeks"]]
    days = [d for w in weeks for d in w]
    weekly = [sum(d["contributionCount"] for d in w) for w in weeks]
    return dict(
        total=cal["totalContributions"],
        active=sum(1 for d in days if d["contributionCount"] > 0),
        best_week=max(weekly) if weekly else 0,
        weekly=weekly)


def style(t):
    return (f"<style>{font_text()}"
            f".e-f{{fill:{t['emph']}}}.m-f{{fill:{t['dim']}}}"
            f".graph-fill{{fill:url(#wash)}}"
            f".graph-stroke{{stroke:{t['graph']};stroke-width:2.4;"
            f"stroke-linecap:round;stroke-linejoin:round;fill:none}}"
            f".endpoint{{fill:{t['surface']};stroke:{t['graph_peak']};"
            f"stroke-width:{DOT_RING}}}</style>"
            f"<defs><linearGradient id='wash' x1='0' y1='1' x2='0' y2='0'>"
            f"<stop offset='0%' stop-color='{t['graph_fill_bottom']}' "
            f"stop-opacity='.08'/>"
            f"<stop offset='70%' stop-color='{t['graph_fill_mid']}' "
            f"stop-opacity='.18'/>"
            f"<stop offset='100%' stop-color='{t['graph_fill_top']}' "
            f"stop-opacity='.42'/>"
            f"</linearGradient></defs>")


def head(w, h, t):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" fill="none" font-family="{MONO}">'
            + style(t))


def anim(attr, frm, to, delay, dur, spline=EASE_OUT):
    return (f'<animate attributeName="{attr}" values="{frm};{to}" '
            f'keyTimes="0;1" calcMode="spline" keySplines="{spline}" '
            f'begin="{delay:.2f}s" dur="{dur}s" fill="freeze"/>')


def fade(delay, dur=0.45):
    return anim("opacity", 0, 1, delay, dur)


def label(x, y, text, size=11, cls="m-f", anchor="start", extra=""):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}"{a}'
            f'{extra}>{text}</text>')


def draw_stats(s, t):
    H = 148
    weekly = s["weekly"] or [0]
    peak = max(weekly) or 1
    p = [head(WIDTH, H, t)]
    p.append(f'<g opacity="0">{fade(0.10)}'
             + label(0, 50, s["total"], 52, "e-f", extra=' font-weight="600"')
             + label(0, 72, "contributions in the last year", 12) + '</g>')
    for i, (val, lab) in enumerate([(s["active"], "active days"),
                                    (s["best_week"], "best week")]):
        p.append(f'<g opacity="0">{fade(0.30 + i * 0.12)}'
                 + label(WIDTH, 30 + i * 40, val, 19, "e-f", "end",
                         ' font-weight="600"')
                 + label(WIDTH, 47 + i * 40, lab, 11, "m-f", "end") + '</g>')

    base, top = H - 10, H - 58
    span = base - top
    step = (WIDTH - PAD_R) / max(len(weekly) - 1, 1)
    pts = [(i * step, base - math.sqrt(v / peak) * span)
           for i, v in enumerate(weekly)]
    ex, ey = pts[-1]

    p.append(f'<path opacity="0" d="M{pts[0][0]:.1f} {base:.1f}'
             + "".join(f'L{x:.1f} {y:.1f}' for x, y in pts)
             + f'L{ex:.1f} {base:.1f}Z" class="graph-fill">'
             + anim("opacity", 0, 1, DRAW_END - 0.18, 0.75, EASE_IN_OUT)
             + '</path>')

    p.append(f'<path d="M{pts[0][0]:.1f} {pts[0][1]:.1f}'
             + "".join(f'L{x:.1f} {y:.1f}' for x, y in pts[1:])
             + f'" class="graph-stroke" pathLength="1000" '
             f'stroke-dasharray="1000" stroke-dashoffset="1000">'
             + anim("stroke-dashoffset", 1000, 0, GRAPH_IN, REVEAL)
             + '</path>')

    p.append(
        f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="0" class="endpoint" opacity="0">'
        + anim("opacity", 0, 1, DRAW_END, 0.24)
        + f'<animate attributeName="r" values="0;{DOT_R * 1.18:.2f};{DOT_R}" '
        f'keyTimes="0;0.6;1" calcMode="spline" '
        f'keySplines="{EASE_OUT};{EASE_IN_OUT}" '
        f'begin="{DRAW_END:.2f}s" dur="0.42s" fill="freeze"/>'
        + '</circle>')
    p.append("</svg>")
    return "".join(p)


def write(path, svg):
    old = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = f.read()
    if old == svg:
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return True


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    login = os.environ.get("GH_LOGIN", "Neilblaze")
    out_dir = os.environ.get("OUT_DIR", OUT_DIR)
    os.makedirs(out_dir, exist_ok=True)

    s = summarise(fetch(login, token))
    changed = [name for name, t in THEMES.items()
               if write(os.path.join(out_dir, f"stats_{name}.svg"),
                        draw_stats(s, t))]
    print(f"{s['total']} contributions, {s['active']} active days, "
          f"best week {s['best_week']}")
    print("updated: " + (", ".join(f"stats_{n}.svg" for n in changed)
                         if changed else "nothing"))


if __name__ == "__main__":
    main()

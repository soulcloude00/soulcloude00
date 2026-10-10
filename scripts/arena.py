"""Builds assets/arena.svg (looping agent race) and the vote buttons. Run: python3 scripts/arena.py"""
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(ROOT, exist_ok=True)

W, H, U = 1200, 560, 6
SKY, WHITE, DIM, LINE = "#060709", "#F2F0EA", "#5b616b", "#1d2128"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
START, FINISH = 150, 1010          # sprite left edge at start / when crossing finish
SW = 72                            # sprite width
LANES = [262, 392, 522]            # ground line of each lane
RACE = 7.0
DT = 0.05

AGENTS = {
    "claude": dict(name="CLAUDE", body="#D97757", dark="#8C4026",
        pal={"X": "#D97757", "D": "#B85C3E"}, sprite=[
        "..XXXXXXXX..",
        "..XXXXXXXX..",
        "..XEEXXEEX..",
        "XXXXXXXXXXXX",
        "XXXXXXXXXXXX",
        "..XXXXXXXX..",
        "..XXXXXXXX..",
        "..D.D..D.D..",
        "..D.D..D.D..",
    ]),
    "codex": dict(name="CODEX", body="#4FE3C1", dark="#1d7f6a",
        pal={"W": "#E9ECEF", "G": "#9aa3ad", "S": "#0b1a1d", "C": "#4FE3C1"}, sprite=[
        "......C.....",
        "......G.....",
        ".WWWWWWWWWW.",
        ".WSSSSSSSSG.",
        ".WSCSSSSSSG.",
        ".WSSCSSSSSG.",
        ".WSCSSCCCSG.",
        ".WSSSSSSSSG.",
        ".WGGGGGGGGG.",
        "..W......G..",
    ]),
    "gemini": dict(name="GEMINI", body="#7B8CFF", dark="#3c46a8",
        pal={"P": "#D08BFF", "M": "#9C8CFF", "X": "#6F95FF", "B": "#3F7BFF", "W": "#ffffff"}, sprite=[
        ".....PP.....",
        ".....PP.....",
        "....PMMP....",
        "....MMMM....",
        "...MXXXXM...",
        "PMMXWEXWEXXB",
        "BXXXXXXXXXXB",
        "...XXXXXX...",
        "....XXXX....",
        "....BXXB....",
        ".....BB.....",
        ".....BB.....",
    ]),
}
ORDER = ["claude", "codex", "gemini"]

# Each race: task, and per agent a list of (t, progress 0..1) keyframes plus an optional bubble (t0, t1, text).
RACES = [
    dict(task="center the div", winner="claude", plan={
        "claude": ([(0.6, 0), (4.4, 1)], None),
        "codex": ([(0.6, 0), (2.0, .38), (3.4, .38), (5.3, 1)], (2.0, 3.4, "sandbox: denied")),
        "gemini": ([(0.6, 0), (1.6, .3), (3.0, .3), (5.8, 1)], (1.6, 3.0, "reading 1M tokens…")),
    }),
    dict(task="fix the flaky test", winner="codex", plan={
        "claude": ([(0.6, 0), (1.4, .22), (3.0, .22), (5.4, 1)], (1.4, 3.0, "let me plan first…")),
        "codex": ([(0.6, 0), (4.3, 1)], None),
        "gemini": ([(0.6, 0), (3.2, .7), (4.3, .7), (5.6, 1)], (3.2, 4.3, "it passes on my end")),
    }),
    dict(task="migrate to postgres", winner="gemini", plan={
        "claude": ([(0.6, 0), (2.6, .55), (3.9, .55), (5.3, 1)], (2.6, 3.9, "writing the tests…")),
        "codex": ([(0.6, 0), (1.2, .15), (2.8, .15), (5.7, 1)], (1.2, 2.8, "rm -rf? asking first")),
        "gemini": ([(0.6, 0), (4.5, 1)], None),
    }),
]
T = RACE * len(RACES)
samples = [i * DT for i in range(int(round(T / DT)) + 1)]
keys = ";".join(f"{t / T:.4f}" for t in samples)


def interp(frames, t):
    if t <= frames[0][0]:
        return frames[0][1]
    for (t0, p0), (t1, p1) in zip(frames, frames[1:]):
        if t0 <= t <= t1:
            return p0 + (p1 - p0) * (t - t0) / (t1 - t0)
    return frames[-1][1]


def sprite_svg(a, ox, oy):
    out = []
    for r, row in enumerate(a["sprite"]):
        for c, ch in enumerate(row):
            fill = SKY if ch == "E" else a["pal"].get(ch)
            if fill:
                out.append(f'<rect x="{ox + c * U}" y="{oy + r * U}" width="{U}" height="{U}" fill="{fill}"/>')
    return "".join(out)


def anim(attr, vals, discrete=False, kind=None):
    mode = ' calcMode="discrete"' if discrete else ""
    if kind:
        return f'<animateTransform attributeName="transform" type="{kind}" values="{vals}" keyTimes="{keys}" dur="{T}s" repeatCount="indefinite"{mode}/>'
    return f'<animate attributeName="{attr}" values="{vals}" keyTimes="{keys}" dur="{T}s" repeatCount="indefinite"{mode}/>'


def window(t0, t1):
    """opacity track: 1 inside [t0,t1) else 0."""
    return ";".join("1" if t0 <= t < t1 else "0" for t in samples)


parts = []

# backdrop: stars + lanes + finish
for i in range(36):
    parts.append(f'<rect x="{(i * 331) % W}" y="{(i * 53) % 110 + 92}" width="3" height="3" fill="#1c2027"/>')
for y in LANES:
    parts.append(f'<rect x="40" y="{y}" width="{W - 80}" height="4" fill="{LINE}"/>')
    for x in range(60, W - 60, 48):
        parts.append(f'<rect x="{x}" y="{y + 12}" width="18" height="3" fill="#13161b"/>')
# HUD: task + race counter, swapped per race
for i, race in enumerate(RACES):
    t0, t1 = i * RACE, (i + 1) * RACE
    parts.append(f'''<g opacity="0">{anim("opacity", window(t0, t1), True)}
  <text x="48" y="54" font-family="{MONO}" font-size="14" font-weight="700" fill="{DIM}" letter-spacing="3">AGENT ARENA · RACE {i + 1}/{len(RACES)}</text>
  <text x="48" y="84" font-family="{MONO}" font-size="24" font-weight="700" fill="{WHITE}">task: {race["task"]}</text>
</g>''')

# agents
for lane, key in zip(LANES, ORDER):
    a = AGENTS[key]
    sh = len(a["sprite"]) * U
    xs, bob = [], []
    for t in samples:
        i = min(int(t // RACE), len(RACES) - 1)
        local = t - i * RACE
        frames = RACES[i]["plan"][key][0]
        p = interp(frames, local)
        moving = frames[0][0] < local < frames[-1][0] and any(
            t0 <= local < t1 and p1 != p0 for (t0, p0), (t1, p1) in zip(frames, frames[1:]))
        won = RACES[i]["winner"] == key and local > frames[-1][0] + 0.1 and local < RACE - 0.4
        hop = -12 if (moving and int(local / 0.12) % 2) else 0
        if won:
            hop = -18 if int(local / 0.2) % 2 else 0
        xs.append(f"{START + p * (FINISH - START):.1f} {hop}")
    import random
    rnd = random.Random(key)
    bars = []
    for row in range(5):
        x = START
        y = lane - 62 + row * 11
        while x < FINISH + SW:
            w = rnd.choice([12, 18, 24, 36, 48, 60])
            if rnd.random() > 0.18:
                bars.append(f'<rect x="{x}" y="{y}" width="{w}" height="5" fill="{a["body"]}" opacity="{rnd.choice([0.18, 0.28, 0.4])}"/>')
            x += w + 6
    shift = ";".join(f"{float(v.split()[0]) - START:.1f} 0" for v in xs)
    parts.append(f'<g>{"".join(bars)}</g>')
    parts.append(f'<rect x="{START + 10}" y="{lane - 70}" width="{FINISH + SW - START}" height="66" fill="{SKY}">{anim(None, shift, kind="translate")}</rect>')
    parts.append(f'<text x="44" y="{lane - 14}" font-family="{MONO}" font-size="13" font-weight="700" fill="{a["body"]}" letter-spacing="2">{a["name"]}</text>')
    parts.append(f'<g>{anim(None, ";".join(xs), kind="translate")}<g>{sprite_svg(a, 0, lane - sh)}</g>')
    # bubbles ride along with the sprite
    for i, race in enumerate(RACES):
        bub = race["plan"][key][1]
        if not bub:
            continue
        b0, b1, text = bub
        bw = len(text) * 10.8 + 24
        parts.append(f'''<g opacity="0">{anim("opacity", window(i * RACE + b0, i * RACE + b1), True)}
  <rect x="-6" y="{lane - sh - 48}" width="{bw:.0f}" height="34" fill="{WHITE}"/>
  <rect x="12" y="{lane - sh - 14}" width="12" height="6" fill="{WHITE}"/>
  <text x="6" y="{lane - sh - 25}" font-family="{MONO}" font-size="18" fill="{SKY}">{text}</text>
</g>''')
    parts.append("</g>")

fx = FINISH + SW + 8
parts.append(f'<text x="{fx + 12}" y="{LANES[0] - 84}" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700" fill="{WHITE}">main</text>')
for r in range(0, LANES[-1] + 4 - (LANES[0] - 60), 12):
    for c in range(2):
        if (r // 12 + c) % 2 == 0:
            parts.append(f'<rect x="{fx + c * 12}" y="{LANES[0] - 60 + r}" width="12" height="12" fill="{WHITE}"/>')

# winner banner
for i, race in enumerate(RACES):
    a = AGENTS[race["winner"]]
    t_fin = race["plan"][race["winner"]][0][-1][0]
    msg = f"MERGED BY {a['name']}"
    parts.append(f'''<g opacity="0">{anim("opacity", window(i * RACE + t_fin + 0.1, (i + 1) * RACE - 0.4), True)}
  <rect x="{W - 48 - 300}" y="40" width="300" height="52" fill="{a["body"]}"/>
  <rect x="{W - 48 - 294}" y="92" width="300" height="6" fill="{a["dark"]}"/>
  <rect x="{W - 48}" y="46" width="6" height="52" fill="{a["dark"]}"/>
  <text x="{W - 48 - 150}" y="74" text-anchor="middle" font-family="{MONO}" font-size="22" font-weight="700" fill="{SKY}">{msg} ✓</text>
</g>''')

parts.append(f'<text x="{W - 48}" y="{H - 22}" text-anchor="end" font-family="{MONO}" font-size="13" fill="#3f444c">agents leave code behind them. first to main wins.</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges" role="img" aria-label="Agent Arena: Claude, Codex and Gemini race to finish coding tasks.">
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="{SKY}" stroke="#1b1e24"/>
<clipPath id="card"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="15"/></clipPath>
<g clip-path="url(#card)">{"".join(parts)}</g>
</svg>
'''
open(os.path.join(ROOT, "arena.svg"), "w").write(svg)

# vote buttons
for key in ORDER:
    a = AGENTS[key]
    bw, bh = 360, 120
    btn = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{bw}" height="{bh}" viewBox="0 0 {bw} {bh}" shape-rendering="crispEdges" role="img" aria-label="Back {a['name']}">
<rect x="6" y="6" width="{bw - 6}" height="{bh - 6}" fill="{a['dark']}"/>
<rect x="0" y="0" width="{bw - 6}" height="{bh - 6}" fill="{SKY}" stroke="{a['body']}" stroke-width="4"/>
{sprite_svg(a, 20, 28)}
<text x="104" y="52" font-family="{MONO}" font-size="13" font-weight="700" fill="{DIM}" letter-spacing="3">BACK</text>
<text x="104" y="82" font-family="{MONO}" font-size="28" font-weight="700" fill="{a['body']}">{a['name']}</text>
<text x="{bw - 30}" y="82" text-anchor="end" font-family="{MONO}" font-size="22" font-weight="700" fill="{WHITE}">▶</text>
</svg>
'''
    open(os.path.join(ROOT, f"vote-{key}.svg"), "w").write(btn)
print("arena loop", T, "s")

"""Records a vote and redraws assets/scoreboard.svg. Usage: vote.py <agent|''> <github-user>"""
import json, os, sys
from html import escape

ROOT = os.path.join(os.path.dirname(__file__), "..")
DB = os.path.join(ROOT, "votes.json")
AGENTS = {"claude": ("CLAUDE", "#D97757"), "codex": ("CODEX", "#EDEDED"), "gemini": ("GEMINI", "#7B8CFF")}
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

data = json.load(open(DB)) if os.path.exists(DB) else {"votes": {k: 0 for k in AGENTS}, "last": []}
agent, user = (sys.argv[1:3] + ["", ""])[:2]
if agent in AGENTS:
    data["votes"][agent] += 1
    data["last"] = ([{"agent": agent, "user": user}] + data["last"])[:3]
json.dump(data, open(DB, "w"), indent=2)

W, H, U = 1200, 250, 6
votes = data["votes"]
total = sum(votes.values())
top = max(votes.values()) or 1
leader = max(votes, key=votes.get) if total else None
rows = []
for i, (k, (name, color)) in enumerate(AGENTS.items()):
    y = 64 + i * 46
    bar = int((votes[k] / top) * 760) // U * U if total else 0
    crown = " ♛" if k == leader else ""
    rows.append(f'<text x="48" y="{y + 20}" font-family="{MONO}" font-size="16" font-weight="700" fill="{color}" letter-spacing="2">{name}{crown}</text>'
                f'<rect x="230" y="{y + 4}" width="760" height="24" fill="#13161b"/>'
                f'<rect x="230" y="{y + 4}" width="{bar}" height="24" fill="{color}"/>'
                f'<text x="{W - 48}" y="{y + 22}" text-anchor="end" font-family="{MONO}" font-size="20" font-weight="700" fill="#F2F0EA">{votes[k]}</text>')
recent = "  ·  ".join(f"@{escape(v['user'])} → {AGENTS[v['agent']][0].lower()}" for v in data["last"]) or "no votes yet. be the first."
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges" role="img" aria-label="Scoreboard: {', '.join(f'{AGENTS[k][0]} {v}' for k, v in votes.items())}">
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="#060709" stroke="#1b1e24"/>
<text x="48" y="42" font-family="{MONO}" font-size="14" font-weight="700" fill="#5b616b" letter-spacing="3">SCOREBOARD · {total} VOTES</text>
{"".join(rows)}
<text x="48" y="{H - 24}" font-family="{MONO}" font-size="14" fill="#5b616b">latest: {recent}</text>
</svg>
'''
open(os.path.join(ROOT, "assets", "scoreboard.svg"), "w").write(svg)
print(json.dumps(votes))

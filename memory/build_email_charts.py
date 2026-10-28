#!/usr/bin/env python3
"""
Chart PNGs sized for an EMAIL BODY.

Different from the dashboard charts on purpose: an email body is ~700 px wide, so
these are drawn at 700 px with larger relative fonts (the dashboard's 1034 px
version becomes unreadable once Outlook scales it down). Palette-quantised,
because every KB has to travel through the agent's context to reach the compose
window -- Pictures > OneDrive opens a native file dialog we cannot drive, and
file_upload is unavailable in Cowork.
"""
import io, base64, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from build_hover_charts import S, dates, ext, NAMES, SUB, seg, X, NAVY, ORANGE, GREEN, PURPLE, TEAL, BAR

DPI = 100
FIGSIZE = (7.0, 3.05)          # -> 700 x 305 px
lbl = [d[5:] for d in dates]
F = 1.42                       # font scale vs the dashboard version


def plot(ax, vals, col, style, lw, ms):
    for r in seg(vals):
        xs = [a for a, _ in r]; ys = [b for _, b in r]
        if len(xs) == 1:
            ax.plot(xs, ys, 'o', color=col, ms=ms)
        else:
            ax.plot(xs, ys, style, color=col, lw=lw)


def lim(ax, vals, padf=0.18, minpad=0.3):
    v = [x for x in vals if x is not None]
    if not v:
        ax.set_ylim(0, 1); return
    lo, hi = min(v), max(v)
    pad = max(minpad, (hi - lo) * padf)
    ax.set_ylim(lo - pad, hi + pad)


def draw(code, colors=64):
    d = S[code]
    fig, axP = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.subplots_adjust(left=0.175, right=0.775, top=0.79, bottom=0.15)
    axPct = axP.twinx(); axPct.spines['left'].set_position(('axes', -0.135))
    axPct.yaxis.set_label_position('left'); axPct.yaxis.tick_left()
    axPct.spines['right'].set_visible(False)
    axV = axP.twinx()
    axC = axP.twinx(); axC.spines['right'].set_position(('axes', 1.135))

    axV.bar(X, [v if v is not None else 0 for v in d['vol']], width=0.62, color=BAR, zorder=1)
    plot(axV, d['stton'], GREEN, '--', 1.7, 4)
    plot(axPct, d['starch'], ORANGE, '--', 1.7, 4)
    rx = [i for i, v in enumerate(d['rec']) if v is not None]
    axPct.plot(rx, [d['rec'][i] for i in rx], 'o', color=TEAL, ms=3.6)
    plot(axC, d['cag'], PURPLE, '-', 1.8, 4)
    plot(axP, d['price'], NAVY, '-', 2.5, 4.6)
    if code == 'PM':
        for i, v in ext.items():
            axP.plot([i], [v], '*', color='#d73027', ms=12)

    pr = list(d['price']) + ([v for v in ext.values()] if code == 'PM' else [])
    lim(axP, pr, 0.22, 0.12)
    lim(axC, d['cag'], 0.15, 0.5)
    lim(axPct, d['starch'] + d['rec'], 0.22, 2.0)
    tons = [v for v in d['vol'] + d['stton'] if v is not None]
    axV.set_ylim(0, max(1, max(tons) if tons else 1) * 1.35)

    axP.set_xlim(-0.8, len(dates) - 0.2)
    tk = [i for i in X if i % 5 == 0 or i == len(X) - 1]
    axP.set_xticks(tk); axP.set_xticklabels([lbl[i] for i in tk], fontsize=7.5 * F * 0.82, color='#5b6470')
    axP.set_ylabel('Price THB/kg', fontsize=8 * F * 0.9, color=NAVY, labelpad=2)
    axPct.set_ylabel('%Starch / %Rec', fontsize=7.5 * F * 0.85, color=ORANGE, labelpad=2)
    axV.set_ylabel('tons', fontsize=8 * F * 0.9, color='#8b9199', labelpad=2)
    axC.set_ylabel('CAG THB/kg', fontsize=8 * F * 0.9, color=PURPLE, labelpad=2)
    axP.tick_params(axis='y', labelsize=7.5 * F * 0.86, colors=NAVY)
    axPct.tick_params(axis='y', labelsize=7 * F * 0.86, colors=ORANGE)
    axV.tick_params(axis='y', labelsize=7.5 * F * 0.86, colors='#8b9199')
    axC.tick_params(axis='y', labelsize=7.5 * F * 0.86, colors=PURPLE)
    axP.grid(axis='y', color='#eceef1', lw=0.9); axP.set_axisbelow(True)
    for a in (axP, axPct, axV, axC):
        a.spines['top'].set_visible(False)
    axP.spines['left'].set_color(NAVY); axPct.spines['left'].set_color(ORANGE)
    axV.spines['right'].set_color('#c7cbd1'); axC.spines['right'].set_color(PURPLE)
    axP.spines['bottom'].set_color('#c7cbd1')
    axP.set_title(NAMES[code], loc='left', fontsize=11.5 * F * 0.86, fontweight='bold', color=NAVY, pad=20)
    if SUB[code]:
        axP.text(0, 1.045, SUB[code], transform=axP.transAxes, fontsize=7.8 * F * 0.82, color='#9ca3af')

    buf = io.BytesIO(); fig.savefig(buf, format='png'); plt.close(fig)
    im = Image.open(buf).convert('RGB')
    q = im.quantize(colors=colors, method=Image.MEDIANCUT)
    o = io.BytesIO(); q.save(o, 'PNG', optimize=True)
    return o.getvalue() if len(o.getvalue()) < len(buf.getvalue()) else buf.getvalue()


if __name__ == '__main__':
    out, tot = {}, 0
    for c in ['TN', 'TKT', 'PM', 'MS', 'TDC', 'TWIC']:
        raw = draw(c)
        b = base64.b64encode(raw).decode()
        out[c] = b
        tot += len(b)
        open('mail_%s.b64' % c, 'w').write(b)
        print('%-5s %4d KB png  %4d KB b64' % (c, len(raw) // 1024, len(b) // 1024))
    json.dump(out, open('mail_charts.json', 'w'))
    print('TOTAL b64 %d KB across 6 images' % (tot // 1024))

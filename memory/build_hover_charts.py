#!/usr/bin/env python3
"""
Daily root dashboard chart builder.

Produces, for each of the 6 plants:
  * an INTERACTIVE inline SVG  -- hover a date to see every value for that date.
    Uses NOTHING but SVG + CSS (:hover + sibling selector). No <script>, no CDN,
    so it survives SharePoint / OneDrive preview, which strips and blocks scripts.
  * a PNG raster of the same chart -- needed for the email body, where no client
    renders CSS :hover anyway.

Axis convention (do not change without telling Por -- CAG had an outlier of 61.78
once and flattened the price line when they shared one axis):
  inner left  = Price THB/kg          navy   solid  thick
  outer left  = %Starch (dashed) + %Recovery (dots)
  inner right = tons: volume (grey bars) + starch output (green dashed)
  outer right = CAG THB/kg            purple solid
"""
import csv, io, base64, json, re, html

import os; M = os.path.dirname(os.path.abspath(__file__)) + '/'
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

DPI = 110
FIGSIZE = (9.4, 3.9)

# ---------------------------------------------------------------- load data
rows = list(csv.DictReader(open(M + 'root-price-history.csv')))
dates = sorted(set(r['date'] for r in rows))
lbl = [d[5:] for d in dates]


def f(v):
    try:
        return float(v)
    except Exception:
        return None


S = {}
for p in ['TN', 'TKT', 'PM', 'MS', 'TDC', 'TWIC']:
    m = {r['date']: r for r in rows if r['plant'] == p}
    d = {k: [] for k in ['price', 'vol', 'starch', 'cag', 'rec', 'stton']}
    for dt in dates:
        r = m.get(dt, {})
        pr, vo, st = f(r.get('price_thb_kg')), f(r.get('volume_tons')), f(r.get('starch_pct'))
        cg, rc = f(r.get('cag_thb_kg')), f(r.get('recovery_pct'))
        d['price'].append(pr)
        d['vol'].append(vo)
        d['starch'].append(st)
        d['cag'].append(cg)
        d['rec'].append(rc)
        d['stton'].append(round(vo * st / 100 * rc / 100, 1) if (vo and st and rc) else None)
    S[p] = d

ext = {}
for r in csv.DictReader(open(M + 'root-price-external.csv')):
    if r['date'] in dates:
        ext[dates.index(r['date'])] = float(r['price_thb_kg'])

NAMES = {'TN': 'TN  ·  Udon Thani', 'TKT': 'TKT  ·  Kalasin',
         'PM': 'PM  ·  Nakhon Ratchasima', 'MS': 'MS  ·  Tak',
         'TDC': 'TDC  ·  Rayong', 'TWIC': 'TWIC  ·  Oddar Meanchey, Cambodia'}
SUB = {'TN': '', 'TKT': '', 'PM': 'red stars = Nettathai reference price (Phimai)',
       'MS': 'no purchases in this 30-day window', 'TDC': '',
       'TWIC': 'separate legal entity — excluded from Thailand total'}

NAVY, ORANGE, GREEN, PURPLE, TEAL, BAR = '#0b2540', '#e0821f', '#1a9850', '#8e44ad', '#0e8aa8', '#d6d9de'
X = list(range(len(dates)))


def seg(v):
    runs, cur = [], []
    for i, x in enumerate(v):
        if x is None:
            if cur:
                runs.append(cur); cur = []
        else:
            cur.append((i, x))
    if cur:
        runs.append(cur)
    return runs


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


def figure(code):
    """Draw the chart. Returns (fig, axPrice)."""
    d = S[code]
    fig, axP = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.subplots_adjust(left=0.16, right=0.795, top=0.80, bottom=0.16)
    axPct = axP.twinx(); axPct.spines['left'].set_position(('axes', -0.115))
    axPct.yaxis.set_label_position('left'); axPct.yaxis.tick_left()
    axPct.spines['right'].set_visible(False)
    axV = axP.twinx()
    axC = axP.twinx(); axC.spines['right'].set_position(('axes', 1.10))

    axV.bar(X, [v if v is not None else 0 for v in d['vol']], width=0.62, color=BAR, zorder=1)
    plot(axV, d['stton'], GREEN, '--', 1.6, 3.5)
    plot(axPct, d['starch'], ORANGE, '--', 1.6, 3.5)
    rx = [i for i, v in enumerate(d['rec']) if v is not None]
    axPct.plot(rx, [d['rec'][i] for i in rx], 'o', color=TEAL, ms=3.2)
    plot(axC, d['cag'], PURPLE, '-', 1.7, 3.5)
    plot(axP, d['price'], NAVY, '-', 2.3, 4.2)
    if code == 'PM':
        for i, v in ext.items():
            axP.plot([i], [v], '*', color='#d73027', ms=11)

    pr = list(d['price']) + ([v for v in ext.values()] if code == 'PM' else [])
    lim(axP, pr, 0.22, 0.12)
    lim(axC, d['cag'], 0.15, 0.5)
    lim(axPct, d['starch'] + d['rec'], 0.22, 2.0)
    tons = [v for v in d['vol'] + d['stton'] if v is not None]
    axV.set_ylim(0, max(1, max(tons) if tons else 1) * 1.35)

    axP.set_xlim(-0.8, len(dates) - 0.2)
    tk = [i for i in X if i % 3 == 0 or i == len(X) - 1]
    axP.set_xticks(tk); axP.set_xticklabels([lbl[i] for i in tk], fontsize=7.5, color='#6b7280')
    axP.set_ylabel('Price  THB/kg', fontsize=8, color=NAVY, labelpad=2)
    axPct.set_ylabel('%Starch / %Recovery', fontsize=7.5, color=ORANGE, labelpad=2)
    axV.set_ylabel('tons', fontsize=8, color='#8b9199', labelpad=2)
    axC.set_ylabel('CAG  THB/kg', fontsize=8, color=PURPLE, labelpad=2)
    axP.tick_params(axis='y', labelsize=7.5, colors=NAVY)
    axPct.tick_params(axis='y', labelsize=7, colors=ORANGE)
    axV.tick_params(axis='y', labelsize=7.5, colors='#8b9199')
    axC.tick_params(axis='y', labelsize=7.5, colors=PURPLE)
    axP.grid(axis='y', color='#eceef1', lw=0.8); axP.set_axisbelow(True)
    for a in (axP, axPct, axV, axC):
        a.spines['top'].set_visible(False)
    axP.spines['left'].set_color(NAVY); axPct.spines['left'].set_color(ORANGE)
    axV.spines['right'].set_color('#c7cbd1'); axC.spines['right'].set_color(PURPLE)
    axP.spines['bottom'].set_color('#c7cbd1')
    axP.set_title(NAMES[code], loc='left', fontsize=11.5, fontweight='bold', color=NAVY, pad=22)
    if SUB[code]:
        axP.text(0, 1.035, SUB[code], transform=axP.transAxes, fontsize=7.8, color='#9ca3af')
    return fig, axP


# ------------------------------------------------------- hover overlay maths
def hover_overlay(code, fig, axP):
    """Build the SVG <g> that adds a hover band + value readout per date."""
    d = S[code]
    k = 72.0 / DPI                      # display px -> SVG user units
    H = FIGSIZE[1] * DPI * k            # svg height
    W = FIGSIZE[0] * DPI * k

    xs = [axP.transData.transform((i, 0))[0] * k for i in X]
    y0 = H - axP.transData.transform((0, axP.get_ylim()[0]))[1] * k   # plot bottom
    y1 = H - axP.transData.transform((0, axP.get_ylim()[1]))[1] * k   # plot top
    top, bot = min(y0, y1), max(y0, y1)
    step = (xs[1] - xs[0]) if len(xs) > 1 else 10.0

    ROWH, PADX, PADY = 11.0, 8.0, 7.0
    parts = []
    for i, dt in enumerate(dates):
        lines = [('Price', d['price'][i], ' THB/kg', NAVY),
                 ('Volume', d['vol'][i], ' t', '#7b828c'),
                 ('%Starch', d['starch'][i], '%', ORANGE),
                 ('%Recovery', d['rec'][i], '%', TEAL),
                 ('CAG', d['cag'][i], ' THB/kg', PURPLE),
                 ('Starch out', d['stton'][i], ' t', GREEN)]
        if code == 'PM' and i in ext:
            lines.append(('Nettathai', ext[i], ' THB/kg', '#d73027'))

        body = []
        novol = d['vol'][i] in (0, 0.0) and d['price'][i] is None
        for nm, val, unit, col in lines:
            if val is None:
                if novol:
                    continue
                txt, tcol = 'pending', '#b0b6bd'
            else:
                txt = ('%.2f' % val if unit.startswith(' THB') else
                       ('%,.0f'.replace(',', '') % val if unit == ' t' and val >= 100 else
                        ('%.0f' % val if unit == ' t' and float(val).is_integer() else '%.1f' % val))
                       if unit == ' t' else '%.2f' % val) if unit != '%' else '%.2f' % val
                if unit == ' t':
                    txt = '{:,.0f}'.format(val) if float(val).is_integer() else '{:,.1f}'.format(val)
                txt += unit
                tcol = col
            body.append((nm, txt, tcol))
        if novol:
            body.append(('', 'no purchase', '#9ca3af'))
        if code == 'TWIC' and d['rec'][i] == 0 and d['vol'][i]:
            body.append(('', 'mill did not run', '#9ca3af'))

        boxw = 118.0
        boxh = PADY * 2 + ROWH * (len(body) + 1)
        # flip the box to the left when close to the right edge
        bx = xs[i] + 9 if xs[i] + 9 + boxw < W - 2 else xs[i] - 9 - boxw
        by = max(2.0, min(top + 4, bot - boxh - 2))

        t = ['<g class="tt" aria-hidden="true">',
             '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" '
             'fill="#ffffff" stroke="#0b2540" stroke-opacity="0.22"/>' % (bx, by, boxw, boxh),
             '<text x="%.1f" y="%.1f" class="tth">%s</text>' % (bx + PADX, by + PADY + 8, dt)]
        for j, (nm, txt, tcol) in enumerate(body):
            yy = by + PADY + 8 + ROWH * (j + 1)
            if nm:
                t.append('<text x="%.1f" y="%.1f" class="ttk">%s</text>' % (bx + PADX, yy, nm))
            t.append('<text x="%.1f" y="%.1f" class="ttv" fill="%s">%s</text>'
                     % (bx + boxw - PADX, yy, tcol, html.escape(txt)))
        t.append('</g>')

        parts.append(
            '<g class="hv"><rect class="hb" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>%s</g>'
            % (xs[i] - step / 2, top, step, bot - top, ''.join(t)))

    css = (
        '<style type="text/css"><![CDATA['
        '.hb{fill:#0b2540;fill-opacity:0;cursor:crosshair}'
        '.hv:hover .hb{fill-opacity:0.055}'
        '.tt{opacity:0;pointer-events:none}'
        '.hv:hover .tt{opacity:1}'
        '.tth{font:600 8.2px Aptos,Calibri,Segoe UI,Arial,sans-serif;fill:#0b2540}'
        '.ttk{font:7.6px Aptos,Calibri,Segoe UI,Arial,sans-serif;fill:#6b7280}'
        '.ttv{font:600 7.9px Aptos,Calibri,Segoe UI,Arial,sans-serif;text-anchor:end}'
        ']]></style>')
    return css + '<g class="hoverlayer">' + ''.join(parts) + '</g>'


def build(code):
    fig, axP = figure(code)

    png = io.BytesIO(); fig.savefig(png, format='png')
    svg = io.BytesIO(); fig.savefig(svg, format='svg')
    overlay = hover_overlay(code, fig, axP)
    plt.close(fig)

    s = svg.getvalue().decode('utf-8')
    s = s[s.index('<svg'):]                                  # drop xml/doctype preamble
    s = re.sub(r'<svg ', '<svg preserveAspectRatio="xMidYMid meet" ', s, count=1)
    s = re.sub(r'\swidth="[\d.]+pt"\s+height="[\d.]+pt"', ' width="100%" ', s, count=1)
    s = s.replace('</svg>', overlay + '</svg>')
    return s, base64.b64encode(png.getvalue()).decode()


if __name__ == '__main__':
    out = {}
    for c in ['TN', 'TKT', 'PM', 'MS', 'TDC', 'TWIC']:
        s, p = build(c)
        out[c] = {'svg': s, 'png': p}
    json.dump(out, open('charts.json', 'w'))
    print('built', {k: (len(v['svg']) // 1000, len(v['png']) // 1000) for k, v in out.items()})
    print('hover bands per chart:', out['TN']['svg'].count('class="hb"'))
    print('script tags:', sum(v['svg'].count('<script') for v in out.values()))

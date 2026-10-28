# One-picture summary for the CEO: where Indonesian accounts sit on each reaction's product GP/kg ladder (YTD Sep-26)
# Usage: python tier_chart.py <dir with tdc_cust_rx.csv> <out.png>
import sys, csv, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
S, OUT = sys.argv[1], sys.argv[2]
FLOOR = {'PO-XL': 4.0, 'XL': 2.0, 'PO': 4.0, 'AC': 7.0, 'Others': 4.0}
TARGET = {'PO-XL': 6.0, 'XL': 3.2, 'PO': 5.5, 'AC': 9.5, 'Others': 6.0}
CAP = {'PO-XL': 2000, 'XL': 750, 'PO': 800, 'AC': 250, 'Others': 600}
RX = ['PO-XL', 'XL', 'PO', 'AC', 'Others']
SHORT = {'PT.INDO ASIA TIRTA MANUNGGAL': 'Indo Asia Tirta', 'PT. CHAROEN POKPHAND INDONESIA': 'CP Indonesia', 'PT. JAPFA FOOD INDONESIA GEDUNG GRAHA PRABA SAMANTA': 'Japfa',
         'PT. SO GOOD FOOD GEDUNG GRAHA PRABA SAMANTA': 'So Good Food', 'PT THAI WAH INDONESIA': 'TWIN (interco)'}
rows = [r for r in csv.DictReader(open(f'{S}/tdc_cust_rx.csv', encoding='utf-8')) if r['reaction'] in RX]
for r in rows:
    r['t'] = float(r['tons_ytd26']); r['gp'] = (float(r['ns_thb']) - float(r['product_cost'])) / (r['t'] * 1000) if r['t'] else None; r['indo'] = r['indonesia'] == '1'
GREY, INDO, DARK, LINE = '#b8bcc2', '#e4572e', '#14213d', '#6b7280'
plt.rcParams['font.family'] = ['Arial', 'DejaVu Sans']
fig, axes = plt.subplots(1, len(RX), figsize=(15, 6.2), sharey=False)
fig.subplots_adjust(left=0.05, right=0.99, top=0.80, bottom=0.17, wspace=0.28)
for ax, g in zip(axes, RX):
    rs = [r for r in rows if r['reaction'] == g and r['t'] >= 5 and r['gp'] is not None]
    tot = sum(r['t'] for r in rows if r['reaction'] == g); indo_t = sum(r['t'] for r in rows if r['reaction'] == g and r['indo'])
    util = tot / (CAP[g] * 9)
    ymin = min(-1, min(r['gp'] for r in rs) - 0.5); ymax = max(TARGET[g] + 4, min(max(r['gp'] for r in rs), 18) + 1)
    ax.add_patch(Rectangle((-0.5, ymin), 1.0, FLOOR[g] - ymin, color='#f6dcd4', zorder=0))
    ax.add_patch(Rectangle((-0.5, FLOOR[g]), 1.0, TARGET[g] - FLOOR[g], color='#fbf0c6', zorder=0))
    ax.add_patch(Rectangle((-0.5, TARGET[g]), 1.0, ymax - TARGET[g], color='#e2efda', zorder=0))
    ax.axhline(FLOOR[g], color=LINE, lw=1, ls='--', zorder=1); ax.axhline(TARGET[g], color=LINE, lw=1, ls=':', zorder=1)
    ax.text(0.48, FLOOR[g], f'floor {FLOOR[g]:.1f}', ha='right', va='bottom', fontsize=8, color=LINE)
    ax.text(0.48, TARGET[g], f'target {TARGET[g]:.1f}', ha='right', va='bottom', fontsize=8, color=LINE)
    # jittered x for the rest, deterministic
    others = sorted([r for r in rs if not r['indo']], key=lambda r: -r['t'])
    for i, r in enumerate(others):
        x = -0.22 + 0.44 * ((i * 0.6180339887) % 1.0)
        ax.scatter(x, min(r['gp'], 18), s=12 + 900 * r['t'] / 2500, color=GREY, alpha=0.75, edgecolor='white', linewidth=0.5, zorder=2)
    ids = sorted([r for r in rs if r['indo']], key=lambda r: -r['t'])
    for i, r in enumerate(ids):
        x = 0.0 if len(ids) == 1 else -0.18 + 0.36 * i / (len(ids) - 1)
        ax.scatter(x, r['gp'], s=12 + 900 * r['t'] / 2500, color=INDO, alpha=0.9, edgecolor=DARK, linewidth=0.8, zorder=3)
        nm = SHORT.get(r['customer'], r['customer'][:16])
        ax.annotate(f'{nm}\n{r["gp"]:.1f} · {r["t"]:,.0f} t', (x, r['gp']), xytext=(0, -14 if i % 2 == 0 else 12), textcoords='offset points', ha='center', va='top' if i % 2 == 0 else 'bottom', fontsize=7.5, color=DARK, fontweight='bold', zorder=4)
    ax.set_xlim(-0.5, 0.5); ax.set_ylim(ymin, ymax); ax.set_xticks([])
    ax.set_title(f'{g}\n{tot:,.0f} t · Indonesia {indo_t/tot*100:.0f}%', fontsize=11, fontweight='bold', color=DARK)
    ax.text(0, ymin - (ymax - ymin) * 0.06, f'utilisation {util*100:.0f}%' + ('  (full)' if util >= 0.8 else '  (spare)'), ha='center', va='top', fontsize=9, color=INDO if util >= 0.8 else '#2a7d4f', fontweight='bold', transform=ax.transData, clip_on=False)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    ax.spines['bottom'].set_visible(False); ax.tick_params(axis='y', labelsize=8, colors=LINE); ax.spines['left'].set_color(LINE)
axes[0].set_ylabel('Product GP, THB per kg (YTD Sep-26)', fontsize=9, color=DARK)
fig.suptitle('Indonesia sits at the bottom of the GP/kg ladder in every reaction it buys', x=0.05, ha='left', fontsize=15, fontweight='bold', color=DARK)
fig.text(0.05, 0.875, 'Orange = Indonesian accounts (direct export and PT Thai Wah Indonesia intercompany) · grey = all other TDC customers with ≥ 5 t · bubble area = YTD Sep-26 tonnes · '
         'bands = HVA tier: red below floor, amber floor to target, green at/above target · product GP = net sales − actual cost − F&I (HVA tracker basis)', fontsize=8.5, color=LINE)
fig.text(0.05, 0.03, 'Read: where the reactor is full (PO-XL 86%, XL 141% of nameplate) Indonesian volume displaces 6–7 THB/kg business and is not a fixed-cost play; where the reactor is spare (PO, AC, Others) volume does absorb idle cost (0.6–1.0 THB/kg) '
         'but should not price below the floor. Capacity per reaction from the Baseline sheet — confirm with the plant (XL above 100%). Source: TDC Profitability data_Actual, Jan–Sep 2026.', fontsize=8, color=LINE, wrap=True)
fig.savefig(OUT, dpi=200, facecolor='white')
print('saved', OUT)

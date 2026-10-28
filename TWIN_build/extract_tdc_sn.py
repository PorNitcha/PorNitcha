# Export TDC data_Actual (ALL customers) to tdc_sn.csv by month x segment x customer x SN for the Indonesia-portfolio benchmarks.
# segment: 'TWIN' (intercompany PT THAI WAH INDONESIA) | 'Indonesia direct' (TDC export to Indonesia, customer level) | 'Non-Indonesia' (everything else, aggregated per SN)
# Usage: python extract_tdc_sn.py <tdc.xlsx> <out_dir>
import sys, csv, openpyxl
from collections import defaultdict
src, out = sys.argv[1], sys.argv[2]
mo = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
wb = openpyxl.load_workbook(src, read_only=True, data_only=True); ws = wb['data_Actual']
agg = defaultdict(lambda: defaultdict(float)); names = {}
def f(x):
    try: return float(x or 0)
    except: return 0.0
for r in ws.iter_rows(min_row=2, values_only=True):
    if r[0] is None: continue
    m = '%s-%02d' % (r[47][-4:], mo[r[46]]); cust = str(r[51] or '').strip(); country = str(r[53] or '').strip(); sn = str(r[57] or '').strip(); tn = str(r[60] or '').strip()
    if cust == 'PT THAI WAH INDONESIA': seg, ck = 'TWIN', 'PT THAI WAH INDONESIA (intercompany)'
    elif country == 'Indonesia': seg, ck = 'Indonesia direct', cust
    else: seg, ck = 'Non-Indonesia', '(all non-Indonesia customers)'
    d = agg[(m, seg, ck, sn)]
    d['t'] += f(r[63]); d['ns'] += f(r[65]); d['af'] += f(r[31]); d['fi'] += f(r[76]); d['idle'] += f(r[77]); d['oadj'] += f(r[78]); d['ppa'] += f(r[79])
    names[sn] = tn
with open(f'{out}/tdc_sn.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['month', 'year', 'month_num', 'quarter', 'segment', 'customer', 'sn', 'trade_name', 'tons', 'ns_thb', 'af', 'fi', 'idle', 'oadj', 'ppa'])
    for (m, seg, ck, sn), d in sorted(agg.items()):
        w.writerow([m, m[:4], int(m[5:]), f"{m[:4]}Q{(int(m[5:]) - 1) // 3 + 1}", seg, ck, sn, names[sn], d['t'], d['ns'], d['af'], d['fi'], d['idle'], d['oadj'], d['ppa']])
print('rows', len(agg), 'segments', sorted(set(k[1] for k in agg)), 'Indonesia direct customers', sorted(set(k[2] for k in agg if k[1] == 'Indonesia direct')))

# Export TDC data_Actual (all customers) to a flat CSV for the TWIT table: month, customer, country, SN, trade name, reaction group, tonnes and cost lines.
# Usage: python extract_tdc_rows.py <tdc.xlsx> <out.csv>
import sys, csv, openpyxl
src, out = sys.argv[1], sys.argv[2]
mo = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
def f(x):
    try: return float(x or 0)
    except: return 0.0
ws = openpyxl.load_workbook(src, read_only=True, data_only=True)['data_Actual']
n = 0
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['month', 'year', 'm', 'cust', 'country', 'sn', 'trade', 'rg', 't', 'ns', 'af', 'fi', 'idle', 'oadj', 'ppa'])
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[0] is None: continue
        y, m = int(str(r[47])[-4:]), mo[r[46]]
        w.writerow(['%d-%02d' % (y, m), y, m, str(r[51] or '').strip(), str(r[53] or '').strip(), str(r[57] or '').strip(), str(r[60] or '').strip(), str(r[59] or '').strip(),
                    f(r[63]), f(r[65]), f(r[31]), f(r[76]), f(r[77]), f(r[78]), f(r[79])]); n += 1
print('rows', n)

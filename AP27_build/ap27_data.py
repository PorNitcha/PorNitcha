import json, sys
src = r'C:\Users\NitchaSuwongtham\THAIWAH\Commercial Finance - General\2026\AI\FC\comparison-data.json'
d = json.load(open(src, encoding='utf-8'))
S = {'2025': '2025', 'AP26': 'AP2026', 'LE26': 'LE2026 (9+3)', 'AP27': 'AP2027 Board', 'AP28': 'AP2028 Board'}
ENT = ['TWPC', 'Starch', 'StarchTH', 'Total CN', 'TWIT', 'TWFZ', 'TWIC', 'Total VN', 'TNT', 'VTC', 'HVA', 'TDC', 'TDC2.0',
       'TWIN', 'TWII', 'ElimH', 'Waxy', 'Foods', 'FoodTH&WG', 'FoodTH', 'Food Dom', 'Food Export', 'FoodWG', 'FoodVN',
       'NBG', 'BioPlastic', 'ElimBU', 'Corp']
out = {}
for b in d['blocks']:
    t = b['title']; out[t] = {}
    for r in b['rows']:
        lab = r['label'].strip()
        if lab == 'ElimHVA': lab = 'ElimH'
        if lab in ENT and lab not in out[t]:
            out[t][lab] = {k: r['abs']['fy'].get(v) for k, v in S.items()}
json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def g(b, e, s):
    v = out[b].get(e, {}).get(s)
    return v if isinstance(v, (int, float)) else 0

print('blocks:', list(out))
for s in S:
    tw = g('OP Before Admin', 'TWPC', s)
    parts = sum(g('OP Before Admin', e, s) for e in ['Starch', 'HVA', 'Waxy', 'Foods', 'NBG', 'ElimBU', 'Corp'])
    print(s, 'OPBA', round(tw, 1), 'sumBU', round(parts, 1))
for s in ['LE26', 'AP27', 'AP28']:
    print(s, {b: round(g(b, 'TWPC', s), 1) for b in ['Volume', 'Net sales', 'Gross profit', 'OP Before Admin', 'Total Admin',
          'Operating profit', 'Other operating income and expenses', 'Exchange gain/(loss)', 'Net non-operating profit',
          'Finance income (expense)', 'CIT', 'MI', 'Net profit']})
for blk in ['OP Before Admin', 'Net profit', 'Net sales', 'Total Admin']:
    print('==', blk)
    for e in ['Starch', 'StarchTH', 'Total CN', 'TWIC', 'Total VN', 'HVA', 'TDC', 'TDC2.0', 'TWIN', 'TWII', 'Waxy', 'Foods', 'FoodTH', 'FoodWG', 'FoodVN', 'NBG', 'ElimBU', 'Corp']:
        print(' ', e.ljust(10), ' '.join('%8.1f' % g(blk, e, s) for s in S))

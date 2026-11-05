# Read FY values straight from the P&L LE9+3 workbook (ConsoAll + BU / entity sheets) and reconcile BU sums to ConsoAll
import openpyxl, json, sys
F = sys.argv[2]
SCN = {'Y23': '2023', 'R24': '2024 Rebase', '2025': '2025', 'AP26': 'AP2026 Stretch', 'LE26': 'LE2026 (9+3)', 'AP27': 'AP2027 Board', 'AP28': 'AP2028 Board'}
LINES = ['Volume', 'Net Sales', 'Gross profit', 'DC', 'A&P', 'S&M', 'OP Before Admin', 'admin exp - People', 'admin exp - Non-people',
         'Other operating income and expenses', 'Exchange gain/(loss)', 'Operating profit', 'Net non-operating profit',
         'Finance income (expense)', 'CIT', 'MI', 'Net profit aft Thanos', 'Total COST', 'PPA - CIT', 'Net income before MI', 'Non-operating income', 'Non-operating expenses', 'Idle']
SHEETS = ['ConsoAll', 'StarchBU', 'HVABU', 'HVA incl Waxy', 'Waxy', 'FoodBU', 'NBGBU', 'ElimBU', 'Corp',
          'StarchTH', 'TotalCN', 'TWIC', 'TotalVN', 'TDC', 'TDC2.0', 'TWIN', 'TWII', 'ElimH', 'FoodTH&WG', 'FoodTH', 'FoodWG', 'FoodVN', 'BioPlastic', 'AnimalFeeds', 'AgBio', 'V9', 'TWIT', 'TWFZ', 'ElimCN', 'FoodTH.Dom', 'FoodTH.Exp', 'TNT', 'VTC', 'TWIP']
wb = openpyxl.load_workbook(F, read_only=True, data_only=True)
out = {}
for sn in SHEETS:
    ws = wb[sn]
    rows = list(ws.iter_rows(min_row=1, max_row=110, max_col=20, values_only=True))
    hdr = None
    for r in range(0, 10):
        labels = [str(v).strip() if v is not None else '' for v in rows[r]]
        if 'AP2027 Board' in labels: hdr = labels; break
    if hdr is None: print('NO HEADER', sn); continue
    col = {k: hdr.index(v) for k, v in SCN.items() if v in hdr}
    vals = {}
    for row in rows:
        lab = str(row[0]).strip() if row[0] is not None else ''
        if lab == 'Net profit': lab = 'Net profit aft Thanos'   # BU sheets call the NP line 'Net profit'
        if lab in LINES and lab not in vals:
            vals[lab] = {k: (float(row[c]) if isinstance(row[c], (int, float)) else 0.0) for k, c in col.items()}
    missing = [l for l in LINES if l not in vals]
    out[sn] = vals
    print(sn.ljust(14), 'cols', {k: c + 1 for k, c in col.items()}, 'missing:', missing)
json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), indent=1)

# reconciliation: ConsoAll vs StarchBU + HVABU + FoodBU + NBGBU + ElimBU + Waxy (the formula written in ConsoAll row 2)
print('\n=== ConsoAll vs sum of BU sheets (diff = BU sum - ConsoAll), MB')
KEY = ['Net Sales', 'Gross profit', 'OP Before Admin', 'admin exp - People', 'admin exp - Non-people', 'Operating profit', 'Net profit aft Thanos']
for s in [x for x in SCN if x != 'Y23']:
    for l in KEY:
        c = out['ConsoAll'][l][s]
        bu = sum(out[x][l][s] for x in ['StarchBU', 'HVABU', 'FoodBU', 'NBGBU', 'ElimBU', 'Waxy'])
        flag = '  <-- VARIANCE' if abs(bu - c) > 0.05 else ''
        print(f'{s:5} {l:24} ConsoAll {c:10.1f}  BU sum {bu:10.1f}  diff {bu - c:7.2f}{flag}')
print('\n=== HVA incl Waxy sheet vs HVABU + Waxy')
for s in [x for x in SCN if x != 'Y23']:
    for l in ['Net Sales', 'Gross profit', 'OP Before Admin', 'Net profit aft Thanos']:
        a = out['HVA incl Waxy'][l][s]; b = out['HVABU'][l][s] + out['Waxy'][l][s]
        print(f'{s:5} {l:22} sheet {a:9.1f}  HVABU+Waxy {b:9.1f}  diff {a - b:6.2f}')
print('\n=== Corp sheet (is it inside ElimBU?)')
for s in [x for x in SCN if x != 'Y23']:
    print(s, 'Corp OPBA', round(out['Corp']['OP Before Admin'][s], 2), 'ElimBU OPBA', round(out['ElimBU']['OP Before Admin'][s], 2), 'Corp NP', round(out['Corp']['Net profit aft Thanos'][s], 2), 'ElimBU NP', round(out['ElimBU']['Net profit aft Thanos'][s], 2))






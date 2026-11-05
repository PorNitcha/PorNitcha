# slide-7 admin table straight from BU Review_Admin (Thailand / Inter x P / Non-P), stored P&L-negative like admin2
import openpyxl, json, sys
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True); ws = wb['BU Review_Admin']
rows = list(ws.iter_rows(min_row=1, max_row=14, max_col=16, values_only=True))
COL = {'2025': 3, 'AP26': 6, 'LE26': 11, 'AP27': 14}   # FY 2025, AP 2026* (reclass TDC 2.0), FC 9+3, AP 2027
def row(i): return rows[i - 1]
src = {'TWPC': {'adp': row(5), 'adn': row(6)}, 'Thailand': {'adp': row(8), 'adn': row(9)}, 'International': {'adp': row(11), 'adn': row(12)}}
d = json.load(open(sys.argv[2], encoding='utf-8'))
for s, c in COL.items():
    for k in ['adp', 'adn']:
        for g in ['TWPC', 'Thailand', 'International']:
            d['admin2'][s][k][g] = -float(src[g][k][c])
        assert abs(d['admin2'][s][k]['Thailand'] + d['admin2'][s][k]['International'] - d['admin2'][s][k]['TWPC']) < 0.05, (s, k)
json.dump(d, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for s in COL: print(s, {k: {g: round(v, 2) for g, v in d['admin2'][s][k].items()} for k in ['adp', 'adn']})

# AP2027 plan per customer per plant (Rayong / TKT): FY tonnes and plan product GP (THB), from the Top Line HVA 'data' sheet
# (same read as tier10.py: AP + headroom lines, col 78-89 = monthly tonnes, col 222-233 = monthly GP THB m).
# Output ap27_plant.json keyed by the customer name used in quadrant_artifact_v7.html DATA (quad_v2 key normalisation).
import csv, io, json, re, collections, openpyxl
SRC = 'topline_final_copy.xlsx'
PLANT = {'TDC': 'RY', 'TKT': 'TKT'}
def norm(n):
    n = str(n).upper().replace('BJ.', '').replace('ฟู๊ด', 'ฟู้ด'); n = re.sub(r'[^A-Z0-9ก-๙]+', '', n); return n[:16]
ALIAS = {'HUIFALINXIAFOODS': 'HUIFA', 'QINGDAOMIRACLESU': 'HUIFA', 'QINGDAOMIRACLE': 'HUIFA', 'MORIIFOODSINC': 'MORIIFOODS', 'FOODTRENDANDSUPE': 'FOODTREND',
         # plan-sheet spellings that differ from the profitability / AP-by-customer names used in the quadrant DATA
         'SIPC': 'SIPCSARL', 'JALEXLOGISTICSLT': 'JALEXLOGISTICS', 'LLCYUZHREGIONRUS': 'LLCYUZHREGION', 'COMPANYCORNPRODU': 'COMPANYCORN', 'LLCOMPANYCORNPRO': 'COMPANYCORN'}
key = lambda n: ALIAS.get(norm(n), norm(n)); num = lambda v: v if isinstance(v, (int, float)) else 0.0

code2grp = {}
for r in csv.DictReader(io.open('data_actual.csv', encoding='utf-8-sig')):
    if r['Customer Code']: code2grp[str(r['Customer Code']).strip()] = r['Customer name (Group)']

wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
raw = [r for r in wb['data'].iter_rows(min_row=8, values_only=True) if r[6] not in (None, '')]
VOL = list(range(78, 90)); GP = list(range(222, 234))
P = collections.defaultdict(lambda: {'name': '', 'country': '', 'RY': [0.0, 0.0], 'TKT': [0.0, 0.0]})
for r in raw:
    vols = [num(r[j]) for j in VOL]
    if sum(vols) <= 0: continue
    code = str(r[5]).strip() if r[5] not in (None, '-', '') else ''; grp = code2grp.get(code) or r[6]
    k = key(grp); c = P[k]; c['name'] = c['name'] or str(grp); c['country'] = c['country'] or str(r[9] or '')
    pl = PLANT.get(r[3], str(r[3])); c.setdefault(pl, [0.0, 0.0])
    c[pl][0] += sum(vols); c[pl][1] += sum(num(r[j]) for j in GP) * 1e6

# map to the artifact DATA names
t = io.open('quadrant_artifact_v7.html', encoding='utf-8').read()
DATA = json.loads(re.search(r'const DATA = (\[.*?\]);', t, re.S).group(1))
byk = {key(d['name']): d for d in DATA}
out, unmatched = {}, []
for k, c in P.items():
    d = byk.get(k)
    if d: out[d['name']] = {'RY': [round(c['RY'][0], 1), round(c['RY'][1])], 'TKT': [round(c['TKT'][0], 1), round(c['TKT'][1])]}
    else: unmatched.append((c['name'], round(c['RY'][0] + c['TKT'][0])))
json.dump(out, io.open('ap27_plant.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump({pl: [round(sum(c[pl][0] for c in P.values()), 1), round(sum(c[pl][1] for c in P.values()))] for pl in ('RY', 'TKT')}, io.open('ap27_plant_totals.json', 'w', encoding='utf-8'))
tot = lambda pl, i: sum(v[pl][i] for v in out.values())
print('matched %d customers · RY %.0f t / %.1f MB · TKT %.0f t / %.1f MB · both %.0f t' % (len(out), tot('RY', 0), tot('RY', 1) / 1e6, tot('TKT', 0), tot('TKT', 1) / 1e6, tot('RY', 0) + tot('TKT', 0)))
print('plan sheet total', round(sum(c['RY'][0] + c['TKT'][0] for c in P.values())), 't; DATA t27 total', round(sum(d['t27'] for d in DATA)))
print('unmatched:', sorted(unmatched, key=lambda x: -x[1])[:10])
diff = [(d['name'][:30], d['t27'], round(out[d['name']]['RY'][0] + out[d['name']]['TKT'][0])) for d in DATA if d['name'] in out and abs(d['t27'] - out[d['name']]['RY'][0] - out[d['name']]['TKT'][0]) > 5]
print('t27 differs >5 t:', diff[:10])
print('DATA accounts with no plan line:', [(d['name'][:30], d['t27']) for d in DATA if d['name'] not in out and d['t27'] > 0][:10])

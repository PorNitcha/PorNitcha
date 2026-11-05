# Thai admin bridge FY26 (LE 9+3) -> AP27 from BU Review_Admin.xlsx, sheet Waterfall_TH, split Admin P / Non-P.
# Also pulls cost-centre moves (NonP by Cost Center) and the TDC -> TDC 2.0 people-cost transfer (BU Review_Admin rows).
# usage: python admin_bridge.py admin.xlsx out.json
import openpyxl, json, sys
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
ws = wb['Waterfall_TH']
rows = list(ws.iter_rows(min_row=1, max_row=80, max_col=6, values_only=True))
def grab(r0, r1):
    d = {}
    for r in range(r0 - 1, r1):
        lab, val = rows[r][1], rows[r][2]
        if lab and isinstance(val, (int, float)): d[str(lab).strip()] = float(val)
    return d
P = grab(3, 18); N = grab(23, 40); TOT = grab(52, 74)
out = {'P': P, 'N': N, 'TOT': TOT}
# tie checks on the sheet's own arithmetic
assert abs(P['LE 2026'] + P['Rev Bonus 2025'] + P['Wellgrow Base'] + P['Special Incentive'] - P['2026 Underlying']) < 0.05
assert abs(P['2026 Underlying'] + P['Salary'] + P['Medical care'] + P['Other Welfare'] + P['Staff recruitment'] + P['Trainning'] + P['Other'] - P['AP 2027 Base']) < 0.05
assert abs(P['AP 2027 Base'] + P['Wellgrow'] - P['AP 2027 Reporting']) < 0.05 and abs(P['AP 2027 Reporting'] + P['Saving'] - P['AP 2027 Strech']) < 0.05
assert abs(N['LE 2026'] + N['Impairment'] + N['TDC 2.0 Pre-Operating'] + N['Wellgrow Base'] + N['TTDI Loyalty 2025'] - N['2026 Underlying']) < 0.05
assert abs(N['2026 Underlying'] + N['Consult Fee'] + N['Admin'] + N['IT'] + N['Other'] - N['AP 2027 Base']) < 0.05
assert abs(N['AP 2027 Base'] + N['Impairment TDC RY (MS1)'] + N['TDC2.0 pre-operating'] + N['Wellgrow'] - N['AP 2027 Reporting']) < 0.05
assert abs(N['AP 2027 Reporting'] + N['Saving'] - N['AP 2027 Strech']) < 0.05
assert abs(P['LE 2026'] + N['LE 2026'] - TOT['LE 2026']) < 0.05 and abs(P['AP 2027 Reporting'] + N['AP 2027 Reporting'] - TOT['AP 2027 Reporting']) < 0.05
assert abs(TOT['AP 2027 Strech'] + TOT['Inter'] - TOT['Total incl Inter']) < 0.05
# bridge bars for the chart: [label, P, NonP, kind]  kind = total | step | subtotal
p26 = P['Rev Bonus 2025'] + P['Wellgrow Base'] + P['Special Incentive']
n26 = N['Impairment'] + N['TDC 2.0 Pre-Operating'] + N['Wellgrow Base'] + N['TTDI Loyalty 2025']
pU = P['Salary'] + P['Medical care'] + P['Other Welfare'] + P['Staff recruitment'] + P['Trainning'] + P['Other']
nU = N['Consult Fee'] + N['Admin'] + N['IT'] + N['Other']
p27 = P['Wellgrow']; n27 = N['Impairment TDC RY (MS1)'] + N['TDC2.0 pre-operating'] + N['Wellgrow']
bars = [['LE 2026 (9+3)', P['LE 2026'], N['LE 2026'], 'total'],
        ['2026 one-offs reversed', p26, n26, 'step'],
        ['2026 underlying', P['2026 Underlying'], N['2026 Underlying'], 'subtotal'],
        ['Recurring cost growth', pU, nU, 'step'],
        ['AP 2027 base', P['AP 2027 Base'], N['AP 2027 Base'], 'subtotal'],
        ['2027 one-offs & Well Grow', p27, n27, 'step'],
        ['AP 2027 (P&L)', P['AP 2027 Reporting'], N['AP 2027 Reporting'], 'total'],
        ['Saving', P['Saving'], N['Saving'], 'step'],
        ['AP 2027 stretch', P['AP 2027 Strech'], N['AP 2027 Strech'], 'total']]
out['bars'] = bars
# detailed line table (P | Non-P | Total) in the same order as the sheet
lines = [('LE 2026 (9+3)', P['LE 2026'], N['LE 2026'], 'total'),
         ('Reversal of 2025 bonus accrual', P['Rev Bonus 2025'], 0, 'line'), ('TTDI loyalty 2025', 0, N['TTDI Loyalty 2025'], 'line'),
         ('Impairment 2026 (non-cash)', 0, N['Impairment'], 'line'), ('TDC 2.0 pre-operating 2026', 0, N['TDC 2.0 Pre-Operating'], 'line'),
         ('Special incentive', P['Special Incentive'], 0, 'line'), ('Well Grow base (Sep-Dec 2026)', P['Wellgrow Base'], N['Wellgrow Base'], 'line'),
         ('2026 underlying', P['2026 Underlying'], N['2026 Underlying'], 'subtotal'),
         ('Salary (merit / inflation)', P['Salary'], 0, 'line'), ('Medical care & other welfare', P['Medical care'] + P['Other Welfare'], 0, 'line'),
         ('Recruitment & training', P['Staff recruitment'] + P['Trainning'], 0, 'line'), ('Other personnel', P['Other'], 0, 'line'),
         ('Consulting / professional fees', 0, N['Consult Fee'], 'line'), ('Admin, IT & other', 0, N['Admin'] + N['IT'] + N['Other'], 'line'),
         ('AP 2027 base', P['AP 2027 Base'], N['AP 2027 Base'], 'subtotal'),
         ('TDC Rayong MS1 write-off', 0, N['Impairment TDC RY (MS1)'], 'line'), ('TDC 2.0 pre-operating 2027', 0, N['TDC2.0 pre-operating'], 'line'),
         ('Well Grow full year', P['Wellgrow'], N['Wellgrow'], 'line'),
         ('AP 2027 reporting (P&L)', P['AP 2027 Reporting'], N['AP 2027 Reporting'], 'total'),
         ('Saving programme', P['Saving'], N['Saving'], 'line'),
         ('AP 2027 stretch', P['AP 2027 Strech'], N['AP 2027 Strech'], 'total')]
out['lines'] = [list(x) for x in lines]
# tie: line items add to the totals
runP = runN = 0
for lab, p, n, k in lines:
    if k == 'total' and lab.startswith('LE'): runP, runN = p, n
    elif k == 'line': runP += p; runN += n
    else: assert abs(runP - p) < 0.05 and abs(runN - n) < 0.05, (lab, runP, p, runN, n)
# cost-centre moves (TH non-P, AP27 base vs 2026 underlying) and IT 2028 step
cc = wb['NonP by Cost Center']
ccrows = list(cc.iter_rows(min_row=28, max_row=74, max_col=12, values_only=True))
ccd = {}
for r in ccrows:
    if r[1] and isinstance(r[7], (int, float)): ccd[str(r[1]).strip()] = {'LE26': r[4], 'under26': r[6], 'AP27': r[7], 'AP28': r[8]}
out['cc'] = {k: ccd[k] for k in ['IT', 'Management', 'Farm Sourcing', 'HR', 'Farm', 'Admin', 'Legal', 'TDC 2.0', 'Starch-Factory', 'Account'] if k in ccd}
# TDC -> TDC 2.0 people cost (BU Review_Admin: rows 31-32, cols 12 = FC 9+3, 15 = AP 2027), values negative in the sheet
br = wb['BU Review_Admin']
brrows = list(br.iter_rows(min_row=1, max_row=60, max_col=16, values_only=True))
def pick(name):
    for r in brrows:
        if r[1] == name: return {'LE26': -float(r[11] or 0), 'AP27': -float(r[14] or 0)}
out['tdc_p'] = {'TDC': pick('TDC'), 'TDC2.0': pick('TDC2.0')}
for r in brrows:
    if r[1] == 'Total' and r[2] == 'Total': out['twpc'] = {'FY25': r[3], 'AP26': r[6], 'target26': r[10], 'LE26': r[11], 'AP27': r[14], 'AP27_target': r[17], 'AP28': r[18]}
    if r[1] == 'Inter' and r[2] == 'P Cost': out['inter_p'] = {'LE26': r[11], 'AP27': r[14]}
    if r[2] == 'Non P' and r[1] is None and 'inter_p' in out and 'inter_n' not in out: out['inter_n'] = {'LE26': r[11], 'AP27': r[14]}
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('bars:'); [print('  %-28s P %7.2f  N %7.2f  T %7.2f  %s' % (b[0], b[1], b[2], b[1] + b[2], b[3])) for b in bars]
print('TOT', {k: round(v, 2) for k, v in TOT.items()})
print('cc', {k: {a: round(b, 1) for a, b in v.items() if isinstance(b, (int, float))} for k, v in out['cc'].items()})
print('tdc_p', out['tdc_p'], 'twpc', out.get('twpc'), 'inter', out.get('inter_p'), out.get('inter_n'))

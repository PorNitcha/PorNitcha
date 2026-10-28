"""Derive tier10.py from tier9.py: five plug-and-play sheets (FY, Q1-Q4 2027) with risk-profile columns. Run: python patch_tier10.py && python tier10.py"""
src = open('tier9.py', encoding='utf-8').read()
A = '# ===================== 2027 plug-and-play ====================='
B = '# ---- Tier definition ----'
ia, ib = src.index(A), src.index(B)
assert ia > 0 and ib > ia

NEW = r'''# ===================== 2027 plug-and-play: FY and by quarter, with risk profile =====================
RT = json.load(open('risk_types.json', encoding='utf-8'))     # written by risk4.py: "rx|customer key|SN" -> risk type
TYPES = {'1': '1 New customer', '2': '2 Existing cust, new SKU', '3': '3 +30% vol of 2026 max qtr', '0': '0 Running base (w/i 30%)', 'x': 'x Sold in 25/26, not in 2027 plan (2026 YTD t)'}
TYPEF = {'1': 'F1C7C7', '2': 'F8DCC6', '3': 'FBF0C6', '0': 'E2EFDA', 'x': 'ECECEC'}
def rz(): return {'t': 0.0, 'gp': 0.0, 'cust': collections.defaultdict(float)}     # tonnes, product GP (THB), tonnes per customer
RISK = collections.defaultdict(lambda: collections.defaultdict(rz)); untyped = 0.0   # (rx, rid, period) -> type -> rz
for l in lines:
    c = C[(l['rx'], l['key'])]; ty = RT.get(f"{l['rx']}|{l['key']}|{l['sn']}")
    if ty is None: untyped += sum(l['vol']); ty = '0'
    for rid in [('tier', c['tier'])] + ([('key', l['key'])] if c['keyacc'] else []):
        for p in ['FY'] + QS:
            idx = range(12) if p == 'FY' else range(QS.index(p) * 3, QS.index(p) * 3 + 3)
            a = RISK[(l['rx'], rid, p)][ty]; t = sum(l['vol'][i] for i in idx); a['t'] += t; a['gp'] += sum(l['gp'][i] for i in idx); a['cust'][l['key']] += t
print('risk profile: plan tonnes without a type', round(untyped))
planned = {(l['rx'], l['key'], l['sn']) for l in lines}; a26 = collections.defaultdict(lambda: [0.0, 0.0]); SNH = collections.defaultdict(lambda: {'t25': 0.0, 'g25': 0.0, 't26': 0.0, 'g26': 0.0})   # customer x SN actuals (both plants)
def _f(v):
    try: return float(v)
    except (TypeError, ValueError): return 0.0
for r_ in csv.DictReader(open('data_actual.csv', encoding='utf-8')):
    if r_['Year'] not in ('Year 2025', 'Year 2026') or r_['Reaction group'] in ('', 'None', '#N/A'): continue
    rxa = r_['Reaction group'] if r_['Reaction group'] in RX else 'Others'; yy = r_['Year'][-2:]
    t_ = _f(r_['Sales Quantity (Tons)']); g_ = _f(r_['Net Sales Revenue (THB)']) - _f(r_['Actual Cost(THB)']) - _f(r_['Cost from Freight(THB)']) - _f(r_['Cost from Insurance(THB)'])
    if yy == '26': a = a26[(rxa, key(r_['Customer name (Group)']), r_['SN'])]; a[0] += t_; a[1] += g_
    h = SNH[(key(r_['Customer name (Group)']), r_['SN'])]; h['t' + yy] += t_; h['g' + yy] += g_
XR = collections.defaultdict(rz); x_unplaced = 0.0        # (rx, rid) -> 2026 YTD tonnes / product GP / customers of lines not in the 2027 plan
for (rx_, k_, sn_), (t_, g_) in a26.items():
    if (rx_, k_, sn_) in planned or t_ <= 0: continue
    h_ = H.get((k_, rx_))
    if not h_ or not h_['t26'] or h_['gp26'] is None: x_unplaced += t_; continue
    for rid_ in [('tier', tier_of(rx_, h_['gp26'] / 1000))] + ([('key', k_)] if k_ in keyset[rx_] else []):
        a = XR[(rx_, rid_)]; a['t'] += t_; a['gp'] += g_; a['cust'][k_] += t_
print('x = 2026 YTD t not in 2027 plan:', round(sum(v['t'] for (rx_, rid_), v in XR.items() if rid_[0] == 'tier')), '| not placed (customer has no 2026 GP/kg)', round(x_unplaced))

PLUG = [('FY', '2027 plug FY', 'full-year 2027'), ('Q1', '2027 plug Q1', 'Q1 2027'), ('Q2', '2027 plug Q2', 'Q2 2027'), ('Q3', '2027 plug Q3', 'Q3 2027'), ('Q4', '2027 plug Q4', 'Q4 2027')]
if '2027 plug-and-play' in wb.sheetnames: del wb['2027 plug-and-play']
INP = 'FFF2CC'; RK = 24; TYO = ['1', '2', '3', '0', 'x']; RSUB = ['Tonnes', '% vol', 'GP/kg', 'GP THB M', '# cust']
def tcol(ty, f): return RK + 5 * TYO.index(ty) + RSUB.index(f)        # column of field f in the block of risk type ty
RKP = RK + 5 * len(TYO)                                               # % at risk (1+2+3), last column
TL = {ty: CL(tcol(ty, 'Tonnes')) for ty in TYO}; PLAN_T = lambda r: f"({TL['1']}{r}+{TL['2']}{r}+{TL['3']}{r}+{TL['0']}{r})"   # AP plan tonnes of the row = sum of the four 2027 types
def pput(r, col, v, fmt=None, fill=None, bold=False, color=None, italic=False):
    c = ws.cell(row=r, column=col, value=v)
    if fmt: c.number_format = fmt
    if fill: c.fill = PatternFill('solid', fgColor=fill)
    if bold or color or italic: c.font = Font(bold=bold, color=color, italic=italic)
    return c
def build_plug(p, sname, plabel):
    global ws, r
    ws = fresh(sname, 2); ws.sheet_view.showGridLines = False
    PL = '2027 FY' if p == 'FY' else f'2027 {p}'
    ws['A1'] = f'{PL} plug-and-play: change the % of volume per tier and plant, keep each plant volume and GP/kg target fixed - with the delivery-risk profile of the {plabel} plan tonnes'; ws['A1'].font = Font(bold=True, size=13, color=NAVY)
    ws['A2'] = (f'Yellow cells are inputs: % of Rayong volume and % of TKT volume per tier (each column must add to 100%), and the plant GP/kg per tier (defaults = AP plan {plabel}; for tiers with no plan volume the default is the tier mid-point, plus the RY-TKT cost gap for TKT). '
                f'Everything else is a formula. The LOCKED row holds the AP27 {plabel} plant tonnes and plant GP/kg (and their combination for the two plants); the CHECK row shows the gap of your mix to those locks - aim for zero. '
                '2025 / 2026 columns are full-period actuals for reference. Risk profile columns = the AP plan tonnes of this period by delivery-risk type (one type per customer x SN, same rule as the risk file); they are static reference, not part of the plug. '
                'x = 2026 YTD tonnes of customer x SN sold in 2025/26 but absent from the 2027 plan, shown under the customer 2026 tier (memo). Two-plant GP/kg here is on plant basis (tonne-weighted Rayong + TKT), unlike the commercial (Rayong-cost) basis on the Tier mapping sheet.')
    ws['A2'].alignment = Alignment(wrap_text=True, vertical='top'); ws.merge_cells(f'A2:{CL(RKP)}2'); ws.row_dimensions[2].height = 80
    pcols = [('', 'Tier (THB/kg)'), ('', 'Zone')]
    for lab in ('2025 actual (FY)', '2026 YTD (Jan-Sep)'): pcols += [(lab, s_) for s_ in ('# cust', 'Tonnes', '% vol', 'GP/kg', 'GP THB M')]
    pcols += [(f'{PL} Rayong (plug)', s_) for s_ in ('% of RY  [input]', 'Tonnes', 'GP/kg  [input]')] + [(f'{PL} TKT (plug)', s_) for s_ in ('% of TKT  [input]', 'Tonnes', 'GP/kg  [input]')]
    pcols += [(f'{PL} two plants (result)', s_) for s_ in ('Tonnes', '% vol', 'GP/kg', 'GP THB M', '# cust (plan)')]
    for ty in TYO: pcols += [(f"{TYPES[ty]}" + (f' - {PL} plan' if ty != 'x' else ''), s_) for s_ in RSUB]
    pcols += [('% at risk', '% at risk (1+2+3)')]
    PNC = len(pcols); c0 = 1
    while c0 <= PNC:
        g = pcols[c0 - 1][0]; c1 = c0
        while c1 + 1 <= PNC and pcols[c1][0] == g: c1 += 1
        if g:
            ws.cell(row=4, column=c0, value=g)
            if c1 > c0: ws.merge_cells(start_row=4, start_column=c0, end_row=4, end_column=c1)
            cell = ws.cell(row=4, column=c0); cell.font = HFNT; cell.fill = HF; cell.alignment = Alignment(horizontal='center')
        c0 = c1 + 1
    for j, (_, s_) in enumerate(pcols, 1):
        c = ws.cell(row=5, column=j, value=s_); c.font = Font(bold=True, color=NAVY); c.fill = SUBF; c.alignment = Alignment(horizontal='center', wrap_text=True); c.border = Border(bottom=med)
        ws.column_dimensions[CL(j)].width = 26 if j == 1 else 16 if j == 2 else 10
    for ty in TYO:   # risk-type group headers carry the muted traffic-light colour of the type
        c = ws.cell(row=4, column=tcol(ty, 'Tonnes')); c.fill = PatternFill('solid', fgColor=TYPEF[ty]); c.font = Font(bold=True, color=NAVY)
    ws.row_dimensions[5].height = 32
    r = 6
    for rx in RX:
        rows = ROWS[rx]
        T25, T26 = tot_of(rx, '25', 't'), tot_of(rx, '26', 't'); RYT, TKT_, TOT = tot_of(rx, p, 'ry_t'), tot_of(rx, p, 'tk_t'), tot_of(rx, p, 't')
        RYG, TKG = tot_of(rx, p, 'ry_gp'), tot_of(rx, p, 'tk_gp'); t_ry = RYG / RYT if RYT else None; t_tk = TKG / TKT_ if TKT_ else None
        pput(r, 1, rx).font = Font(bold=True, size=12, color=NAVY)
        pput(r, 3, f"tier gap {GRIDTXT[rx]} · locked {plabel}: Rayong {RYT:,.0f} t @ {t_ry or 0:.2f}" + (f" · TKT {TKT_:,.0f} t @ {t_tk:.2f}" if TKT_ else '') + (f" · two plants {TOT:,.0f} t @ {(RYG + TKG) / TOT:.2f} (plant basis)" if TOT else '')).font = Font(italic=True, color='595959')
        for j in range(1, PNC + 1): ws.cell(row=r, column=j).border = Border(top=med)
        r += 1; blk0 = r
        keys_by_tier = collections.defaultdict(list)
        for k in KEYS[rx]: keys_by_tier[C[(rx, k)]['tier']].append(k)
        cuts_ = cuts(rx)
        def riskpct(ty, rr):   # % vol: 2027 types = share of the row's AP plan tonnes; x = share of the row's 2026 YTD tonnes (col I)
            return f"=IFERROR({TL[ty]}{rr}/{PLAN_T(rr)},\"\")" if ty != 'x' else f"=IFERROR({TL['x']}{rr}/I{rr},\"\")"
        def riskcells(rid, bold=False, italic=False, color=None):
            rk = RISK.get((rx, rid, p), {})
            for ty in TYO:
                a = rk.get(ty) if ty != 'x' else XR.get((rx, rid)); t_, g_, n_ = (a['t'], a['gp'], sum(1 for v in a['cust'].values() if v >= MIN_T)) if a else (0.0, 0.0, 0)
                ct, cp, ck, cg, cn = (tcol(ty, f) for f in RSUB)
                pput(r, ct, round(t_) or None, NUM, bold=bold, italic=italic, color=color); pput(r, cp, riskpct(ty, r), PCT, bold=bold, italic=italic, color=color)
                pput(r, ck, f"=IFERROR({CL(cg)}{r}/{CL(ct)}{r}*1000,\"\")", DEC, bold=bold, italic=italic, color=color); pput(r, cg, g_ / 1e6 if t_ else None, MB, bold=bold, italic=italic, color=color); pput(r, cn, n_ or None, NUM, bold=bold, italic=italic, color=color)
            pput(r, RKP, f"=IFERROR(({TL['1']}{r}+{TL['2']}{r}+{TL['3']}{r})/{PLAN_T(r)},\"\")", PCT, bold=bold, italic=italic, color=color)
        for rid in rows:
            cell = CELL[(rx, rid)]; i = rid[1]
            if all(cell[q]['t'] < 1.0 for q in ('25', '26', p)) and not (0 < i < len(cuts_)): continue   # keep every in-grid tier (plug targets), drop empty open-ended ends
            zn = zone(rx, i); x, y, zz = cell['25'], cell['26'], cell[p]
            mid = (cuts_[i - 1] + cuts_[i]) / 2 if 0 < i < len(cuts_) else (cuts_[0] - 0.25 if i == 0 else cuts_[-1] + 0.25)
            pput(r, 1, tname(rx, i), fill=ZONEF[zn]); pput(r, 2, zn, fill=ZONEF[zn])
            pput(r, 3, x['n'] or None, NUM); pput(r, 4, round(x['t']) or None, NUM); pput(r, 5, x['t'] / T25 if T25 and x['t'] else None, PCT); pput(r, 6, x['gp'] / x['t'] if x['t'] else None, DEC); pput(r, 7, x['gp'] / 1000 if x['t'] else None, MB)
            pput(r, 8, y['n'] or None, NUM); pput(r, 9, round(y['t']) or None, NUM); pput(r, 10, y['t'] / T26 if T26 and y['t'] else None, PCT); pput(r, 11, y['gp'] / y['t'] if y['t'] else None, DEC); pput(r, 12, y['gp'] / 1000 if y['t'] else None, MB)
            pput(r, 13, zz['ry_t'] / RYT if RYT else 0, PCT, INP); pput(r, 14, f"=M{r}*$N${{TR}}", NUM); pput(r, 15, (zz['ry_gp'] / zz['ry_t']) if zz['ry_t'] else round(mid, 2), DEC, INP)
            pput(r, 16, zz['tk_t'] / TKT_ if TKT_ else 0, PCT, INP); pput(r, 17, f"=P{r}*$Q${{TR}}", NUM); pput(r, 18, (zz['tk_gp'] / zz['tk_t']) if zz['tk_t'] else round(mid + GAP.get(rx, 0.0), 2), DEC, INP)
            pput(r, 19, f"=N{r}+Q{r}", NUM); pput(r, 20, f"=IFERROR(S{r}/$S${{TR}},\"\")", PCT); pput(r, 21, f"=IFERROR((N{r}*O{r}+Q{r}*R{r})/S{r},\"\")", DEC); pput(r, 22, f"=(N{r}*O{r}+Q{r}*R{r})/1000", MB); pput(r, 23, zz['n'] or None, NUM)
            riskcells(rid)
            r += 1
            for k in keys_by_tier.get(i, []):
                c = C[(rx, k)]; kc = CELL[(rx, ('key', k))]; kz = kc[p]; k25 = kc['25']; k26 = kc['26']
                pput(r, 1, '★ ' + c['grp'][:34], fill=ZONEF[zn], bold=True, italic=True, color=BLUE).alignment = Alignment(indent=2)
                pput(r, 2, f"{zone_g(rx, c['g'])} · {c['g']:.2f}", fill=ZONEF[zn], italic=True, color=BLUE)
                vals = {3: k25['n'] or None, 4: round(k25['t']) or None, 5: k25['t'] / T25 if T25 and k25['t'] else None, 6: k25['gp'] / k25['t'] if k25['t'] else None, 7: k25['gp'] / 1000 if k25['t'] else None,
                        8: k26['n'] or None, 9: round(k26['t']) or None, 10: k26['t'] / T26 if T26 and k26['t'] else None, 11: k26['gp'] / k26['t'] if k26['t'] else None, 12: k26['gp'] / 1000 if k26['t'] else None,
                        13: kz['ry_t'] / RYT if RYT and kz['ry_t'] else None, 14: round(kz['ry_t']) or None, 15: kz['ry_gp'] / kz['ry_t'] if kz['ry_t'] else None, 16: kz['tk_t'] / TKT_ if TKT_ and kz['tk_t'] else None, 17: round(kz['tk_t']) or None, 18: kz['tk_gp'] / kz['tk_t'] if kz['tk_t'] else None,
                        19: round(kz['t']) or None, 20: kz['t'] / TOT if TOT and kz['t'] else None, 21: (kz['ry_gp'] + kz['tk_gp']) / kz['t'] if kz['t'] else None, 22: (kz['ry_gp'] + kz['tk_gp']) / 1000 if kz['t'] else None, 23: 1 if kz['t'] else None}
                fm_ = {3: NUM, 4: NUM, 5: PCT, 6: DEC, 7: MB, 8: NUM, 9: NUM, 10: PCT, 11: DEC, 12: MB, 13: PCT, 14: NUM, 15: DEC, 16: PCT, 17: NUM, 18: DEC, 19: NUM, 20: PCT, 21: DEC, 22: MB, 23: NUM}
                for col, v in vals.items(): pput(r, col, v, fm_[col], italic=True, color=BLUE)
                riskcells(('key', k), italic=True, color=BLUE)
                r += 1
        blk1 = r - 1; TR = r + 3
        for rr in range(blk0, blk1 + 1):
            for col in (14, 17, 20):
                v = ws.cell(row=rr, column=col).value
                if isinstance(v, str) and '{TR}' in v: ws.cell(row=rr, column=col).value = v.replace('{TR}', str(TR + 1 if col in (14, 17) else TR))   # tonnes use the LOCKED plant totals (row TR+1); % vol uses the mix total (row TR)
        def prng(col): return f"{CL(col)}${blk0}:{CL(col)}${blk1}"
        RSUM = [tcol(ty, f) for ty in TYO for f in ('Tonnes', 'GP THB M', '# cust')]; RGPM = {tcol(ty, 'GP THB M') for ty in TYO}
        SUMC = (3, 4, 7, 8, 9, 12, 13, 14, 16, 17, 19, 22, 23) + tuple(RSUM)
        def fmt_of(col): return PCT if col in (13, 16) else (MB if col in (7, 12, 22) or col in RGPM else NUM)
        def riskratios(rr, fill=None):   # % vol and GP/kg on subtotal / total rows (formulas over the row's own sums)
            for ty in TYO:
                pput(rr, tcol(ty, '% vol'), riskpct(ty, rr), PCT, fill, True); pput(rr, tcol(ty, 'GP/kg'), f"=IFERROR({CL(tcol(ty, 'GP THB M'))}{rr}/{TL[ty]}{rr}*1000,\"\")", DEC, fill, True)
            pput(rr, RKP, f"=IFERROR(({TL['1']}{rr}+{TL['2']}{rr}+{TL['3']}{rr})/{PLAN_T(rr)},\"\")", PCT, fill, True)
        for zi, zname in enumerate(['Below floor', 'Floor to target', 'Target and above']):
            crit = f'$B${blk0}:$B${blk1},"{zname}"'
            pput(r, 1, 'Σ ' + zname, fill=ZONEF[zname], bold=True); pput(r, 2, zname, fill=ZONEF[zname], bold=True)
            for col in SUMC: pput(r, col, f"=SUMIFS({prng(col)},{crit})", fmt_of(col), bold=True)
            pput(r, 5, f"=IFERROR(D{r}/D${TR},\"\")", PCT, bold=True); pput(r, 10, f"=IFERROR(I{r}/I${TR},\"\")", PCT, bold=True); pput(r, 20, f"=IFERROR(S{r}/S${TR},\"\")", PCT, bold=True)
            pput(r, 6, f"=IFERROR(G{r}/D{r}*1000,\"\")", DEC, bold=True); pput(r, 11, f"=IFERROR(L{r}/I{r}*1000,\"\")", DEC, bold=True); pput(r, 21, f"=IFERROR(V{r}/S{r}*1000,\"\")", DEC, bold=True)
            pput(r, 15, f"=IFERROR(SUMPRODUCT(($B${blk0}:$B${blk1}=\"{zname}\")*{prng(14)}*{prng(15)})/SUMIFS({prng(14)},{crit}),\"\")", DEC, bold=True)
            pput(r, 18, f"=IFERROR(SUMPRODUCT(($B${blk0}:$B${blk1}=\"{zname}\")*{prng(17)}*{prng(18)})/SUMIFS({prng(17)},{crit}),\"\")", DEC, bold=True)
            riskratios(r)
            for j in range(3, PNC + 1): ws.cell(row=r, column=j).fill = PatternFill('solid', fgColor=ZONEF[zname])
            for j in range(1, PNC + 1): ws.cell(row=r, column=j).border = Border(top=thin if zi == 0 else None)
            r += 1
        z1, z3 = TR - 3, TR - 1
        pput(r, 1, 'Total ' + rx + ' (your mix)', fill=GREY, bold=True)
        for col in SUMC: pput(r, col, f"=SUM({CL(col)}{z1}:{CL(col)}{z3})", fmt_of(col), GREY, True)
        pput(r, 5, 1 if T25 else None, PCT, GREY, True); pput(r, 10, 1 if T26 else None, PCT, GREY, True); pput(r, 20, f"=IFERROR(S{r}/S{r},\"\")", PCT, GREY, True)
        pput(r, 6, f"=IFERROR(G{r}/D{r}*1000,\"\")", DEC, GREY, True); pput(r, 11, f"=IFERROR(L{r}/I{r}*1000,\"\")", DEC, GREY, True)
        pput(r, 15, f"=IFERROR(SUMPRODUCT({prng(14)},{prng(15)})/N{r},\"\")", DEC, GREY, True); pput(r, 18, f"=IFERROR(SUMPRODUCT({prng(17)},{prng(18)})/Q{r},\"\")", DEC, GREY, True)
        pput(r, 21, f"=IFERROR(V{r}/S{r}*1000,\"\")", DEC, GREY, True); riskratios(r, GREY)
        for j in range(1, PNC + 1): ws.cell(row=r, column=j).border = Border(top=thin)
        r += 1
        pput(r, 1, f'LOCKED: AP27 {plabel} plant tonnes and GP/kg', fill='D9D9D9', bold=True)
        pput(r, 13, 1 if RYT else None, PCT, 'D9D9D9', True); pput(r, 14, round(RYT), NUM, 'D9D9D9', True); pput(r, 15, t_ry, DEC, 'D9D9D9', True)
        pput(r, 16, 1 if TKT_ else None, PCT, 'D9D9D9', True); pput(r, 17, round(TKT_), NUM, 'D9D9D9', True); pput(r, 18, t_tk, DEC, 'D9D9D9', True)
        pput(r, 19, round(TOT), NUM, 'D9D9D9', True); pput(r, 20, 1 if TOT else None, PCT, 'D9D9D9', True); pput(r, 21, (RYG + TKG) / TOT if TOT else None, DEC, 'D9D9D9', True); pput(r, 22, (RYG + TKG) / 1000, MB, 'D9D9D9', True)
        pput(r, RK, '=' + PLAN_T(r - 1), NUM, 'D9D9D9', True); pput(r, RK + 1, 'risk types 1+2+3+0 tonnes (= plan t)', fill='D9D9D9', italic=True, color='595959')
        LR = r; r += 1
        pput(r, 1, 'CHECK (should be 0): your mix minus locked', bold=True, color='C62828')
        for col, fmt in ((13, '+0.0%;-0.0%;0.0%'), (14, '+#,##0;-#,##0;0'), (15, '+0.00;-0.00;0.00'), (16, '+0.0%;-0.0%;0.0%'), (17, '+#,##0;-#,##0;0'), (18, '+0.00;-0.00;0.00'), (19, '+#,##0;-#,##0;0'), (21, '+0.00;-0.00;0.00'), (22, '+#,##0.0;-#,##0.0;0.0')):
            pput(r, col, f"=IFERROR({CL(col)}{TR}-{CL(col)}{LR},\"\")", fmt, bold=True, color='C62828')
        pput(r, RK, f"={CL(RK)}{LR}-S{LR}", '+#,##0;-#,##0;0', bold=True, color='C62828'); pput(r, RK + 1, 'risk types minus locked t', italic=True, color='595959')
        r += 2
    for j in (3, 8, 13, 16, 19) + tuple(tcol(ty, 'Tonnes') for ty in TYO) + (RKP,):
        for rr in range(4, r):
            c = ws.cell(row=rr, column=j); c.border = Border(left=Side(style='thin', color='FFFFFF' if rr == 4 else NAVY), top=c.border.top, bottom=c.border.bottom)
    for j in range(1, PNC + 1):
        c = ws.cell(row=4, column=j); c.border = Border(left=c.border.left, top=Side(style='thin', color='FFFFFF'), bottom=Side(style='thin', color='FFFFFF'))
    pnotes = ['How to use',
              '1. Start from the AP mix (defaults). Change the yellow % of RY / % of TKT cells to move volume between tiers; keep each plant column summing to 100% (CHECK row = 0).',
              '2. The plant GP/kg per tier (yellow) is the price position of that tier; adjust it only if you expect the tier itself to be priced differently.',
              '3. Read the result: Total GP/kg per plant and for the two plants vs the LOCKED AP27 values; the CHECK row shows the gap. A mix that moves tonnes down a tier must be offset by tonnes up a tier to hold the lock.',
              '4. Star rows (blue italic) are memo lines for key accounts inside the tier above; they are not summed. The three Σ rows sum the tiers by zone.',
              f'5. This sheet works on {plabel}. Sister sheets: 2027 plug FY / Q1 / Q2 / Q3 / Q4. Quarterly phasing side by side and the price-action case are on the Tier mapping sheet.',
              '6. Risk profile blocks (static, AP plan of this period, Rayong + TKT): 1 = new customer (no 2025/26 sales), 2 = existing customer but new SKU, 3 = same customer and SKU but the plan quarter is more than +30% of the best 2026 quarter, 0 = running base within +30%. '
              'One type per customer x SN, identical to the risk file (HVA 2027 Q1-Q4 volume delivery risk). Each block: Tonnes, % vol = share of the row plan tonnes (on Total rows = share of the reaction), GP/kg and GP THB M = AP plan product GP of those lines (plant basis), # cust = customer groups with at least 1 t. '
              'The four 2027 blocks add up to the row plan tonnes (LOCKED row shows the tie-out). % at risk = (1 + 2 + 3) / plan tonnes of the row. '
              'x block = 2026 YTD actuals (tonnes, product GP/kg, GP, # cust) of customer x SN sold in 2025/26 but not in the 2027 plan, placed in the customer 2026 tier; % vol = share of the row 2026 YTD tonnes. A memo of what the tier used to carry, not part of the plug.']
    for i, n in enumerate(pnotes):
        c = ws.cell(row=r + i, column=1, value=n)
        if i == 0: c.font = Font(bold=True, color=NAVY)
    ws.freeze_panes = 'C6'; ws.sheet_properties.pageSetUpPr = openpyxl.worksheet.properties.PageSetupProperties(fitToPage=True); ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
for p_, sname_, plabel_ in PLUG: build_plug(p_, sname_, plabel_)

'''
out = src[:ia] + NEW + src[ib:]
out = out.replace('HVA GP tier tracker 2027 v11.xlsx', 'HVA GP tier tracker 2027 v13.xlsx')
old_move = "wb.move_sheet('2027 plug-and-play', offset=wb.sheetnames.index('Tier mapping 25-26-27') + 1 - wb.sheetnames.index('2027 plug-and-play'))"
assert old_move in out
out = out.replace(old_move, "for i_, (p_, sname_, _) in enumerate(PLUG): wb.move_sheet(sname_, offset=wb.sheetnames.index('Tier mapping 25-26-27') + 1 + i_ - wb.sheetnames.index(sname_))")
old_rd = "    wr['A11'].alignment = Alignment(wrap_text=True, vertical='top')\n"
assert old_rd in out
out = out.replace(old_rd, old_rd + "    wr['A12'] = ('v12-v13 (20 Oct 2026): the plug-and-play sheet is now five sheets - 2027 plug FY, Q1, Q2, Q3, Q4 - each with 2025 / 2026 YTD actuals, the plug block for that period (inputs, LOCKED, CHECK) and five risk-profile blocks (types 1 / 2 / 3 / 0 of the period plan, same classification as the risk file, one type per customer x SN; x = 2026 YTD actuals not in the 2027 plan, memo in the customer 2026 tier), each with Tonnes, % vol, GP/kg, GP THB M and # cust, plus % at risk.')\n    wr['A12'].alignment = Alignment(wrap_text=True, vertical='top')\n")

# ---- v14: tiers on the customer's tonne-weighted plan GP/kg across Rayong + TKT (plant basis, as booked in the AP); no Rayong-cost adjustment ----
REPL = [
 ("for l in lines: l['gap'] = 0.0 if l['plant'] == 'RY' else gap_sn.get((l['rx'], l['sn']), GAP.get(l['rx'], 0.0))",
  "for l in lines: l['gap'] = 0.0   # v14: no Rayong-cost adjustment; customer GP/kg = tonne-weighted plan GP/kg across both plants"),
 ("'2027 tier = commercial GP/kg at Rayong cost (TKT rows less the measured same-SN cost gap). % vol = share of the reaction (total column) or of that plant volume (Rayong / TKT columns).'",
  "'2027 tier = the customer tonne-weighted plan product GP/kg across Rayong + TKT (plant basis, as booked in the AP). % vol = share of the reaction (total column) or of that plant volume (Rayong / TKT columns).'"),
 ('(f" · measured cost gap RY–TKT {GAP[rx]:.2f}" if rx in GAP else \'\')', '(f" · RY–TKT cost gap {GAP[rx]:.2f} (info only, not applied)" if rx in GAP else \'\')'),
 ("'Measured cost gap RY-TKT'", "'RY-TKT cost gap (info only)'"),
 ("'Plan plant GP/kg', 'Cost gap to RY', 'Commercial GP/kg (line)', 'Customer commercial GP/kg (FY)', 'Tier (customer)', 'Zone', 'Action', 'Commercial GP/kg after action', 'Plant GP/kg after action'",
  "'Plan plant GP/kg', 'Cost gap (not applied)', 'Line GP/kg', 'Customer weighted GP/kg (FY)', 'Tier (customer)', 'Zone', 'Action', 'GP/kg after action', 'Plant GP/kg after action'"),
 ("Two-plant GP/kg here is on plant basis (tonne-weighted Rayong + TKT), unlike the commercial (Rayong-cost) basis on the Tier mapping sheet.",
  "All GP/kg on this sheet = plan product GP/kg as booked at each plant; the tier of a customer = its tonne-weighted GP/kg across Rayong + TKT, so tier, zone and the risk blocks are on one basis."),
 ("    wr['A12'].alignment = Alignment(wrap_text=True, vertical='top')\n",
  "    wr['A12'].alignment = Alignment(wrap_text=True, vertical='top')\n    wr['A13'] = ('v14 (20 Oct 2026): tier basis changed - a customer is placed by its tonne-weighted plan product GP/kg across Rayong + TKT as booked in the AP (plant basis). The earlier Rayong-cost (commercial) adjustment for TKT volume is dropped, so tier / zone / GP/kg / GP THB M are on one basis everywhere (Tier mapping, plug sheets, Line list). The RY-TKT cost gap is kept on Tier definition for information only.')\n    wr['A13'].alignment = Alignment(wrap_text=True, vertical='top')\n"),
 ("HVA GP tier tracker 2027 v13.xlsx", "HVA GP tier tracker 2027 v15.xlsx"),

 ("'2025 t (cust×reaction)', '2025 GP/kg', '2026 YTD t', '2026 GP/kg', 'New account?'",
  "'2025 t (this SN)', '2025 GP/kg (SN)', '2026 YTD t (SN)', '2026 GP/kg (SN)', '2025 t (cust×reaction)', '2026 YTD t (cust×reaction)', 'New account?'"),
 ("wid = [8, 7, 6, 30, 8, 30, 9, 10, 11, 8, 14, 9, 8, 9, 8, 8, 9, 7, 7, 7, 7, 9, 8, 10, 11, 12, 16, 30, 10, 10, 9, 9, 10, 12, 10]",
  "wid = [8, 7, 6, 30, 8, 30, 9, 10, 11, 8, 14, 9, 8, 9, 8, 10, 10, 8, 9, 7, 7, 7, 7, 9, 8, 10, 11, 12, 16, 30, 10, 10, 9, 9, 10, 12, 10]"),
 ("                h.get('t25') or None, round(h['gp25'] / 1000, 2) if h.get('gp25') is not None else None, h.get('t26') or None, round(h['gp26'] / 1000, 2) if h.get('gp26') is not None else None,\n",
  "                round(sh['t25'], 1) or None, round(sh['g25'] / sh['t25'] / 1000, 2) if sh['t25'] else None, round(sh['t26'], 1) or None, round(sh['g26'] / sh['t26'] / 1000, 2) if sh['t26'] else None, h.get('t25') or None, h.get('t26') or None,\n"),
 ("    c = C[(l['rx'], l['key'])]; h = c['h'] or {}; v = sum(l['vol']); gpl = sum(l['gp']) / v / 1000; gcl = gpl - l['gap']; up = c['g_act'] - c['g']; zn = zone_g(l['rx'], c['g'])",
  "    c = C[(l['rx'], l['key'])]; h = c['h'] or {}; sh = SNH[(l['key'], l['sn'])]; v = sum(l['vol']); gpl = sum(l['gp']) / v / 1000; gcl = gpl - l['gap']; up = c['g_act'] - c['g']; zn = zone_g(l['rx'], c['g'])"),
 ("    ws3.cell(row=i, column=26).fill = PatternFill('solid', fgColor=ZONEF[zn]); ws3.cell(row=i, column=27).fill = PatternFill('solid', fgColor=ZONEF[zn])",
  "    ws3.cell(row=i, column=28).fill = PatternFill('solid', fgColor=ZONEF[zn]); ws3.cell(row=i, column=29).fill = PatternFill('solid', fgColor=ZONEF[zn])"),
 ("    wr['A13'].alignment = Alignment(wrap_text=True, vertical='top')\n",
  "    wr['A13'].alignment = Alignment(wrap_text=True, vertical='top')\n    wr['A14'] = ('v15 (20 Oct 2026): Line list history columns are now per customer x SN (2025 t, 2025 GP/kg, 2026 YTD t, 2026 GP/kg of that SN, both plants), with the customer x reaction totals in two separate columns; previously the customer x reaction total was repeated on every SN line.')\n    wr['A14'].alignment = Alignment(wrap_text=True, vertical='top')\n"),
]
for a_, b_ in REPL:
    assert a_ in out, a_[:60]
    out = out.replace(a_, b_)
open('tier10.py', 'w', encoding='utf-8').write(out); print('tier10.py written', len(out))

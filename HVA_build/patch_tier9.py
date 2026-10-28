"""Create tier9.py from tier8.py: zone subtotal rows, blue key-account memo rows, and a '2027 plug-and-play' sheet."""
import io, shutil
shutil.copy('tier8.py', 'tier9.py')
s = io.open('tier9.py', encoding='utf-8').read()
R = []
def rep(a, b):
    global s
    assert a in s, a[:90]; s = s.replace(a, b, 1); R.append(a[:40])
rep('v10.xlsx"', 'v11.xlsx"')
# A. blue memo rows
rep("""        if memo:
            for j in range(3, NC + 1): ws.cell(row=r, column=j).font = Font(italic=True, color='404040')
            ws.cell(row=r, column=1).font = Font(bold=True, italic=True, color='1F3A5F')""",
"""        if memo:
            for j in range(2, NC + 1): ws.cell(row=r, column=j).font = Font(italic=True, color=BLUE)
            ws.cell(row=r, column=1).font = Font(bold=True, italic=True, color=BLUE)""")
rep("NAVY = '1F3A5F'; HFNT = Font(bold=True, color='FFFFFF')", "NAVY = '1F3A5F'; BLUE = '0000FF'; HFNT = Font(bold=True, color='FFFFFF')")
# B. block start marker + zone rows before the Total row
rep("    r += 1; over = []; grouped = []\n    keys_by_tier = collections.defaultdict(list)",
    "    r += 1; over = []; grouped = []; blk0 = r\n    keys_by_tier = collections.defaultdict(list)")
rep("""    for rr in grouped:
        ws.row_dimensions[rr].outline_level = 1; ws.row_dimensions[rr].hidden = True
    for j in range(1, NC + 1): ws.cell(row=r, column=j).fill = PatternFill('solid', fgColor=GREY); ws.cell(row=r, column=j).border = Border(top=thin)""",
"""    for rr in grouped:
        ws.row_dimensions[rr].outline_level = 1; ws.row_dimensions[rr].hidden = True
    # ---- zone subtotal rows (formulas over the tier rows of this block; star memo rows are excluded because their zone text carries the GP/kg suffix) ----
    blk1 = r - 1; TR = r + 3
    SUMC = [3, 4, 7, 8, 9, 12, 13, 14, 15, 19, 20, 23] + [c for qi in range(4) for c in (QB + QW * qi, QB + QW * qi + 1, QB + QW * qi + 4, QB + QW * qi + 7)] + [AB, AB + 1, AB + 4, AB + 5]
    PCTC = {5: 4, 10: 9, 16: 15, 21: 20, 24: 23, AB + 2: AB + 1}
    for qi in range(4): b = QB + QW * qi; PCTC[b + 2] = b + 1; PCTC[b + 5] = b + 4; PCTC[b + 8] = b + 7
    RATIO = {6: (7, 4), 11: (12, 9), 18: (19, 15), AB + 3: (AB + 4, AB + 1)}          # GP THB M / tonnes * 1000
    WAVG = {22: 20, 25: 23}                                                            # SUMPRODUCT(tonnes x GP/kg) / tonnes
    for qi in range(4): b = QB + QW * qi; WAVG[b + 3] = b + 1; WAVG[b + 6] = b + 4; WAVG[b + 9] = b + 7
    def rng(col): return f"{CL(col)}${blk0}:{CL(col)}${blk1}"
    for zi, zname in enumerate(['Below floor', 'Floor to target', 'Target and above']):
        crit = f'$B${blk0}:$B${blk1},"{zname}"'
        put(r, 1, '\\u03a3 ' + zname, fill=ZONEF[zname], bold=True); put(r, 2, zname, fill=ZONEF[zname], bold=True)
        for col in SUMC: put(r, col, f"=SUMIFS({rng(col)},{crit})", NUM if col not in (7, 12, 19, AB + 4, AB + 5) else MB, bold=True)
        for col, tcol in PCTC.items(): put(r, col, f"=IFERROR({CL(tcol)}{r}/{CL(tcol)}${TR},\\"\\")", PCT, bold=True)
        for col, (gcol, tcol) in RATIO.items(): put(r, col, f"=IFERROR({CL(gcol)}{r}/{CL(tcol)}{r}*1000,\\"\\")", DEC, bold=True)
        for col, tcol in WAVG.items(): put(r, col, f"=IFERROR(SUMPRODUCT(($B${blk0}:$B${blk1}=\\"{zname}\\")*{rng(tcol)}*{rng(col)})/SUMIFS({rng(tcol)},{crit}),\\"\\")", DEC, bold=True)
        put(r, 26, f"=IFERROR(({CL(16)}{r}-{CL(5)}{r})*100,\\"\\")", '+0;-0;0', bold=True)
        for j in range(1, NC + 1):
            c_ = ws.cell(row=r, column=j); c_.border = Border(top=thin if zi == 0 else None, left=c_.border.left, bottom=c_.border.bottom)
            if j > 2: c_.fill = PatternFill('solid', fgColor=ZONEF[zname])
        r += 1
    for j in range(1, NC + 1): ws.cell(row=r, column=j).fill = PatternFill('solid', fgColor=GREY); ws.cell(row=r, column=j).border = Border(top=thin)""")
# C. notes line about zone rows & blue
rep("""notes = ['Reading the sheet',
         '- Tier rows include all customers.""", """notes = ['Reading the sheet',
         '- Blue italic star rows are memo lines (key accounts): they are already inside the tier above them and are NOT added again. The three \\u03a3 rows per reaction sum the tier rows by zone (formulas); the Total row is the reaction total.',
         '- Tier rows include all customers.""")
# D. plug-and-play sheet, inserted before Tier definition
PLUG = r'''
# ===================== 2027 plug-and-play =====================
ws = fresh('2027 plug-and-play', 2); ws.sheet_view.showGridLines = False
ws['A1'] = '2027 plug-and-play: change the % of volume per tier and plant, keep each plant volume and GP/kg target fixed'; ws['A1'].font = Font(bold=True, size=13, color=NAVY)
ws['A2'] = ('Yellow cells are inputs: % of Rayong volume and % of TKT volume per tier (each column must add to 100%), and the plant GP/kg per tier (defaults = AP plan; for tiers with no plan volume the default is the tier mid-point, plus the RY-TKT cost gap for TKT). '
            'Everything else is a formula. The LOCKED row holds the AP27 plant tonnes and plant GP/kg (and their combination for the two plants); the CHECK row shows the gap of your mix to those locks - aim for zero. '
            '2025 / 2026 columns are actuals for reference. Note: here the 2-plant GP/kg is on plant basis (tonne-weighted Rayong + TKT), unlike the commercial (Rayong-cost) basis on the Tier mapping sheet.')
ws['A2'].alignment = Alignment(wrap_text=True, vertical='top'); ws.merge_cells('A2:W2'); ws.row_dimensions[2].height = 66
pcols = [('', 'Tier (THB/kg)'), ('', 'Zone')]
for lab in ('2025 actual (FY)', '2026 YTD (Jan-Sep)'): pcols += [(lab, s_) for s_ in ('# cust', 'Tonnes', '% vol', 'GP/kg', 'GP THB M')]
pcols += [('2027 Rayong (plug)', s_) for s_ in ('% of RY  [input]', 'Tonnes', 'GP/kg  [input]')] + [('2027 TKT (plug)', s_) for s_ in ('% of TKT  [input]', 'Tonnes', 'GP/kg  [input]')]
pcols += [('2027 two plants (result)', s_) for s_ in ('Tonnes', '% vol', 'GP/kg', 'GP THB M', '# cust (plan)')]
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
ws.row_dimensions[5].height = 32
INP = 'FFF2CC'
def pput(r, col, v, fmt=None, fill=None, bold=False, color=None, italic=False):
    c = ws.cell(row=r, column=col, value=v)
    if fmt: c.number_format = fmt
    if fill: c.fill = PatternFill('solid', fgColor=fill)
    if bold or color or italic: c.font = Font(bold=bold, color=color, italic=italic)
    return c
r = 6
for rx in RX:
    rows = ROWS[rx]; t_ry, t_tk = APT.get((rx, 'RY')), APT.get((rx, 'TKT'))
    T25, T26 = tot_of(rx, '25', 't'), tot_of(rx, '26', 't'); RYT, TKT_, TOT = tot_of(rx, 'FY', 'ry_t'), tot_of(rx, 'FY', 'tk_t'), tot_of(rx, 'FY', 't')
    RYG, TKG = tot_of(rx, 'FY', 'ry_gp'), tot_of(rx, 'FY', 'tk_gp')
    pput(r, 1, rx).font = Font(bold=True, size=12, color=NAVY)
    pput(r, 3, f"tier gap {GRIDTXT[rx]} · locked: Rayong {RYT:,.0f} t @ {t_ry or 0:.2f}" + (f" · TKT {TKT_:,.0f} t @ {t_tk:.2f}" if TKT_ else '') + f" · two plants {TOT:,.0f} t @ {(RYG + TKG) / TOT:.2f} (plant basis)").font = Font(italic=True, color='595959')
    for j in range(1, PNC + 1): ws.cell(row=r, column=j).border = Border(top=med)
    r += 1; blk0 = r
    keys_by_tier = collections.defaultdict(list)
    for k in KEYS[rx]: keys_by_tier[C[(rx, k)]['tier']].append(k)
    cuts_ = cuts(rx)
    for rid in rows:
        cell = CELL[(rx, rid)]; i = rid[1]
        if all(cell[p]['t'] < 1.0 for p in ('25', '26', 'FY')) and not (0 < i < len(cuts_)): continue   # keep every in-grid tier (plug targets), drop empty open-ended ends
        zn = zone(rx, i); x, y, zz = cell['25'], cell['26'], cell['FY']
        mid = (cuts_[i - 1] + cuts_[i]) / 2 if 0 < i < len(cuts_) else (cuts_[0] - 0.25 if i == 0 else cuts_[-1] + 0.25)
        pput(r, 1, tname(rx, i), fill=ZONEF[zn]); pput(r, 2, zn, fill=ZONEF[zn])
        pput(r, 3, x['n'] or None, NUM); pput(r, 4, round(x['t']) or None, NUM); pput(r, 5, x['t'] / T25 if T25 and x['t'] else None, PCT); pput(r, 6, x['gp'] / x['t'] if x['t'] else None, DEC); pput(r, 7, x['gp'] / 1000 if x['t'] else None, MB)
        pput(r, 8, y['n'] or None, NUM); pput(r, 9, round(y['t']) or None, NUM); pput(r, 10, y['t'] / T26 if T26 and y['t'] else None, PCT); pput(r, 11, y['gp'] / y['t'] if y['t'] else None, DEC); pput(r, 12, y['gp'] / 1000 if y['t'] else None, MB)
        pput(r, 13, zz['ry_t'] / RYT if RYT else 0, PCT, INP); pput(r, 14, f"=M{r}*$N${{TR}}", NUM); pput(r, 15, (zz['ry_gp'] / zz['ry_t']) if zz['ry_t'] else round(mid, 2), DEC, INP)
        pput(r, 16, zz['tk_t'] / TKT_ if TKT_ else 0, PCT, INP); pput(r, 17, f"=P{r}*$Q${{TR}}", NUM); pput(r, 18, (zz['tk_gp'] / zz['tk_t']) if zz['tk_t'] else round(mid + GAP.get(rx, 0.0), 2), DEC, INP)
        pput(r, 19, f"=N{r}+Q{r}", NUM); pput(r, 20, f"=IFERROR(S{r}/$S${{TR}},\"\")", PCT); pput(r, 21, f"=IFERROR((N{r}*O{r}+Q{r}*R{r})/S{r},\"\")", DEC); pput(r, 22, f"=(N{r}*O{r}+Q{r}*R{r})/1000", MB); pput(r, 23, zz['n'] or None, NUM)
        r += 1
        for k in keys_by_tier.get(i, []):
            c = C[(rx, k)]; kc = CELL[(rx, ('key', k))]; kz = kc['FY']; k25 = kc['25']; k26 = kc['26']
            pput(r, 1, '★ ' + c['grp'][:34], fill=ZONEF[zn], bold=True, italic=True, color=BLUE).alignment = Alignment(indent=2)
            pput(r, 2, f"{zone_g(rx, c['g'])} · {c['g']:.2f}", fill=ZONEF[zn], italic=True, color=BLUE)
            vals = {3: k25['n'] or None, 4: round(k25['t']) or None, 5: k25['t'] / T25 if T25 and k25['t'] else None, 6: k25['gp'] / k25['t'] if k25['t'] else None, 7: k25['gp'] / 1000 if k25['t'] else None,
                    8: k26['n'] or None, 9: round(k26['t']) or None, 10: k26['t'] / T26 if T26 and k26['t'] else None, 11: k26['gp'] / k26['t'] if k26['t'] else None, 12: k26['gp'] / 1000 if k26['t'] else None,
                    13: kz['ry_t'] / RYT if RYT else None, 14: round(kz['ry_t']) or None, 15: kz['ry_gp'] / kz['ry_t'] if kz['ry_t'] else None, 16: kz['tk_t'] / TKT_ if TKT_ else None, 17: round(kz['tk_t']) or None, 18: kz['tk_gp'] / kz['tk_t'] if kz['tk_t'] else None,
                    19: round(kz['t']) or None, 20: kz['t'] / TOT if TOT else None, 21: (kz['ry_gp'] + kz['tk_gp']) / kz['t'] if kz['t'] else None, 22: (kz['ry_gp'] + kz['tk_gp']) / 1000 if kz['t'] else None, 23: 1}
            fm_ = {3: NUM, 4: NUM, 5: PCT, 6: DEC, 7: MB, 8: NUM, 9: NUM, 10: PCT, 11: DEC, 12: MB, 13: PCT, 14: NUM, 15: DEC, 16: PCT, 17: NUM, 18: DEC, 19: NUM, 20: PCT, 21: DEC, 22: MB, 23: NUM}
            for col, v in vals.items(): pput(r, col, v, fm_[col], italic=True, color=BLUE)
            r += 1
    blk1 = r - 1; TR = r + 3
    # replace the {TR} placeholders in this block's formulas now that TR is known
    for rr in range(blk0, blk1 + 1):
        for col in (14, 17, 20):
            v = ws.cell(row=rr, column=col).value
            if isinstance(v, str) and '{TR}' in v: ws.cell(row=rr, column=col).value = v.replace('{TR}', str(TR))
    def prng(col): return f"{CL(col)}${blk0}:{CL(col)}${blk1}"
    for zi, zname in enumerate(['Below floor', 'Floor to target', 'Target and above']):
        crit = f'$B${blk0}:$B${blk1},"{zname}"'
        pput(r, 1, 'Σ ' + zname, fill=ZONEF[zname], bold=True); pput(r, 2, zname, fill=ZONEF[zname], bold=True)
        for col in (3, 4, 7, 8, 9, 12, 13, 14, 16, 17, 19, 22, 23): pput(r, col, f"=SUMIFS({prng(col)},{crit})", PCT if col in (13, 16) else (MB if col in (7, 12, 22) else NUM), bold=True)
        pput(r, 5, f"=IFERROR(D{r}/D${TR},\"\")", PCT, bold=True); pput(r, 10, f"=IFERROR(I{r}/I${TR},\"\")", PCT, bold=True); pput(r, 20, f"=IFERROR(S{r}/S${TR},\"\")", PCT, bold=True)
        pput(r, 6, f"=IFERROR(G{r}/D{r}*1000,\"\")", DEC, bold=True); pput(r, 11, f"=IFERROR(L{r}/I{r}*1000,\"\")", DEC, bold=True); pput(r, 21, f"=IFERROR(V{r}/S{r}*1000,\"\")", DEC, bold=True)
        pput(r, 15, f"=IFERROR(SUMPRODUCT(($B${blk0}:$B${blk1}=\"{zname}\")*{prng(14)}*{prng(15)})/SUMIFS({prng(14)},{crit}),\"\")", DEC, bold=True)
        pput(r, 18, f"=IFERROR(SUMPRODUCT(($B${blk0}:$B${blk1}=\"{zname}\")*{prng(17)}*{prng(18)})/SUMIFS({prng(17)},{crit}),\"\")", DEC, bold=True)
        for j in range(3, PNC + 1): ws.cell(row=r, column=j).fill = PatternFill('solid', fgColor=ZONEF[zname])
        for j in range(1, PNC + 1): ws.cell(row=r, column=j).border = Border(top=thin if zi == 0 else None)
        r += 1
    # Total row (formulas = sum of the three zone rows)
    z1, z3 = TR - 3, TR - 1
    pput(r, 1, 'Total ' + rx + ' (your mix)', fill=GREY, bold=True)
    for col in (3, 4, 7, 8, 9, 12, 13, 14, 16, 17, 19, 22, 23): pput(r, col, f"=SUM({CL(col)}{z1}:{CL(col)}{z3})", PCT if col in (13, 16) else (MB if col in (7, 12, 22) else NUM), GREY, True)
    pput(r, 5, 1 if T25 else None, PCT, GREY, True); pput(r, 10, 1 if T26 else None, PCT, GREY, True); pput(r, 20, f"=IFERROR(S{r}/S{r},\"\")", PCT, GREY, True)
    pput(r, 6, f"=IFERROR(G{r}/D{r}*1000,\"\")", DEC, GREY, True); pput(r, 11, f"=IFERROR(L{r}/I{r}*1000,\"\")", DEC, GREY, True)
    pput(r, 15, f"=IFERROR(SUMPRODUCT({prng(14)},{prng(15)})/N{r},\"\")", DEC, GREY, True); pput(r, 18, f"=IFERROR(SUMPRODUCT({prng(17)},{prng(18)})/Q{r},\"\")", DEC, GREY, True)
    pput(r, 21, f"=IFERROR(V{r}/S{r}*1000,\"\")", DEC, GREY, True)
    for j in range(1, PNC + 1): ws.cell(row=r, column=j).border = Border(top=thin)
    r += 1
    # LOCKED row (AP27 plan)
    pput(r, 1, 'LOCKED: AP27 plant tonnes and GP/kg', fill='D9D9D9', bold=True)
    pput(r, 13, 1, PCT, 'D9D9D9', True); pput(r, 14, round(RYT), NUM, 'D9D9D9', True); pput(r, 15, t_ry, DEC, 'D9D9D9', True)
    pput(r, 16, 1 if TKT_ else None, PCT, 'D9D9D9', True); pput(r, 17, round(TKT_), NUM, 'D9D9D9', True); pput(r, 18, t_tk, DEC, 'D9D9D9', True)
    pput(r, 19, round(TOT), NUM, 'D9D9D9', True); pput(r, 20, 1, PCT, 'D9D9D9', True); pput(r, 21, (RYG + TKG) / TOT if TOT else None, DEC, 'D9D9D9', True); pput(r, 22, (RYG + TKG) / 1000, MB, 'D9D9D9', True)
    LR = r; r += 1
    # CHECK row
    pput(r, 1, 'CHECK (should be 0): your mix minus locked', bold=True, color='C62828')
    for col, fmt in ((13, '+0.0%;-0.0%;0.0%'), (14, '+#,##0;-#,##0;0'), (15, '+0.00;-0.00;0.00'), (16, '+0.0%;-0.0%;0.0%'), (17, '+#,##0;-#,##0;0'), (18, '+0.00;-0.00;0.00'), (19, '+#,##0;-#,##0;0'), (21, '+0.00;-0.00;0.00'), (22, '+#,##0.0;-#,##0.0;0.0')):
        pput(r, col, f"=IFERROR({CL(col)}{TR}-{CL(col)}{LR},\"\")", fmt, bold=True, color='C62828')
    r += 2
for j in (3, 8, 13, 16, 19):
    for rr in range(4, r):
        c = ws.cell(row=rr, column=j); c.border = Border(left=Side(style='thin', color='FFFFFF' if rr == 4 else NAVY), top=c.border.top, bottom=c.border.bottom)
for j in range(1, PNC + 1):
    c = ws.cell(row=4, column=j); c.border = Border(left=c.border.left, top=Side(style='thin', color='FFFFFF'), bottom=Side(style='thin', color='FFFFFF'))
pnotes = ['How to use',
          '1. Start from the AP mix (defaults). Change the yellow % of RY / % of TKT cells to move volume between tiers; keep each plant column summing to 100% (CHECK row = 0).',
          '2. The plant GP/kg per tier (yellow) is the price position of that tier; adjust it only if you expect the tier itself to be priced differently.',
          '3. Read the result: Total GP/kg per plant and for the two plants vs the LOCKED AP27 values; the CHECK row shows the gap. A mix that moves tonnes down a tier must be offset by tonnes up a tier to hold the lock.',
          '4. Star rows (blue italic) are memo lines for key accounts inside the tier above; they are not summed. The three Σ rows sum the tiers by zone.',
          '5. Quarterly phasing and the price-action case are on the Tier mapping sheet; this sheet works on full-year 2027 only.']
for i, n in enumerate(pnotes):
    c = ws.cell(row=r + i, column=1, value=n)
    if i == 0: c.font = Font(bold=True, color=NAVY)
ws.freeze_panes = 'C6'; ws.sheet_properties.pageSetUpPr = openpyxl.worksheet.properties.PageSetupProperties(fitToPage=True); ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
'''
rep("# ---- Tier definition ----", PLUG + "\n# ---- Tier definition ----")
rep("""    wr['A10'] = ('v9 (20 Oct 2026): key-account memo rows now carry the same colour as their tier. v8:""",
    """    wr['A11'] = ('v11 (20 Oct 2026): new sheet "2027 plug-and-play" (inputs = % of Rayong / % of TKT volume per tier and plant GP/kg per tier; plant tonnes and GP/kg locked to AP27; CHECK row). Three zone subtotal rows per reaction on both sheets (formulas). Key-account memo rows in blue italic: inside their tier, not summed again.')
    wr['A11'].alignment = Alignment(wrap_text=True, vertical='top')
    wr['A10'] = ('v9 (20 Oct 2026): key-account memo rows now carry the same colour as their tier. v8:""")
io.open('tier9.py', 'w', encoding='utf-8').write(s)
print('tier9.py written,', len(R), 'edits')

# Extract Por's manual format adjustments (column outline groups, hidden columns, column-A highlight fills,
# freeze panes, zoom) from the workbook she edited and store them in ..\memory\twin-format-profile.json.
# build_formula_xlsx.py re-applies the profile on every build.  Usage: python sync_format_profile.py <por_edited.xlsx>
import json, os, sys, openpyxl
from openpyxl.utils import column_index_from_string as CI
os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
out = os.path.join('..', 'memory', 'twin-format-profile.json')
prof = json.load(open(out, encoding='utf-8')) if os.path.exists(out) else {'_note': "Por's manual format adjustments to the TWIN profitability workbook (column groups / hidden columns / row highlights). Applied by build_formula_xlsx.py on every build. Re-sync with: python sync_format_profile.py <file Por edited>", 'sheets': {}}
wb = openpyxl.load_workbook(src)
for name in ['By customer', 'By customer-product', 'By country-tag', 'Summary', 'Reported vs Constant', 'Quarterly trend', 'Key findings', 'TDC product rates', 'FX']:
    if name not in wb.sheetnames: continue
    ws = wb[name]
    cols = {}
    for k, v in ws.column_dimensions.items():
        if v.outline_level or v.hidden or v.collapsed:
            cols[k] = {'level': v.outline_level or 0, 'hidden': bool(v.hidden), 'collapsed': bool(v.collapsed), 'width': round(v.width or 0, 2)}
    fills = {}
    for r in range(1, ws.max_row + 1):
        c = ws.cell(row=r, column=1); f = c.fill
        if f.fill_type == 'solid' and c.value and getattr(f.fgColor, 'theme', None) is not None and isinstance(f.fgColor.theme, int):
            fills[str(c.value)] = {'theme': f.fgColor.theme, 'tint': round(f.fgColor.tint or 0, 4)}
        elif f.fill_type == 'solid' and c.value and isinstance(getattr(f.fgColor, 'rgb', None), str) and f.fgColor.rgb not in ('FFF2F2F2', '00000000', 'FFE7E6E6', 'FFDDEBF7', 'FFE2EFDA', 'FFFFF2CC'):
            fills[str(c.value)] = {'rgb': f.fgColor.rgb}
    op = ws.sheet_properties.outlinePr
    prof['sheets'][name] = {'columns': cols, 'colA_fills': fills, 'freeze': ws.freeze_panes, 'zoom': ws.sheet_view.zoomScale,
                            'outline': {'summaryBelow': op.summaryBelow if op else True, 'summaryRight': op.summaryRight if op else True}}
    print(name, 'cols', len(cols), 'fills', len(fills), 'freeze', ws.freeze_panes)
prof['_source'] = os.path.basename(src)
json.dump(prof, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('saved', out)

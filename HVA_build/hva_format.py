"""Apply Por's stored format adjustments (memory/hva-format-profile.json) to a rebuilt HVA workbook.
Usage inside a builder, just before wb.save():  import hva_format; hva_format.apply(wb, 'tracker')   # or 'risk'
"""
import json, os
from openpyxl.styles import PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL

PROFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'memory', 'hva-format-profile.json')
NAVY = '1F3A5F'

def _group_spans(ws, row):
    """{group label: (first col, last col)} from a merged/un-merged group header row."""
    spans = {}
    merged = {(m.min_row, m.min_col): m.max_col for m in ws.merged_cells.ranges}
    for c in range(1, ws.max_column + 1):
        v = ws.cell(row=row, column=c).value
        if v not in (None, ''):
            spans[str(v)] = (c, merged.get((row, c), c))
    return spans

def _sub_col(ws, sub_row, label, lo=1, hi=None):
    hi = hi or ws.max_column
    for c in range(lo, hi + 1):
        if str(ws.cell(row=sub_row, column=c).value) == label: return c
    return None

def _expand_col_dims(ws):
    from openpyxl.utils import column_index_from_string
    items = list(ws.column_dimensions.items())
    for k, v in items:
        lo = v.min or column_index_from_string(k); hi = v.max or lo
        if hi > lo:
            w, hid, ol = v.width, bool(v.hidden), v.outline_level or 0
            del ws.column_dimensions[k]
            for i in range(lo, hi + 1):
                d = ws.column_dimensions[CL(i)]; d.width = w; d.hidden = hid; d.outline_level = ol

def _apply_sheet(ws, spec):
    if 'zoom' in spec: ws.sheet_view.zoomScale = spec['zoom']
    _expand_col_dims(ws)
    for letter, w in spec.get('col_widths_by_letter', {}).items(): ws.column_dimensions[letter].width = w
    hr = spec.get('header_rows', {}); g_row, s_row = hr.get('group'), hr.get('sub')
    if not g_row: return
    for old, new in spec.get('rename_group_headers', {}).items():
        for c in range(1, ws.max_column + 1):
            if ws.cell(row=g_row, column=c).value == old: ws.cell(row=g_row, column=c).value = new
    spans = _group_spans(ws, g_row)
    for g, w in spec.get('col_widths_by_group', {}).items():
        if g in spans:
            for c in range(spans[g][0], spans[g][1] + 1): ws.column_dimensions[CL(c)].width = w
    if s_row:
        for lab, rgb in spec.get('highlight_sub_headers', {}).items():
            c = _sub_col(ws, s_row, lab)
            if c: ws.cell(row=s_row, column=c).fill = PatternFill('solid', fgColor=rgb)
        if spec.get('sub_header_vertical'):
            for c in range(1, ws.max_column + 1):
                cell = ws.cell(row=s_row, column=c); a = cell.alignment
                cell.alignment = Alignment(horizontal=a.horizontal, vertical=spec['sub_header_vertical'], wrap_text=a.wrap_text, indent=a.indent)
        line = spec.get('actual_forecast_line')
        if line:
            lo, hi = spans.get(line['within_group'], (1, ws.max_column))
            c = _sub_col(ws, s_row, line['first_forecast_sub_label'], lo, hi)
            if c and c > 1:
                for r in range(g_row, ws.max_row + 1):
                    cur = ws.cell(row=r, column=c); cur.border = Border(left=None, right=cur.border.right, top=cur.border.top, bottom=cur.border.bottom)
                    prv = ws.cell(row=r, column=c - 1); prv.border = Border(left=prv.border.left, right=Side(style='thin'), top=prv.border.top, bottom=prv.border.bottom)
        for grp in spec.get('collapsed_groups', []):
            cols = []
            if 'whole_groups' in grp:
                for g in grp['whole_groups']:
                    if g in spans: cols += list(range(spans[g][0], spans[g][1] + 1))
            else:
                lo, hi = spans.get(grp.get('within_group'), (1, ws.max_column))
                cols = [c for c in (_sub_col(ws, s_row, lab, lo, hi) for lab in grp['sub_labels']) if c]
            if not cols: continue
            cols.sort()
            # contiguous runs -> one outline group each, collapsed
            run = [cols[0]]
            for c in cols[1:] + [None]:
                if c is not None and c == run[-1] + 1: run.append(c); continue
                for cc in run:
                    d = ws.column_dimensions[CL(cc)]; d.outline_level = 1; d.hidden = True
                run = [c] if c is not None else []
        ws.sheet_properties.outlinePr.summaryRight = True

def apply(wb, which):
    prof = json.load(open(PROFILE, encoding='utf-8')).get(which, {})
    done = []
    for sheet, spec in prof.items():
        if sheet in wb.sheetnames:
            _apply_sheet(wb[sheet], spec); done.append(sheet)
    print(f'format profile [{which}] applied to: {done}')

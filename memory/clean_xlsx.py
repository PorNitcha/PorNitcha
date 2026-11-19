"""Make a cleaned copy of an xlsx: drop broken/unused defined names, unused
external links (renumbering [n] refs), and calcChain. Cell values untouched."""
import zipfile, re, sys, html

src, dst = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(src)
parts = {n: zin.read(n) for n in zin.namelist()}
txt = lambda n: parts[n].decode('utf-8')

wb = txt('xl/workbook.xml')

# ---------- formula-bearing text (everything except names/links/strings) ----------
FORMULA_PARTS = [n for n in parts if n.endswith('.xml') and n.startswith('xl/') and not (
    n == 'xl/workbook.xml' or n.startswith('xl/externalLinks/') or n in
    ('xl/sharedStrings.xml', 'xl/styles.xml', 'xl/calcChain.xml') or n.startswith('xl/theme/'))]
FORMULA_PARTS += [n for n in parts if n.endswith('.vml')]
F_RE = re.compile(r'(<(?:f|formula|formula1|formula2|xm:f|c:f)\b[^>]*>)(.*?)(</(?:f|formula|formula1|formula2|xm:f|c:f)>)', re.S)
ATTR_RE = re.compile(r'((?:fmlaLink|fmlaRange|fmlaTxbx|fmlaGroup)="[^"]*")')
formula_text = []
for n in FORMULA_PARTS:
    t = txt(n)
    formula_text += [m.group(2) for m in F_RE.finditer(t)]
    formula_text += ATTR_RE.findall(t)
    formula_text += re.findall(r'<x:(?:FmlaLink|FmlaRange|FmlaTxbx)>(.*?)</x:', t)
TOK = re.compile(r'[A-Za-z_\\][\w.\\?]*')
def tokens(s): return {t.lower() for t in TOK.findall(html.unescape(s))}

# ---------- defined names ----------
DN_RE = re.compile(r'<definedName\b([^>]*)>(.*?)</definedName>|<definedName\b[^>]*/>', re.S)
dn = [(m.group(0), re.search(r'name="([^"]+)"', m.group(0)).group(1), m.group(2) or '') for m in DN_RE.finditer(wb)]
by_name = {}
for full, nm, val in dn: by_name.setdefault(nm.lower(), []).append(val)

used = set()
frontier = tokens('\n'.join(formula_text)) & set(by_name)
while frontier:
    used |= frontier
    nxt = set()
    for k in frontier:
        for v in by_name[k]:
            nxt |= tokens(v) & set(by_name)
    frontier = nxt - used

def keep_name(nm, val):
    if '#REF!' in val: return False
    if nm.lower().startswith('_xl'): return True          # built-ins: print area, _xlfn.*
    return nm.lower() in used
kept = [(f, n, v) for f, n, v in dn if keep_name(n, v)]

# ---------- external links ----------
EXT = re.compile(r'(?<![\w\]\.])\[(\d+)\](?!\])')
ext_used = set()
for s in formula_text + [v for _, _, v in kept]:
    ext_used |= {int(k) for k in EXT.findall(s)}

rels = txt('xl/_rels/workbook.xml.rels')
rel_target = {}
for r in re.findall(r'<Relationship\b[^>]*/>', rels):
    rel_target[re.search(r'Id="([^"]+)"', r).group(1)] = re.search(r'Target="([^"]+)"', r).group(1)
order = re.findall(r'<externalReference r:id="(rId\d+)"\s*/>', wb)
remap, new_refs, drop_rids = {}, [], []
for i, rid in enumerate(order, 1):
    if i in ext_used:
        remap[i] = len(new_refs) + 1; new_refs.append(rid)
    else:
        drop_rids.append(rid)
missing = ext_used - set(range(1, len(order) + 1))
assert not missing, f'formula refers to unknown ext index {missing}'

def renum(s): return EXT.sub(lambda m: f'[{remap[int(m.group(1))]}]', s)

# ---------- rewrite workbook.xml ----------
new_dn = ''.join(renum(f) for f, _, _ in kept)
wb = re.sub(r'<definedNames>.*?</definedNames>', f'<definedNames>{new_dn}</definedNames>' if kept else '', wb, flags=re.S)
wb = re.sub(r'<externalReferences>.*?</externalReferences>',
            ('<externalReferences>' + ''.join(f'<externalReference r:id="{r}"/>' for r in new_refs) + '</externalReferences>') if new_refs else '',
            wb, flags=re.S)
parts['xl/workbook.xml'] = wb.encode('utf-8')

# ---------- rewrite formulas in sheets/charts ----------
for n in FORMULA_PARTS:
    t = txt(n)
    t2 = F_RE.sub(lambda m: m.group(1) + renum(m.group(2)) + m.group(3), t)
    t2 = ATTR_RE.sub(lambda m: renum(m.group(1)), t2)
    if t2 != t: parts[n] = t2.encode('utf-8')

# ---------- drop link parts, calcChain; fix rels & content types ----------
drop_parts = ['xl/calcChain.xml']
for rid in drop_rids:
    p = 'xl/' + rel_target[rid].lstrip('/').replace('xl/', '', 1) if not rel_target[rid].startswith('/xl/') else rel_target[rid][1:]
    drop_parts += [p, p.replace('externalLinks/', 'externalLinks/_rels/') + '.rels']
drop_set = set(drop_parts)
for p in drop_set: parts.pop(p, None)
calc_rid = [k for k, v in rel_target.items() if v.endswith('calcChain.xml')]
for rid in drop_rids + calc_rid:
    rels = re.sub(rf'<Relationship\b[^>]*Id="{rid}"[^>]*/>', '', rels)
parts['xl/_rels/workbook.xml.rels'] = rels.encode('utf-8')
ct = txt('[Content_Types].xml')
ct = re.sub(r'<Override\b[^>]*PartName="/([^"]+)"[^>]*/>', lambda m: '' if m.group(1) in drop_set else m.group(0), ct)
parts['[Content_Types].xml'] = ct.encode('utf-8')

with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zo:
    for n in zin.namelist():
        if n in parts: zo.writestr(n, parts[n])

print(f'names: {len(dn)} -> {len(kept)}  (used-by-formula {len(used)})')
print(f'external links: {len(order)} -> {len(new_refs)}')
print('dropped parts', len(drop_set))

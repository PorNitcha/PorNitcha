# Shape names, picture positions and text of chosen slides in a pptx (zip read, no COM)
import zipfile, re, sys
z = zipfile.ZipFile(sys.argv[1])
for n in sys.argv[2:]:
    x = z.read('ppt/slides/slide%s.xml' % n).decode('utf8')
    names = re.findall(r'<p:cNvPr id="\d+" name="([^"]+)"', x)
    print('slide', n, 'shapes', len(names), '| first 14:', names[:14])
    for m in re.finditer(r'<p:pic>.*?<a:off x="(\d+)" y="(\d+)"/><a:ext cx="(\d+)" cy="(\d+)"/>', x, re.S):
        print('  pic at (pt)', [round(int(v) / 12700, 1) for v in m.groups()])
    txt = [t for t in re.findall(r'<a:t>([^<]*)</a:t>', x) if t.strip()]
    print('  text:', ' | '.join(txt)[:600])

# Slide order of a pptx with title, shape count and flags (which slides carry a 'Cost of sales (total)' row / a waterfall)
import zipfile, re, sys
z = zipfile.ZipFile(sys.argv[1])
pres = z.read('ppt/presentation.xml').decode('utf8'); rels = z.read('ppt/_rels/presentation.xml.rels').decode('utf8')
rm = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="(slides/slide\d+\.xml)"', rels))
rm.update({k: v for v, k in re.findall(r'Target="(slides/slide\d+\.xml)"[^>]*Id="(rId\d+)"', rels)})
order = [rm[r] for r in re.findall(r'<p:sldId [^>]*r:id="(rId\d+)"', pres)]
print('slides', len(order))
for i, t in enumerate(order, 1):
    x = z.read('ppt/' + t).decode('utf8'); txt = [a for a in re.findall(r'<a:t>([^<]*)</a:t>', x) if a.strip()]
    title = next((a for a in txt if len(a) > 25), '')[:90]
    flags = ('COS ' if 'Cost of sales (total)' in txt else '    ') + ('WF ' if 'Waterfall_TH' in ' '.join(txt) else '   ')
    print('%2d %s %4d %s' % (i, flags, len(txt), title))

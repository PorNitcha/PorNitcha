# Per-slide content diff of two shape dumps (ignores shape names and z-order index)
import sys, collections
def load(p):
    d = collections.defaultdict(collections.Counter)
    for ln in open(p, encoding='utf-8-sig'):
        f = ln.rstrip('\n').split('\t')
        if len(f) < 14: continue
        key = '\t'.join([f[2]] + f[4:])        # type + geometry + font + size + bold + colour + fill + text
        d[int(f[0])][key] += 1
    return d
a, b = load(sys.argv[1]), load(sys.argv[2])     # a = Por's file, b = my rebuild
for s in sorted(set(a) | set(b)):
    only_a = a[s] - b[s]; only_b = b[s] - a[s]
    if not only_a and not only_b: print(f'slide {s}: identical'); continue
    print(f'slide {s}: {sum(only_a.values())} shapes only in Por file, {sum(only_b.values())} only in my build')
    for k in list(only_a)[:12]: print('   POR +', k[:160])
    for k in list(only_b)[:12]: print('   MINE+', k[:160])

import os
b=os.path.expanduser('~/mnt/lovely/')
bad='66ราว 76&ndash;92%ndash;92%'; good='ราว 66&ndash;92%'
for f,n in [('Daily root dashboard - 16 November 2026.html',2),('memory/_gen_1117r3.py',2),('memory/_mk_1117r3.py',2)]:
    s=open(b+f,encoding='utf-8').read(); print(f,s.count(bad)); assert s.count(bad)==n
    open(b+f,'w',encoding='utf-8').write(s.replace(bad,good))

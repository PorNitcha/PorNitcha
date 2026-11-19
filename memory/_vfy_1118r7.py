import re,csv,json,subprocess,os,sys
base=os.path.expanduser('~/mnt/lovely/'); s=open(base+'Daily root dashboard - 17 November 2026.html',encoding='utf-8').read()
scr=[m.group(2) for m in re.finditer(r'<script([^>]*)>(.*?)</script>',s,re.S) if 'application/json' not in m.group(1) and m.group(2).strip()]
for i,c in enumerate(scr):
    open('/sessions/rcw-016htjkjzudtjnr1jwadafz7/vf/b%d.js'%i,'w').write(c); r=subprocess.run(['node','--check','/sessions/rcw-016htjkjzudtjnr1jwadafz7/vf/b%d.js'%i],capture_output=True,text=True); print('block',i,len(c),'OK' if r.returncode==0 else r.stderr[:300])
k=s.find('const dates'); e=s.find('};\n\nObject.values(plants)')
js=s[k:e]+'};\nconsole.log(JSON.stringify({dates,plants}));'
open('/sessions/rcw-016htjkjzudtjnr1jwadafz7/vf/x.js','w').write(js); d=json.loads(subprocess.run(['node','/sessions/rcw-016htjkjzudtjnr1jwadafz7/vf/x.js'],capture_output=True,text=True).stdout)
rows=list(csv.DictReader(open(base+'memory/root-price-history.csv'))); assert len(rows)==180
ds=sorted({r['date'] for r in rows}); key={(r['date'],r['plant']):r for r in rows}
f=lambda x: None if x=='' else float(x); mm=0;n=0
for p in ['TN','TKT','PM','MS','TDC','TWIC']:
    for a,c in [('price','price_thb_kg'),('volume','volume_tons'),('starch','starch_pct'),('cag','cag_thb_kg'),('recov','recovery_pct')]:
        arr=d['plants'][p][a]; assert len(arr)==30
        for j,dt in enumerate(ds):
            n+=1
            if arr[j]!=f(key[(dt,p)][c]): mm+=1; print('MM',p,a,dt,arr[j],key[(dt,p)][c])
print('points',n,'mismatch',mm,'dates',d['dates'][0],d['dates'][-1],len(d['dates']))
for bad in ['92.0% = placeholder','ยังไม่เข้าทุกโรง','รอผลโม่ทุกโรง','ndash;92%ndash','09:2x น. (T-1']: print(repr(bad),s.count(bad))
i=s.find('<span class="plant-code">MS</span>'); print(re.sub(r'\s+',' ',s[i:i+1100]))

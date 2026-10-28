import csv,re,json,subprocess,datetime
SRC="Daily root dashboard - 4 October 2026.html"; DST="Daily root dashboard - 6 October 2026.html"
DST="Daily root dashboard - 5 October 2026.html"
rows=list(csv.DictReader(open('memory/root-price-history.csv')))
dates=sorted({r['date'] for r in rows}); assert len(dates)==30
def lab(d):
    dt=datetime.date.fromisoformat(d); return f"{dt.day}-{dt.strftime('%b')}"
D={}
for r in rows: D[(r['date'],r['plant'])]=r
def f(x): return None if x=='' else float(x)
def i_(x): return None if x=='' else int(x)
order=['TN','TKT','PM','MS','TDC','TWIC']
S={p:{k:[] for k in ('price','volume','starch','cag','recov')} for p in order}
for p in order:
    for d in dates:
        r=D[(d,p)]
        S[p]['price'].append(f(r['price_thb_kg'])); S[p]['volume'].append(i_(r['volume_tons']))
        S[p]['starch'].append(f(r['starch_pct'])); S[p]['cag'].append(f(r['cag_thb_kg'])); S[p]['recov'].append(f(r['recovery_pct']))
def js(a): return '['+', '.join('null' if v is None else (repr(v) if not isinstance(v,float) else (repr(round(v,4)))) for v in a)+']'
h=open(SRC,encoding='utf-8').read()
lines=h.split('\n')
# --- plants arrays
for p in order:
    for k,name in (('price','price: '),('volume','volume:'),('starch','starch:'),('cag','cag:   '),('recov','recov: ')):
        pass
txt=h
m=re.search(r'const dates = \[.*?\];',txt); txt=txt.replace(m.group(0),'const dates = '+json.dumps([lab(d) for d in dates])+';')
for p in order:
    start=txt.index(f'  {p}: {{ label')
    end=txt.index('\n  },',start)
    blk=txt[start:end]
    for k in ('price','volume','starch','cag','recov'):
        blk=re.sub(rf'(\n    {k}:\s*)\[[^\]]*\]',lambda mm:mm.group(1)+js(S[p][k]),blk,count=1)
    txt=txt[:start]+blk+txt[end:]
# --- metrics
L=dates[-1]; P=dates[-2]
th=['TN','TKT','PM','MS','TDC']
def day(d): 
    return {p:(D[(d,p)]) for p in th if D[(d,p)]['volume_tons'] not in ('',) and int(D[(d,p)]['volume_tons'] or 0)>0 and D[(d,p)]['price_thb_kg']!=''}
def wavg(d,key):
    dd=day(d); tv=sum(int(r['volume_tons']) for r in dd.values())
    return tv, sum(int(r['volume_tons'])*float(r[key]) for r in dd.values())/tv, list(dd)
tvL,prL,plL=wavg(L,'price_thb_kg'); _,stL,_=wavg(L,'starch_pct')
tvP,prP,plP=wavg(P,'price_thb_kg'); _,stP,_=wavg(P,'starch_pct')
# like for like
common=[p for p in plL if p in plP]
lfP=sum(int(D[(P,p)]['volume_tons']) for p in common)
print('L',L,tvL,prL,stL,plL,'P',tvP,prP,stP,plP,'lfP',lfP)
# last complete CAG
last=None
for d in reversed(dates):
    dd=day(d); need=[p for p in dd if p!='MS']
    if need and all(dd[p]['cag_thb_kg']!='' for p in need):
        tv=sum(int(dd[p]['volume_tons']) for p in need); cg=sum(int(dd[p]['volume_tons'])*float(dd[p]['cag_thb_kg']) for p in need)/tv
        last=(d,cg,len(need),tv); break
print('lastCAG',last)
pending={}
for p in th:
    pending[p]=[lab(d) for d in dates if D[(d,p)]['volume_tons'] and int(D[(d,p)]['volume_tons'])>0 and D[(d,p)]['recovery_pct']=='' ]
print(pending)
# CBG check
for p in th:
    r=D[(L,p)]
    if r['price_thb_kg']: print(p,round(float(r['price_thb_kg'])/float(r['starch_pct'])*100,2))
json.dump(dict(tvL=tvL,prL=prL,stL=stL,tvP=tvP,prP=prP,stP=stP,lfP=lfP,last=last,pending=pending),open('memory/_m_0610.json','w'),ensure_ascii=False)
open('memory/_stage1_0610.html','w',encoding='utf-8').write(txt)

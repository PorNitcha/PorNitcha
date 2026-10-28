import csv, collections, re, json
def f(x):
    try: return float(x)
    except: return 0.0
def norm(n):
    n=n.upper().replace('BJ.','').replace('ฟู๊ด','ฟู้ด'); n=re.sub(r'[^A-Z0-9ก-๙]+','',n); return n[:16]
ALIAS={'HUIFALINXIAFOODS':'HUIFA','QINGDAOMIRACLESU':'HUIFA','QINGDAOMIRACLE':'HUIFA','MORIIFOODSINC':'MORIIFOODS','FOODTRENDANDSUPE':'FOODTREND'}
key=lambda n: ALIAS.get(norm(n),norm(n))
MAP={'HP-XL':'PO-XL','XL':'XL','HP':'PO','AC':'AC','AC-XL':'AC','AC | AC-XL':'AC','HP | HP-XL':'PO-XL','MX':'MX','AA-XL':'XL'}
rows=list(csv.DictReader(open('data_actual.csv',encoding='utf-8')))
data=[r for r in rows if r['Reaction group'] not in ('','None','#N/A') and r['Year'] in ('Year 2025','Year 2026')]
L=collections.defaultdict(lambda:{'name':'','t25':0,'g25':0,'t26':0,'g26':0,'t27':0,'t27ry':0,'t27tk':0,'country':''})
for r in data:
    k=(key(r['Customer name (Group)']),r['Reaction group']); c=L[k]; c['name']=c['name'] or r['Customer name (Group)']; c['country']=c['country'] or r['Country']
    y='25' if r['Year']=='Year 2025' else '26'
    c['t'+y]+=f(r['Sales Quantity (Tons)']); c['g'+y]+=f(r['Actual Gross Profit (THB)'])+f(r['Idle Cost'])+f(r['PPA'])+f(r['Other Adj'])
ap=list(csv.DictReader(open('ap27_by_customer.csv',encoding='utf-8')))
for r in ap:
    g=MAP.get(r['rx'],'Others'); k=(key(r['name']),g); c=L[k]; c['name']=c['name'] or r['name']; c['country']=c['country'] or r['country']
    c['t27']+=f(r['ry27'])+f(r['tkt27'])+f(r['ry_hr27'])+f(r['tkt_hr27']); c['t27ry']+=f(r['ry27'])+f(r['ry_hr27']); c['t27tk']+=f(r['tkt27'])+f(r['tkt_hr27'])
TIERS={'XL':[0,2000,3200,4500],'PO-XL':[2000,4000,6000,7500],'PO':[2000,4000,5500,7000],'AC':[4000,7000,9500,12000],'MX':[2000,4000,6000,9000],'Others':[2000,4000,6000,9000]}
def tier(rx,g):
    b=TIERS[rx]; 
    if g is None: return 'new'
    for i,x in enumerate(b):
        if g<x: return f'T{i+1}'
    return f'T{len(b)+1}'
def tname(rx):
    b=TIERS[rx]; n=[f'<{b[0]/1000:g}']+[f'{b[i]/1000:g}-{b[i+1]/1000:g}' for i in range(len(b)-1)]+[f'>{b[-1]/1000:g}']
    return n
out={}
print('Volume share by product-GP tier (THB/kg) within reaction. Columns: 2025 FY | 2026 YTD | 2027 plan at 2025 margins | 2027 plan at 2026 margins')
for rx in ['PO-XL','XL','PO','AC','MX','Others']:
    lines=[(k,v) for k,v in L.items() if k[1]==rx]
    names=tname(rx)
    agg={n:[0,0,0,0,0,0,0,0] for n in ['T1','T2','T3','T4','T5','new']}
    for k,v in lines:
        g25=v['g25']/v['t25'] if v['t25'] else None; g26=v['g26']/v['t26'] if v['t26'] else None
        if v['t25']: a=agg[tier(rx,g25)]; a[0]+=v['t25']; a[1]+=v['g25']
        if v['t26']: a=agg[tier(rx,g26)]; a[2]+=v['t26']; a[3]+=v['g26']
        if v['t27']:
            a=agg[tier(rx,g25)]; a[4]+=v['t27']; a[5]+=v['t27']*(g25 or 0)
            a=agg[tier(rx,g26)]; a[6]+=v['t27']; a[7]+=v['t27']*(g26 or 0)
    T=[sum(a[i] for a in agg.values()) for i in (0,2,4,6)]
    print(f"\n## {rx}  2025 {T[0]:,.0f} t | 2026 YTD {T[1]:,.0f} t | 2027 plan {T[2]:,.0f} t")
    print(f"{'tier':10s} {'2025 t':>8s} {'%':>4s} {'GP/kg':>6s} | {'2026 t':>8s} {'%':>4s} {'GP/kg':>6s} | {'27@25 t':>8s} {'%':>4s} {'GP/kg':>6s} | {'27@26 t':>8s} {'%':>4s}")
    for i,tn in enumerate(['T1','T2','T3','T4','T5','new']):
        a=agg[tn]; lab=(names[i] if i<5 else 'no hist')
        def c(t,g,tot): return f"{t:8.0f} {t/tot*100 if tot else 0:4.0f} {g/t/1000 if t else 0:6.2f}"
        print(f"{tn+' '+lab:10s} {c(a[0],a[1],T[0])} | {c(a[2],a[3],T[1])} | {c(a[4],a[5],T[2])} | {a[6]:8.0f} {a[6]/T[3]*100 if T[3] else 0:4.0f}")
    w25=sum(a[1] for a in agg.values())/T[0] if T[0] else 0; w26=sum(a[3] for a in agg.values())/T[1] if T[1] else 0
    h=[a for n,a in agg.items() if n!='new']; w27=sum(a[5] for a in h)/sum(a[4] for a in h) if sum(a[4] for a in h) else 0; w27b=sum(a[7] for a in h)/sum(a[6] for a in h) if sum(a[6] for a in h) else 0
    print(f"weighted product GP/kg: 2025 {w25/1000:.2f} | 2026 {w26/1000:.2f} | 2027 plan (hist lines) at 2025 margins {w27/1000:.2f} | at 2026 margins {w27b/1000:.2f}")
    # members per tier 2025 (top by t27)
    for tn in ['T1','T2','T3','T4','T5']:
        mem=sorted([(v['name'][:22],round(v['t25']),round(v['t27']),round(v['g25']/v['t25']) if v['t25'] else None,round(v['g26']/v['t26']) if v['t26'] else None) for k,v in lines if v['t25'] and tier(rx,v['g25']/v['t25'])==tn], key=lambda x:-x[2])[:6]
        if mem: print(f"   {tn}: "+'; '.join(f"{m[0]} ({m[1]}t→{m[2]}t, {m[3]}→{m[4]})" for m in mem))
    out[rx]={'tiers':names,'agg':agg,'lines':[{'name':v['name'],'country':v['country'],'t25':round(v['t25'],2),'gp25':round(v['g25']/v['t25'],2) if v['t25'] else None,'t26':round(v['t26'],2),'gp26':round(v['g26']/v['t26'],2) if v['t26'] else None,'t27':round(v['t27']),'t27ry':round(v['t27ry']),'t27tk':round(v['t27tk'])} for k,v in lines if v['t25'] or v['t26'] or v['t27']]}
json.dump(out,open('tiers.json','w',encoding='utf-8'),ensure_ascii=False)

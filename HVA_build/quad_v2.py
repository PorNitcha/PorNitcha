import csv, collections, json, re
def f(x):
    try: return float(x)
    except: return 0.0
def norm(n):
    n=n.upper().replace('BJ.','').replace('ฟู๊ด','ฟู้ด'); n=re.sub(r'[^A-Z0-9ก-๙]+','',n); return n[:16]
ALIAS={'HUIFALINXIAFOODS':'HUIFA','QINGDAOMIRACLESU':'HUIFA','QINGDAOMIRACLE':'HUIFA','MORIIFOODSINC':'MORIIFOODS','FOODTRENDANDSUPE':'FOODTREND'}
key=lambda n: ALIAS.get(norm(n),norm(n))
rows=list(csv.DictReader(open('data_actual.csv',encoding='utf-8')))
data=[r for r in rows if r['Reaction group'] not in ('','None','#N/A')]
C=collections.defaultdict(lambda:{'name':'','country':'','channel':'','t25':0,'ns25':0,'c25':0,'gp25':0,'i25':0,'p25':0,'t26':0,'ns26':0,'c26':0,'gp26':0,'i26':0,'p26':0,'xl25':0,'xl26':0,'t27':0})
for r in data:
    k=key(r['Customer name (Group)']); c=C[k]
    if not c['name'] or r['Year']=='Year 2026': c['name']=r['Customer name (Group)']; c['country']=r['Country']; c['channel']=r['Channel']
    y='25' if r['Year']=='Year 2025' else ('26' if r['Year']=='Year 2026' else None)
    if not y: continue
    t=f(r['Sales Quantity (Tons)'])
    c['t'+y]+=t; c['ns'+y]+=f(r['Net Sales Revenue (THB)']); c['c'+y]+=f(r['Actual Cost (THB)']); c['gp'+y]+=f(r['Actual Gross Profit (THB)']); c['i'+y]+=f(r['Idle Cost']); c['p'+y]+=f(r['PPA'])+f(r['Other Adj'])
    if r['Reaction group']=='XL': c['xl'+y]+=t
ap=list(csv.DictReader(open('ap27_by_customer.csv',encoding='utf-8')))
for r in ap:
    t=f(r['ry27'])+f(r['tkt27'])+f(r['ry_hr27'])+f(r['tkt_hr27'])
    if t<=0: continue
    k=key(r['name']); c=C[k]
    if not c['name']: c['name']=r['name']; c['country']=r['country']; c['channel']=r['channel']
    c['t27']+=t
out=[]
for k,c in C.items():
    if c['t27']<50 and c['t25']<50 and c['t26']<50: continue
    d={'name':c['name'],'country':c['country'],'channel':c['channel'],'t25':round(c['t25'],1),'t26':round(c['t26'],1),'t26a':round(c['t26']*12/9,1),'t27':round(c['t27'])}
    for y in ('25','26'):
        T=c['t'+y]
        if T:
            d['asp'+y]=round(c['ns'+y]/T); d['costf'+y]=round(c['c'+y]/T); d['costp'+y]=round((c['c'+y]-c['i'+y]-c['p'+y])/T)
            d['gpf'+y]=round(c['gp'+y]/T); d['gpx'+y]=round((c['gp'+y]+c['i'+y])/T); d['gpp'+y]=round((c['gp'+y]+c['i'+y]+c['p'+y])/T)
            d['xl'+y]=round(c['xl'+y]/T*100); d['gpm'+y]=round((c['gp'+y]+c['i'+y]+c['p'+y])/1e6,1)
        else:
            for kk in ('asp','costf','costp','gpf','gpx','gpp','xl','gpm'): d[kk+y]=None
    out.append(d)
out.sort(key=lambda d:-d['t27'])
json.dump(out,open('quad2.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print('accounts',len(out))
# stats on product GP, floor 4700
FL=4700
def q(gp,growth):
    if gp is None: return 'new'
    if gp>=FL: return 'grow' if growth>0 else 'protect'
    return 'fix' if growth>0 else 'reprice'
hist=[x for x in out if x['t27']>0]
for base in ('25','26'):
    cnt=collections.Counter(); tons=collections.defaultdict(float)
    for x in hist:
        bt=x['t25'] if base=='25' else x['t26a']; gp=x['gpp'+base] if bt else None
        r=q(gp,x['t27']-bt); cnt[r]+=1; tons[r]+=x['t27']
    print('base',base,{k:(cnt[k],round(tons[k])) for k in ('fix','grow','protect','reprice','new')}, 'total',round(sum(tons.values())))
fix=[x for x in hist if x['t25'] and x['gpp25'] is not None and x['gpp25']<FL and x['t27']-x['t25']>0]
print('FIX 2025 basis:',[(x['name'][:18],x['t27'],x['gpp25'],x['gpp26']) for x in sorted(fix,key=lambda x:-x['t27'])])
print('FIX t27',sum(x['t27'] for x in fix),'GP25',round(sum(x['gpm25'] for x in fix),1),'GP26 9m',round(sum(x['gpm26'] or 0 for x in fix),1))
# at-the-floor band 4000-5500 in 2025 among growing accounts
band=[x for x in hist if x['t25'] and x['gpp25'] is not None and 4000<=x['gpp25']<5500 and x['t27']>=300]
print('2025 product GP 4,000-5,500 (>=300t27):',[(x['name'][:18],x['t27'],x['gpp25'],x['gpp26']) for x in sorted(band,key=lambda x:-x['t27'])])
w=collections.defaultdict(float)
for x in hist:
    if x['t26'] and x['t25'] and x['gpp26'] is not None:
        W=x['t26']; w['w']+=W; w['dasp']+=W*(x['asp26']-x['asp25']); w['dcost']+=W*(x['costp26']-x['costp25']); w['dgp']+=W*(x['gpp26']-x['gpp25'])
print('weighted ΔASP',round(w['dasp']/w['w']),'Δproduct cost',round(w['dcost']/w['w']),'ΔGP/t product',round(w['dgp']/w['w']))
print('grow accounts losing >1,500 product GP/t (>=200t27):',[(x['name'][:16],x['gpp25'],x['gpp26']) for x in sorted(hist,key=lambda x:-x['t27']) if x['t27']>=200 and x['gpp25'] and x['gpp26'] and x['gpp25']>=FL and x['gpp25']-x['gpp26']>1500][:10])
grow=[x for x in hist if x['t26'] and x['gpp26'] and x['gpp26']>=FL and x['t27']-x['t26a']>0]
g=sum(x['t27']-x['t26a'] for x in grow); rec=sum(min(x['t27']-x['t26a'],max(0,x['t25']-x['t26a'])) for x in grow); print('grow growth',round(g),'recovery',round(rec),f'{rec/g*100:.0f}%',len(grow))
lost=[x for x in out if x['t25']>=100 and x['t27']==0]; print('lost',len(lost),round(sum(x['t25'] for x in lost)),'avg product GP/t',round(sum(x['gpm25'] for x in lost)*1e6/sum(x['t25'] for x in lost)))
new=[x for x in out if x['t25']==0 and x['t27']>0]; print('new',len(new),round(sum(x['t27'] for x in new)))
tw=[x for x in out if 'THAI WAH INDONESIA' in x['name'].upper()][0]; print('TWI',tw['gpp25'],tw['gpp26'],tw['asp26']-tw['asp25'],tw['costp26']-tw['costp25'],tw['t27'])

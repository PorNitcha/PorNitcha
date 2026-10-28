import csv, io, base64, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

M='/sessions/focused-optimistic-keller/mnt/lovely/memory/'
rows=list(csv.DictReader(open(M+'root-price-history.csv')))
dates=sorted(set(r['date'] for r in rows)); lbl=[d[5:] for d in dates]
def f(v):
    try: return float(v)
    except: return None
S={}
for p in ['TN','TKT','PM','MS','TDC','TWIC']:
    m={r['date']:r for r in rows if r['plant']==p}
    d={k:[] for k in ['price','vol','starch','cag','rec','stton']}
    for dt in dates:
        r=m.get(dt,{})
        pr,vo,st=f(r.get('price_thb_kg')),f(r.get('volume_tons')),f(r.get('starch_pct'))
        cg,rc=f(r.get('cag_thb_kg')),f(r.get('recovery_pct'))
        d['price'].append(pr); d['vol'].append(vo); d['starch'].append(st)
        d['cag'].append(cg); d['rec'].append(rc)
        d['stton'].append(round(vo*st/100*rc/100,1) if (vo and st and rc) else None)
    S[p]=d
ext=[]
for r in csv.DictReader(open(M+'root-price-external.csv')):
    if r['date'] in dates: ext.append((dates.index(r['date']), float(r['price_thb_kg'])))

NAMES={'TN':'TN  ·  Udon Thani','TKT':'TKT  ·  Kalasin','PM':'PM  ·  Nakhon Ratchasima',
       'MS':'MS  ·  Tak','TDC':'TDC  ·  Rayong','TWIC':'TWIC  ·  Oddar Meanchey, Cambodia'}
SUB={'TN':'','TKT':'','PM':'red stars = Nettathai reference price (Phimai)',
     'MS':'no purchases in this 30-day window','TDC':'',
     'TWIC':'separate legal entity — excluded from Thailand total'}
NAVY='#0b2540'; ORANGE='#e0821f'; GREEN='#1a9850'; PURPLE='#8e44ad'; TEAL='#0e8aa8'; BAR='#d6d9de'
X=list(range(len(dates)))
def seg(v):
    runs=[];cur=[]
    for i,x in enumerate(v):
        if x is None:
            if cur: runs.append(cur); cur=[]
        else: cur.append((i,x))
    if cur: runs.append(cur)
    return runs
def plot(ax,vals,col,style,lw,ms):
    for r in seg(vals):
        xs=[a for a,_ in r]; ys=[b for _,b in r]
        if len(xs)==1: ax.plot(xs,ys,'o',color=col,ms=ms)
        else: ax.plot(xs,ys,style,color=col,lw=lw)
def lim(ax,vals,padf=0.18,minpad=0.3,floor0=False):
    v=[x for x in vals if x is not None]
    if not v: ax.set_ylim(0,1); return
    lo,hi=min(v),max(v); pad=max(minpad,(hi-lo)*padf)
    ax.set_ylim(0 if floor0 else lo-pad, hi+pad)

def draw(code):
    d=S[code]
    fig,axP=plt.subplots(figsize=(9.4,3.9),dpi=110)
    fig.subplots_adjust(left=0.16,right=0.795,top=0.80,bottom=0.16)
    axPct=axP.twinx(); axPct.spines['left'].set_position(('axes',-0.115))
    axPct.yaxis.set_label_position('left'); axPct.yaxis.tick_left()
    axPct.spines['right'].set_visible(False)
    axV=axP.twinx()
    axC=axP.twinx(); axC.spines['right'].set_position(('axes',1.10))

    vb=[v if v is not None else 0 for v in d['vol']]
    axV.bar(X,vb,width=0.62,color=BAR,zorder=1)
    plot(axV,d['stton'],GREEN,'--',1.6,3.5)
    plot(axPct,d['starch'],ORANGE,'--',1.6,3.5)
    rx=[i for i,v in enumerate(d['rec']) if v is not None]
    axPct.plot(rx,[d['rec'][i] for i in rx],'o',color=TEAL,ms=3.2)
    plot(axC,d['cag'],PURPLE,'-',1.7,3.5)
    plot(axP,d['price'],NAVY,'-',2.3,4.2)
    if code=='PM':
        for i,v in ext: axP.plot([i],[v],'*',color='#d73027',ms=11)

    pr=list(d['price'])+([v for _,v in ext] if code=='PM' else [])
    lim(axP,pr,0.22,0.12)
    lim(axC,d['cag'],0.15,0.5)
    lim(axPct,d['starch']+d['rec'],0.22,2.0)
    tons=[v for v in d['vol']+d['stton'] if v is not None]
    axV.set_ylim(0,max(1,max(tons) if tons else 1)*1.35)

    axP.set_xlim(-0.8,len(dates)-0.2)
    tk=[i for i in X if i%3==0 or i==len(X)-1]
    axP.set_xticks(tk); axP.set_xticklabels([lbl[i] for i in tk],fontsize=7.5,color='#6b7280')
    axP.set_ylabel('Price  THB/kg',fontsize=8,color=NAVY,labelpad=2)
    axPct.set_ylabel('%Starch / %Recovery',fontsize=7.5,color=ORANGE,labelpad=2)
    axV.set_ylabel('tons',fontsize=8,color='#8b9199',labelpad=2)
    axC.set_ylabel('CAG  THB/kg',fontsize=8,color=PURPLE,labelpad=2)
    axP.tick_params(axis='y',labelsize=7.5,colors=NAVY)
    axPct.tick_params(axis='y',labelsize=7,colors=ORANGE)
    axV.tick_params(axis='y',labelsize=7.5,colors='#8b9199')
    axC.tick_params(axis='y',labelsize=7.5,colors=PURPLE)
    axP.grid(axis='y',color='#eceef1',lw=0.8); axP.set_axisbelow(True)
    for a in (axP,axPct,axV,axC): a.spines['top'].set_visible(False)
    axP.spines['left'].set_color(NAVY); axPct.spines['left'].set_color(ORANGE)
    axV.spines['right'].set_color('#c7cbd1'); axC.spines['right'].set_color(PURPLE)
    axP.spines['bottom'].set_color('#c7cbd1')
    axP.set_title(NAMES[code],loc='left',fontsize=11.5,fontweight='bold',color=NAVY,pad=22)
    if SUB[code]: axP.text(0,1.035,SUB[code],transform=axP.transAxes,fontsize=7.8,color='#9ca3af')
    buf=io.BytesIO(); fig.savefig(buf,format='png'); plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()

out={c:draw(c) for c in ['TN','TKT','PM','MS','TDC','TWIC']}
json.dump(out,open('charts_b64.json','w'))
for k,v in out.items(): open('chart_%s.png'%k,'wb').write(base64.b64decode(v))
print('ok',{k:len(v)//1000 for k,v in out.items()})

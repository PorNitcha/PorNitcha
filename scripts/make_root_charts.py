#!/usr/bin/env python3
"""รูปกราฟ 5 โรงงานสำหรับอีเมล Daily root dashboard — visualisation เดียวกับ HTML dashboard
1 โรงงาน = 1 กราฟ, แกนซ้าย 3 (ราคา / %Starch / %Recovery) แกนขวา 2 (ตัน / CAG)
ใช้ memory/root-price-history.csv -> outputs/mail/chart_<PLANT>.png
sandbox ไม่มีฟอนต์ไทย จึงใช้ label อังกฤษ (ตรงกับชื่อคอลัมน์ไฟล์ต้นทาง)"""
import csv, collections, datetime, sys, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

SRC = sys.argv[1] if len(sys.argv)>1 else 'memory/root-price-history.csv'
OUT = sys.argv[2] if len(sys.argv)>2 else 'outputs/mail'
os.makedirs(OUT, exist_ok=True)
rows=list(csv.DictReader(open(SRC)))
dates=sorted({r['date'] for r in rows})
labels=[datetime.date.fromisoformat(d).strftime('%d-%b') for d in dates]
D=collections.defaultdict(dict)
for r in rows: D[r['plant']][r['date']]=r
def col(pl,f):
    o=[]
    for d in dates:
        v=D[pl].get(d,{}).get(f,'')
        o.append(float(v) if v not in ('',None) else None)
    return o
FULL={'TN':'TN  —  Mueang Udon Thani','TKT':'TKT  —  Tha Khantho, Kalasin',
      'PM':'PM  —  Phimai, Nakhon Ratchasima','TDC':'TDC  —  Ban Chang, Rayong','MS':'MS  —  Mae Sot, Tak',
      'TWIC':'TWIC  —  Oddar Meanchey, Cambodia'}
NAVY='#0b2540'; ORANGE='#e0821f'; GREEN='#1a9850'; PURPLE='#8e44ad'; TEAL='#0e8aa8'
GREY_F='#d6d9de'; GREY_E='#c7cbd1'


def _iso(vals):
    """index/value ของค่าที่โดดเดี่ยว (เพื่อนบ้านเป็น None) — เส้นวาดไม่ได้ ต้องโชว์เป็นจุด"""
    xs=[]; ys=[]
    for i,v in enumerate(vals):
        if v is None: continue
        prev = vals[i-1] if i>0 else None
        nxt  = vals[i+1] if i<len(vals)-1 else None
        if prev is None and nxt is None: xs.append(i); ys.append(v)
    return xs,ys

for pl in ['TN','TKT','PM','TDC','MS','TWIC']:
    price=col(pl,'price_thb_kg'); vol=col(pl,'volume_tons')
    st=col(pl,'starch_pct'); cag=col(pl,'cag_thb_kg'); rec=col(pl,'recovery_pct')
    stn=[None if (v is None or not v or s is None) else round(v*s/100,1) for v,s in zip(vol,st)]
    x=list(range(len(dates)))

    fig,axP=plt.subplots(figsize=(12.4,6.1))
    fig.patch.set_facecolor('white')
    fig.subplots_adjust(left=0.175, right=0.855, top=0.88, bottom=0.20)

    axS=axP.twinx(); axR=axP.twinx(); axV=axP.twinx(); axC=axP.twinx()
    # extra LEFT axes
    for a,off in ((axS,52),(axR,104)):
        a.yaxis.set_label_position('left'); a.yaxis.tick_left()
        a.spines['left'].set_position(('outward',off)); a.spines['right'].set_visible(False)
    # extra RIGHT axis
    axC.spines['right'].set_position(('outward',52))

    # bars behind everything
    axV.set_zorder(0); axV.bar(x,[0 if v is None else v for v in vol],color=GREY_F,
                               edgecolor=GREY_E,width=.72,label='Root purchased (t)')
    axV.plot(x,stn,color=GREEN,lw=1.5,ls='--',label='Starch output (t)')
    axV.plot(*_iso(stn),color=GREEN,ls='none',marker='o',ms=3.4)
    for a in (axP,axS,axR,axC): a.set_zorder(3); a.patch.set_visible(False)

    axP.plot(x,price,color=NAVY,lw=2.3,label='Root price (THB/kg)')
    axP.plot(*_iso(price),color=NAVY,ls='none',marker='o',ms=3.8)
    axS.plot(x,st,color=ORANGE,lw=1.7,ls='--',label='%Starch')
    axS.plot(*_iso(st),color=ORANGE,ls='none',marker='o',ms=3.4)
    axR.plot(x,rec,color=TEAL,ls='none',marker='o',ms=4.0,label='%Recovery')
    axC.plot(x,cag,color=PURPLE,lw=2.1,label='CAG cost after grind (THB/kg)')
    axC.plot(*_iso(cag),color=PURPLE,ls='none',marker='o',ms=4.2)

    pv=[p for p in price if p]
    if pv:
        lo,hi=min(pv),max(pv); pad=max((hi-lo)*0.45,0.06); axP.set_ylim(lo-pad,hi+pad)
    axP.set_ylabel('Root price  THB/kg',fontsize=9,color=NAVY)
    axS.set_ylabel('%Starch',fontsize=9,color=ORANGE)
    axR.set_ylabel('%Recovery',fontsize=9,color=TEAL)
    axV.set_ylabel('Tonnes',fontsize=9,color='#6b7280')
    axC.set_ylabel('CAG  THB/kg',fontsize=9,color=PURPLE)
    for a,c_ in ((axP,NAVY),(axS,ORANGE),(axR,TEAL),(axV,'#6b7280'),(axC,PURPLE)):
        a.tick_params(labelsize=8,colors=c_)
    axV.set_ylim(bottom=0)
    axP.grid(axis='y',color='#eceef1',zorder=1)
    axP.set_title(FULL[pl],fontsize=13.5,fontweight='bold',color=NAVY,loc='left',pad=10)
    axP.set_xticks(x[::3]); axP.set_xticklabels([labels[i] for i in x[::3]],fontsize=8,color='#555')
    axP.set_xlim(-0.8,len(dates)-0.2)

    hs=[];ls_=[]
    for a in (axV,axP,axS,axR,axC):
        hh,ll=a.get_legend_handles_labels(); hs+=hh; ls_+=ll
    axP.legend(hs,ls_,fontsize=8,ncol=3,loc='upper center',
               bbox_to_anchor=(0.5,-0.13),frameon=False)
    if all(v in (0,None) for v in vol):
        axP.text(.5,.5,'No root purchased in the last 30 days',transform=axP.transAxes,
                 ha='center',fontsize=12,color='#9ca3af',style='italic')
    for a in (axP,axS,axR,axV,axC):
        for s_ in a.spines.values(): s_.set_color('#d5d8dd')
    fig.savefig(f'{OUT}/chart_{pl}.png',dpi=110,facecolor='white'); plt.close(fig)
print(f'charts -> {OUT} | window {labels[0]} -> {labels[-1]}')

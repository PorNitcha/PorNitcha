import openpyxl, csv
p=r"C:/Users/NitchaSuwongtham/THAIWAH/Commercial Finance - General/AP 2027/TDC/Top Line HVA Thailand_Oct1 Revised ASP_Final.xlsx"
wb=openpyxl.load_workbook(p, read_only=True, data_only=True)
out=[]
for name,plant in [('TDC by Customer','RY'),('TDC 2.0 by Customer','TKT')]:
    ws=wb[name]; rows=list(ws.iter_rows(values_only=True))
    hdr=rows[4]; assert 'Jan-27' in str(hdr[9]) and 'Dec-27' in str(hdr[31]), (hdr[9],hdr[31])
    for r in rows[5:]:
        if r[2] is None: continue
        q=[0.0]*4
        for m in range(12):
            for j in (9+2*m, 10+2*m):
                v=r[j]
                if isinstance(v,(int,float)): q[m//3]+=v
        if sum(q)<=0: continue
        out.append([str(r[2]),str(r[6]),plant]+[round(x,3) for x in q])
with open('ap27_quarterly.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['name','rx','plant','q1','q2','q3','q4']); w.writerows(out)
for pl in ('RY','TKT'):
    qs=[sum(float(o[3+i]) for o in out if o[2]==pl) for i in range(4)]
    print(pl,[round(x) for x in qs],'FY',round(sum(qs)))

import openpyxl, csv, sys
p=r"C:/Users/NitchaSuwongtham/THAIWAH/Commercial Finance - General/2026/02_HVA/Profitability/K Cherry/Sent/TDC Profitability_Act 2024-2026_Jul2026_AddPPA.xlsx"
wb=openpyxl.load_workbook(p, read_only=True, data_only=True)
ws=wb['data_Actual']
rows=ws.iter_rows(values_only=True)
hdr=next(rows)
for i,h in enumerate(hdr): print(i, repr(h))
# save to csv for reuse
with open('data_actual.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(hdr)
    n=0
    for r in rows:
        if r[0] is None and r[46] is None: continue
        w.writerow(r); n+=1
print('rows',n)

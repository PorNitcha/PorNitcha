const fs=require('fs'),vm=require('vm');
const h=fs.readFileSync('Daily root dashboard - 15 November 2026.html','utf8');
const re=/<script(?![^>]*src)([^>]*)>([\s\S]*?)<\/script>/g;let m,n=0,ok=0;
while((m=re.exec(h))){n++; if(/json/.test(m[1])){continue} try{new vm.Script(m[2]);ok++}catch(e){console.log('SYNTAX FAIL block',n,e.message)}}
console.log('script blocks',n,'syntax ok',ok);
const k=h.indexOf('const dates'),e=h.indexOf('};\n\nObject.values(plants)');
const ctx={};vm.runInNewContext(h.slice(k,e+2).replace('const dates','var dates').replace('const plants','var plants'),ctx);
const rows=fs.readFileSync('memory/root-price-history.csv','utf8').trim().split('\n').slice(1).map(l=>l.split(','));
const ds=[...new Set(rows.map(r=>r[0]))];const M={Sep:'09',Oct:'10',Nov:'11'};
let mis=0,pts=0;
if(ds.length!==30||ctx.dates.length!==30)console.log('date count',ds.length,ctx.dates.length);
ctx.dates.forEach((lb,i)=>{const [d,mo]=lb.split('-');const iso='2026-'+M[mo]+'-'+String(d).padStart(2,'0');if(iso!==ds[i]){mis++;console.log('date mismatch',lb,ds[i])}});
for(const r of rows){const i=ds.indexOf(r[0]);const p=ctx.plants[r[1]];const f=[['price',2],['volume',3],['starch',4],['cag',5],['recov',6]];
 for(const [a,c] of f){pts++;const v=r[c]===''?null:parseFloat(r[c]);if(p[a][i]!==v){mis++;console.log('MIS',r[0],r[1],a,p[a][i],v)}}}
console.log('rows',rows.length,'points',pts,'mismatch',mis);

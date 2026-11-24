const { chromium } = require('playwright');
// wood designs: node shotw.js <out_dir> <views comma list> [prefix]   e.g. front,back,open,edge,pinch,mark
(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});const p=await b.newPage({viewport:{width:1000,height:1300}});
const pre=process.argv[4]||''; const src={front:'closed',back:'closed',edge:'closed',mark:'closed',open:'open',pinch:'open',inside:'open'};
for (const v of process.argv[3].split(',')){
 await p.goto(`http://127.0.0.1:${process.env.PORT||8770}/view.html?f=v7_${src[v]}&v=${v}`); await p.waitForFunction(()=>document.title==='done',null,{timeout:120000});
 await p.screenshot({path:`${process.argv[2]}/${pre}v7_${v}.png`});}
await b.close();})();

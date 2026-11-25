const { chromium } = require('playwright');
// v9 concept shots: front / back / open as before, plus 'edge' (crescent thumb scoop) and 'pinch' (channel tops). Usage: node shot9.js <out_dir>
(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});const p=await b.newPage({viewport:{width:1000,height:1300}});
for (const [s,v] of [['closed','front'],['open','open'],['closed','back'],['closed','edge'],['open','pinch']]){
 await p.goto(`http://127.0.0.1:${process.env.PORT||8770}/view.html?f=v7_${s}&v=${v}`); await p.waitForFunction(()=>document.title==='done',null,{timeout:120000});
 await p.screenshot({path:`${process.argv[2]}/v7_${v}.png`});}
await b.close();})();

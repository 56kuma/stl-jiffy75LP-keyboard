const {chromium}=require('playwright');
const OUT=process.argv[2]||'../images';
const shots=[
 ['hero.png',{cam:{p:[-330,-520,330],t:[0,0,10]}}],
 ['with_keyboard.png',{cam:{p:[-420,-620,330],t:[0,0,60]},kb:1}],
 ['side.png',{cam:{p:[900,0,70],t:[0,0,60]},kb:1,fov:16}],
 ['top.png',{cam:{p:[0,-1,800],t:[0,0,0]},fov:20}],
 ['space_gray.png',{cam:{p:[-330,-520,330],t:[0,0,10]},col:'#5b5d62',kb:0}],
];
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1600,height:1000}});
for(const [f,o] of shots){const u=new URLSearchParams({cam:JSON.stringify(o.cam),...(o.kb?{kb:1}:{}),...(o.fov?{fov:o.fov}:{}),...(o.col?{col:o.col}:{})});
 await p.goto('http://127.0.0.1:8765/view.html?'+u); await p.waitForFunction('window.done',null,{timeout:120000});
 await p.screenshot({path:OUT+'/'+f}); console.log(f);}
await b.close();})();

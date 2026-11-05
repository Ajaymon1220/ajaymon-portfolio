const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const dir = path.join(__dirname, '../dist/_next/static/immutable/chunks');
const code = fs.readFileSync(path.join(dir, '1yn8m_cadz_bt-ajay-v2-profile-final-mascot.js'), 'utf8');
const moduleBody = code.split(',908634,e=>{')[1].split('},785250,e=>')[0];
async function check(reduced, fail, skip = false) {
  let effect, component, ended = false, draws = 0, entrances = 0, time = 0;
  const html = {dataset:{}};
  const animation = () => ({finished:fail ? Promise.reject(Error('Animation unavailable')) : Promise.resolve(), cancel(){}});
  const paths = Array.from({length:9}, () => ({style:{}, getTotalLength:()=>100, animate(){draws++;return animation();}}));
  const jsx = (type, props) => {
    if(props.ref) props.ref.current = {style:{}, querySelectorAll:()=>paths, animate(){entrances++;return animation();}};
    return {type,props};
  };
  const hooks = {useRef:()=>({current:null}), useState:(v)=>[typeof v==='function'?v():v, (v)=>ended=v],useEffect:(fn)=>{effect=fn;}};
  const dependencies = {843476:{jsx,jsxs:jsx},271645:hooks,482852:{f:'mascot'},291390:{f:'signature'},988370:{i(){}},691572:{f:{movedBetweenPages:false}},330203:{V:async()=>{}}};
  const ctx = {e:{i:id=>dependencies[id],s:exports=>component=exports[2]},document:{documentElement:html,readyState:'complete',fonts:{ready:Promise.resolve()}},window:{__ajaySkipIntro:skip,scrollTo(){},matchMedia:()=>({matches:reduced}),innerWidth:1200,innerHeight:800},history:{},setTimeout:fn=>{queueMicrotask(fn);return 1;},performance:{now:()=>0},requestAnimationFrame:fn=>queueMicrotask(()=>fn(time+=250)),Promise};
  vm.runInNewContext(moduleBody,ctx);component();effect();
  for(let i=0;i<100;i++) await Promise.resolve();
  assert.equal(ended,true,'Loader must exit');
  assert.equal(html.dataset.preloader,undefined,'Scroll lock must clear');
  assert.equal(html.dataset.revealed,'true','Content must reveal');
  if(skip) assert.equal(draws,0,"Page switches must not animate the signature");
  if(!reduced&&!fail&&!skip){assert.equal(draws,9);assert.ok(entrances>0,'Mascot entrance must run');}
}
(async()=>{await check(false,false);await check(true,false);await check(false,true);await check(false,false,true);console.log('Loader: handwriting, mascot entrance, page reveal, reduced motion and failure recovery passed.');})().catch(e=>{console.error(e);process.exit(1);});

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const code = fs.readFileSync('dist/replica-runtime.js','utf8');
const key = 'ajay:page-switch';
const storage = new Map();
function enter(path, type='navigate') {
 const document = {documentElement:{dataset:{}}, addEventListener(name, fn){this.click=fn;}};
 const location = {origin:'https://portfolio.test',pathname:path,search:'',href:'https://portfolio.test'+path,assign(url){this.assigned=url;}};
 const window = {};
 vm.runInNewContext(code,{document,location,window,performance:{getEntriesByType:()=>[{type}]},sessionStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},URL,Date});
 return {document,location,window};
}
function click(page,href,extra={}) {
 const link={href:'https://portfolio.test'+href,target:'',download:'',hasAttribute:()=>false};
 const event={target:{closest:()=>link},button:0,preventDefault(){},stopImmediatePropagation(){},...extra};
 page.document.click(event);
}
const first=enter('/');assert.equal(first.window.__ajaySkipIntro,false);
click(first,'/work');assert.equal(first.location.assigned,'https://portfolio.test/work');
const work=enter('/work');assert.equal(work.window.__ajaySkipIntro,true);assert.equal(work.document.documentElement.dataset.revealed,'true');assert.equal(storage.has(key),false);
assert.equal(enter('/work','reload').window.__ajaySkipIntro,false);
click(work,'/about');assert.equal(enter('/about').window.__ajaySkipIntro,true);
assert.equal(enter('/work','back_forward').window.__ajaySkipIntro,true);
click(work,'/about');assert.equal(enter('/about','reload').window.__ajaySkipIntro,false);
click(work,'/about');assert.equal(enter('/playground').window.__ajaySkipIntro,false);
click(work,'/about',{metaKey:true});assert.equal(storage.has(key),false);
assert.equal(enter('/about').window.__ajaySkipIntro,false);
console.log('Navigation: first visits and refreshes play intro; internal switches and history skip it; markers are consumed and destination-specific.');

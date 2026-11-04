const {readFileSync}=require('fs'),{runInNewContext}=require('vm'),assert=require('assert');
let Character,raf,move,io; const media={matches:false,addEventListener(){}};
const face={style:{},classList:{add(){},remove(){}}},button={addEventListener(type,fn){this[type]=fn}},status={};
const ctx={HTMLElement:class{attachShadow(){return this.shadowRoot={innerHTML:'',querySelector:q=>q==='.face'?face:q==='button'?button:status}}getBoundingClientRect(){return {left:0,top:0,width:100,height:100}}},customElements:{get(){},define(n,c){Character=c}},matchMedia:q=>q.includes('pointer')?{matches:true}:media,AbortController,IntersectionObserver:class{constructor(fn){io=fn}observe(){}disconnect(){}},window:{addEventListener(t,fn){if(t==='pointermove')move=fn}},document:{documentElement:{addEventListener(){}},addEventListener(){}},Image:class{},requestAnimationFrame:fn=>(raf=fn,1),cancelAnimationFrame(){},setTimeout(){return 1},clearTimeout(){},Math};
runInNewContext(readFileSync('dist/mascot.js','utf8'),ctx);const mascot=new Character();mascot.connectedCallback();
for(const [x,y,expected] of [[-200,-200,0],[50,-200,1],[300,-200,2],[-200,50,3],[50,50,4],[300,50,5],[-200,300,6],[50,300,7],[300,300,8]]){move({clientX:x,clientY:y,pointerType:'mouse'});raf();assert.equal(mascot.frame,expected)}
for(const frame of [0,1,2,3,5,6,7,8]){button.click();assert.equal(mascot.frame,frame);assert.equal(mascot.reaction,true)}
mascot.reset();media.matches=true;move({clientX:999,clientY:999,pointerType:'mouse'});assert.equal(mascot.frame,4);button.click();assert.equal(mascot.reaction,true);mascot.disconnectedCallback();assert.equal(mascot.reaction,false);
const previous=mascot.abort;mascot.connectedCallback();assert.notEqual(mascot.abort,previous,'Reconnecting must attach fresh event listeners');assert.equal(mascot.abort.signal.aborted,false);
console.log('Passed: nine gaze directions, eight reactions, reduced-motion behavior, cleanup, and streamed-node reconnection.');

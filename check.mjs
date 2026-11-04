import {readdir,readFile,stat} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {spawnSync} from 'node:child_process';
const root=resolve('dist');
async function walk(p){return(await Promise.all((await readdir(p,{withFileTypes:true})).map(e=>e.isDirectory()?walk(resolve(p,e.name)):[resolve(p,e.name)]))).flat();}
let errors=[],pages=0,js=0;
for(const file of await walk(root)){
 if(file.endsWith('.js')){js++;const r=spawnSync(process.execPath,['--check',file],{encoding:'utf8'});if(r.status)errors.push(r.stderr);}
 if(!/\.(html|css)$/.test(file))continue;
 const s=await readFile(file,'utf8');if(file.endsWith('.html'))pages++;
 const refs=file.endsWith('.html')?[...s.matchAll(/(?:src|href)="(\/[^"#?]*)(?:[^" ]*)"/g)].map(x=>x[1]):[...s.matchAll(/url\((\.\.\/media\/[^)]+)\)/g)].map(x=>x[1]);
 for(const ref of refs){const path=ref.startsWith('/')?resolve(root,'.'+ref):resolve(dirname(file),ref);try{await stat(path);}catch{errors.push(`${file}: missing ${ref}`);}}
}
if(errors.length){console.error([...new Set(errors)].join('\n'));process.exit(1);}
console.log(`Validated ${pages} pages, ${js} JavaScript files, and all HTML/CSS local asset references.`);

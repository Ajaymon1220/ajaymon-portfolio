import {createServer} from 'node:http';
import {readFile,stat} from 'node:fs/promises';
import {resolve,extname,sep} from 'node:path';
const root=resolve(import.meta.dirname,'dist');
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.woff2':'font/woff2','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.svg':'image/svg+xml','.webp':'image/webp','.mp3':'audio/mpeg','.mp4':'video/mp4'};
createServer(async(req,res)=>{try{const url=new URL(req.url,'http://localhost');let p=resolve(root,'.'+decodeURIComponent(url.pathname));if(p!==root&&!p.startsWith(root+sep)){res.writeHead(403).end();return;}if((await stat(p)).isDirectory())p=resolve(p,'index.html');const data=await readFile(p);res.writeHead(200,{'Content-Type':mime[extname(p)]||'application/octet-stream'});res.end(data);}catch{res.writeHead(404).end('Not found');}}).listen(5174,'127.0.0.1',()=>console.log('Replica: http://127.0.0.1:5174'));

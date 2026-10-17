import {build} from "esbuild";
import {readFile,writeFile,mkdir} from "node:fs/promises";
import path from "node:path";
const partial=process.argv.includes("--allow-partial");
const manifest=JSON.parse(await readFile("config/render-manifest.json","utf8"));
if(!manifest.complete&&!partial)throw new Error("Refusing to label an incomplete frame sequence as a full review. Use --allow-partial for authoring only.");
const assets={};
for(const file of new Set([manifest.poster,...manifest.frames.map(frame=>frame.src)])){
 const bytes=await readFile("public"+file);assets[file]="data:image/webp;base64,"+bytes.toString("base64");
}
const result=await build({entryPoints:["scripts/preview-entry.tsx"],bundle:true,write:false,minify:true,format:"iife",target:"es2020",jsx:"automatic",tsconfig:"tsconfig.json",legalComments:"eof",define:{"process.env.NODE_ENV":'"production"',"process.env.NEXT_PUBLIC_BUSINESS_PHONE":JSON.stringify(process.env.NEXT_PUBLIC_BUSINESS_PHONE??"+19175310595")}});
let css=await readFile("styles/globals.css","utf8");
for(const file of ["archivo-600.woff2","instrument-400.woff2","instrument-500.woff2","mono-400.woff2"]){
 const bytes=await readFile(path.join("public/fonts",file));css=css.replaceAll("/fonts/"+file,"data:font/woff2;base64,"+bytes.toString("base64"));
}
const script=result.outputFiles[0].text.replaceAll("</script","<\\/script");
const licenses=await Promise.all(["archivo","instrument-sans","ibm-plex-mono"].map(name=>readFile("public/fonts/"+name+"-LICENSE.txt","utf8")));
licenses.push(await readFile("public/third-party-notices.txt","utf8"));
const html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#090d12"><title>IP NET Security &amp; Locksmith — Website Review</title><style>'+css+'</style></head><body><a class="skip-link" href="#services">Skip the journey — explore our services</a><div id="root"></div><script>window.__IPNET_ASSETS__='+JSON.stringify(assets)+';</script><script>'+script+'</script><script type="text/plain" id="font-licenses">'+licenses.join("\n")+'</script></body></html>';
await mkdir("preview",{recursive:true});await writeFile("preview/IP-NET-Website-Review.html",html);
console.log(JSON.stringify({review:"preview/IP-NET-Website-Review.html",bytes:Buffer.byteLength(html),embeddedAssets:Object.keys(assets).length,complete:manifest.complete}));

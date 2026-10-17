const fs=require("node:fs");
const assert=require("node:assert/strict");
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||"/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");
const manifest=JSON.parse(fs.readFileSync("config/render-manifest.json","utf8"));
(async()=>{
 assert(manifest.complete,"Only a complete film can pass the release review check.");
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||"/usr/bin/chromium",args:["--no-sandbox"]});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[],requests=[];
  page.on("pageerror",e=>errors.push(e.message));
  await page.route("**/*",route=>{requests.push(route.request().url());return route.abort();});
  await page.setContent(fs.readFileSync("preview/IP-NET-Website-Review.html","utf8"),{waitUntil:"load"});
  await page.locator('.journey-stage[data-ready="true"]').waitFor();
  for(const p of [0,.265,.735,.999,0]){
   await page.evaluate(p=>{const el=document.querySelector(".journey");window.scrollTo({top:p*(el.clientHeight-innerHeight),behavior:"instant"});},p);
   await page.waitForFunction(p=>Math.abs(Number(document.querySelector(".journey-stage").dataset.progress)-p)<.002,p);
   await page.waitForFunction(i=>Number(document.querySelector(".journey-stage").dataset.frame)===i,Math.round(p*(manifest.frames.length-1)));
  }
  assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
  const result={passed:true,completeJourney:true,embeddedFrames:manifest.frames.length,externalRequests:0,forwardAndReverse:true};
  fs.writeFileSync("/tmp/ipnet-offline-check.json",JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});

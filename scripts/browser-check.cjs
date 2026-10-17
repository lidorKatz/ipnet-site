/* Functional smoke checks against an already-running local export/dev server.
   PLAYWRIGHT_MODULE can point at an installed Playwright module; no browser
   download or external message submission is performed by this script. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||"/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const origin=process.argv[2]||"http://127.0.0.1:3001";
const manifest=JSON.parse(fs.readFileSync("config/render-manifest.json","utf8"));
const scenes=JSON.parse(fs.readFileSync("config/journey.json","utf8")).scenes;
const output=process.env.IPNET_CHECK_OUTPUT||"/tmp/ipnet-browser-check";
fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||"/usr/bin/chromium",args:["--no-sandbox"]});
 try{
  const context=await browser.newContext({viewport:{width:1440,height:1000}});const page=await context.newPage();const errors=[];
  page.on("pageerror",error=>errors.push(error.message));
  const response=await page.goto(origin,{waitUntil:"networkidle"});assert.equal(response.status(),200);
  await page.locator('.journey-stage[data-ready="true"]').waitFor();
  assert.match(await page.title(),/IP NET Security & Locksmith/);
  assert.equal(await page.locator("h1").count(),1);
  await page.screenshot({path:output+"/desktop-intro.png"});
  const checkpoint=[];
  async function seek(p){
   await page.evaluate(p=>{const el=document.querySelector(".journey");window.scrollTo({top:el.offsetTop+p*(el.clientHeight-innerHeight),behavior:"instant"});},p);
   await page.waitForFunction(p=>Math.abs(Number(document.querySelector(".journey-stage").dataset.progress)-p)<.002,p);
   const frame=manifest.frames.reduce((best,f,i)=>Math.abs(f.progress-p)<Math.abs(manifest.frames[best].progress-p)?i:best,0);
   if(manifest.frames.length)await page.waitForFunction(i=>Number(document.querySelector(".journey-stage").dataset.frame)===i,frame);
   const state=await page.locator(".journey-stage").evaluate(el=>({...el.dataset}));assert(Number(state.cachedFrames)<=18);return state;
  }
  for(const scene of scenes){const p=scene.id==="intro"?0:scene.id==="final"?.999:(scene.start+scene.end)/2;const state=await seek(p);assert.equal(state.scene,scene.id);checkpoint.push({scene:scene.id,frame:state.frame});if(["cctv","intercom","network","locksmith","final"].includes(scene.id))await page.screenshot({path:output+"/desktop-"+scene.id+".png"});}
  await seek(.735);await page.getByRole("button",{name:"Explore Network infrastructure",exact:true}).click();await page.locator("#system-detail").waitFor();assert.match(await page.locator("#system-detail").innerText(),/Structured cabling/);await page.keyboard.press("Escape");assert.equal(await page.locator("#system-detail").count(),0);
  const reverse=await seek(.145);assert.equal(reverse.scene,"cctv");
  const call=await page.locator(".dock-call").getAttribute("href");assert.equal(call,"tel:+19175310595");
  assert.equal(await page.locator('.contact-dock a[aria-label^="Message IP NET"]').getAttribute("href"),"https://wa.me/19175310595");
  await page.locator("#quote").scrollIntoViewIfNeeded();await page.getByRole("button",{name:"REVIEW YOUR MESSAGE"}).click();assert.equal(await page.locator("#quote-name").getAttribute("aria-invalid"),"true");
  await page.locator("#quote-name").fill("Website review");await page.locator("#quote-email").fill("review@example.com");await page.locator("#quote-service").selectOption("Wi-Fi & Networking");await page.locator("#quote-details").fill("Please improve Wi-Fi coverage in our building.");await page.getByRole("button",{name:"REVIEW YOUR MESSAGE"}).click();
  await page.locator(".inquiry-ready").waitFor();assert.match(await page.locator(".inquiry-ready").innerText(),/Nothing has been sent yet/);
  const email=await page.getByRole("link",{name:"OPEN EMAIL",exact:true}).getAttribute("href");assert.match(email,/^mailto:ipnet.security@gmail.com\?/);assert.match(decodeURIComponent(email),/review@example.com/);
  const whatsapp=await page.getByRole("link",{name:"OPEN WHATSAPP",exact:true}).getAttribute("href");assert.match(whatsapp,/^https:\/\/wa.me\/19175310595\?text=/);assert.match(decodeURIComponent(whatsapp),/Wi-Fi & Networking/);
  await page.getByRole("button",{name:"Edit your details"}).click();assert.equal(await page.locator("#quote-name").inputValue(),"Website review");
  for(const width of [320,390,768,1440]){await page.setViewportSize({width,height:width===320?667:844});await seek(0);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),"Horizontal overflow at "+width);await page.screenshot({path:output+"/intro-"+width+".png"});}
  await page.setViewportSize({width:390,height:844});await seek(.265);await page.getByRole("button",{name:"Explore Video intercom",exact:true}).click();const panel=await page.locator("#system-detail").boundingBox();assert(panel.x>=0&&panel.x+panel.width<=390,"Hotspot panel exceeds phone viewport");await page.keyboard.press("Escape");
  await page.getByRole("button",{name:"Open navigation",exact:true}).click();assert.equal(await page.locator(".menu-toggle").getAttribute("aria-expanded"),"true");await page.keyboard.press("Escape");assert.equal(await page.locator(".menu-toggle").getAttribute("aria-expanded"),"false");
  await page.getByRole("button",{name:"Open navigation",exact:true}).click();await page.locator(".main-nav").getByRole("link",{name:"SERVICE AREA",exact:true}).click();assert.equal(await page.locator(".menu-toggle").getAttribute("aria-expanded"),"false");await page.waitForFunction(()=>{const y=document.querySelector("#coverage").getBoundingClientRect().top;return y>=0&&y<120;});
  await page.screenshot({path:output+"/phone-coverage.png"});
  const reduced=await browser.newContext({viewport:{width:390,height:844},reducedMotion:"reduce"});const rp=await reduced.newPage();await rp.goto(origin,{waitUntil:"networkidle"});await rp.locator(".journey.reduced").waitFor();assert.equal(await rp.locator(".chapter-rail").count(),0);assert(await rp.locator("#services").isVisible());assert(await rp.locator(".journey").evaluate(el=>el.clientHeight<=innerHeight+2));await reduced.close();
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const np=await nojs.newPage();await np.goto(origin);assert(await np.locator("h1").isVisible());assert(await np.locator(".journey-poster").evaluate(el=>el.complete&&el.naturalWidth>0));assert.equal(await np.locator(".scene-loading").count(),0);assert(await np.locator(".journey").evaluate(el=>el.clientHeight<=innerHeight+2));await nojs.close();
  assert.deepEqual(errors,[]);const result={passed:true,completeJourney:manifest.complete,renderedFrames:manifest.frames.length,chapters:checkpoint,reverse:true,quoteReviewEdit:true,contactLinks:true,responsiveWidths:[320,390,768,1440],reducedMotion:true,noJavaScriptPoster:true,browser:"Chromium desktop emulation; physical devices unverified"};fs.writeFileSync(output+"/result.json",JSON.stringify(result,null,2));console.log(JSON.stringify(result));await context.close();
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});

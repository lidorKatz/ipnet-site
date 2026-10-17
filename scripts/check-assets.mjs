import {readFile} from "node:fs/promises";
import {createHash} from "node:crypto";
const manifest=JSON.parse(await readFile("config/render-manifest.json","utf8"));
const spec=JSON.parse(await readFile("config/journey.json","utf8"));
if(!manifest.complete||manifest.frames.length!==spec.frameCount){
 if(process.env.IPNET_ALLOW_PARTIAL==="1"){console.warn("AUTHORING BUILD: rendered journey is incomplete; not a release.");process.exit(0);}
 throw new Error("Rendered journey is incomplete. Run assets:render and assets:prepare before a release build.");
}
let previous=-1;
for(const [index,frame] of manifest.frames.entries()){
 if(frame.progress<=previous)throw new Error("Frame progress is not strictly ordered.");
 if(Math.abs(frame.progress-index/(spec.frameCount-1))>1e-9)throw new Error("A rendered frame is missing or misplaced.");
 if(frame.src!==`/journey/frames/frame-${String(index).padStart(3,"0")}.webp`)throw new Error("Unexpected rendered frame path.");
 previous=frame.progress;
 const file=await readFile("public"+frame.src);
 if(createHash("sha256").update(file).digest("hex")!==frame.sha256)throw new Error("Frame integrity mismatch: "+frame.src);
}
await readFile("public"+manifest.poster);
console.log("Verified complete rendered journey: "+manifest.frames.length+" frames.");

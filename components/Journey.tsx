"use client";
import {useCallback,useEffect,useLayoutEffect,useRef,useState} from "react";
import gsap from "gsap";
import {ScrollTrigger} from "gsap/ScrollTrigger";
import specification from "@/config/journey.json";
import data from "@/config/render-manifest.json";
import {asset} from "@/lib/assets";
import {brand} from "@/config/brand";
import {Arrow} from "./Icons";
import {SystemHotspot} from "./SystemHotspot";
type Frame={src:string;progress:number};
const manifest=data as {frames:Frame[];poster:string;complete:boolean;width:number;height:number};
const {scenes}=specification;
function clamp(n:number){return Math.max(0,Math.min(1,n));}
function smooth(n:number){n=clamp(n);return n*n*(3-2*n);}
export function Journey(){
 const container=useRef<HTMLDivElement>(null),stage=useRef<HTMLDivElement>(null),canvas=useRef<HTMLCanvasElement>(null);
 const progress=useRef(0),draw=useRef<(p:number)=>void>(()=>{}),overlays=useRef<(HTMLElement|null)[]>([]);
 const bar=useRef<HTMLDivElement>(null),chapter=useRef<HTMLSpanElement>(null);
 const[ready,setReady]=useState(false),[reduced,setReduced]=useState(false),[debug,setDebug]=useState(false);
 const [activeScene,setActiveScene]=useState("intro");const activeId=useRef("intro");
 const resize=useRef<()=>void>(()=>{});
 useEffect(()=>{const media=matchMedia("(prefers-reduced-motion: reduce)");const update=()=>setReduced(media.matches);update();media.addEventListener("change",update);setDebug(new URLSearchParams(location.search).get("debug")==="1");return()=>media.removeEventListener("change",update);},[]);
 useEffect(()=>{
  const surface=canvas.current;if(!surface)return;const ctx=surface.getContext("2d",{alpha:false});if(!ctx){setReady(true);return;}
  let disposed=false,current:HTMLImageElement|null=null,target=0,renderedIndex=-1,raf=0;
  const cache=new Map<number,{image:HTMLImageElement;ready:boolean}>(),failed=new Set<number>();
  const paint=()=>{if(disposed||!current)return;const w=surface.width,h=surface.height;const scale=Math.max(w/current.naturalWidth,h/current.naturalHeight);
   const dw=current.naturalWidth*scale,dh=current.naturalHeight*scale;ctx.fillStyle="#080b0f";ctx.fillRect(0,0,w,h);ctx.drawImage(current,(w-dw)/2,(h-dh)/2,dw,dh);if(stage.current){stage.current.dataset.frame=String(renderedIndex);stage.current.dataset.cachedFrames=String(cache.size);}
  };
  const load=(index:number,priority=false)=>{
   if(index<0||index>=manifest.frames.length||failed.has(index))return;
   const existing=cache.get(index);if(existing){if(existing.ready&&index===target){current=existing.image;renderedIndex=index;paint();}return;}
   const image=new Image();image.decoding="async";if(priority)image.fetchPriority="high";
   const entry={image,ready:false};cache.set(index,entry);
   image.onload=()=>{if(disposed||cache.get(index)!==entry)return;entry.ready=true;if(index===target){current=image;renderedIndex=index;paint();setReady(true);}};
   image.onerror=()=>{if(cache.get(index)!==entry)return;failed.add(index);cache.delete(index);};
   image.src=asset(manifest.frames[index].src);
   while(cache.size>18){const key=[...cache.keys()].sort((a,b)=>Math.abs(b-target)-Math.abs(a-target))[0];if(key===target)break;const old=cache.get(key);cache.delete(key);if(old&&!old.ready)old.image.src="data:,";}
  };
  draw.current=(p)=>{
   if(!manifest.frames.length){paint();return;}
   let low=0,high=manifest.frames.length-1;
   while(low<high){const middle=Math.floor((low+high)/2);if(manifest.frames[middle].progress<p)low=middle+1;else high=middle;}
   let nearest=low;if(low>0&&Math.abs(manifest.frames[low-1].progress-p)<Math.abs(manifest.frames[low].progress-p))nearest=low-1;
   target=nearest;load(target,true);for(let i=1;i<=5;i++){load(target+i);load(target-i);}
  };
  resize.current=()=>{const bounds=surface.getBoundingClientRect();const ratio=Math.min(devicePixelRatio,innerWidth<761?1.25:1.5);surface.width=Math.max(1,Math.round(bounds.width*ratio));surface.height=Math.max(1,Math.round(bounds.height*ratio));paint();};
  const poster=new Image();poster.fetchPriority="high";poster.onload=()=>{if(disposed)return;current=poster;resize.current();setReady(true);draw.current(progress.current);};poster.onerror=()=>{if(!disposed)setReady(true);};poster.src=asset(manifest.poster);
  const onResize=()=>{cancelAnimationFrame(raf);raf=requestAnimationFrame(resize.current);};window.addEventListener("resize",onResize);resize.current();
  return()=>{disposed=true;draw.current=()=>{};window.removeEventListener("resize",onResize);cancelAnimationFrame(raf);cache.clear();};
 },[]);
 const update=useCallback((value:number)=>{
  const p=clamp(value);progress.current=p;const index=scenes.findIndex((scene,i)=>p>=scene.start&&(p<scene.end||i===scenes.length-1));const active=scenes[Math.max(0,index)];
  if(activeId.current!==active.id){activeId.current=active.id;setActiveScene(active.id);}
  if(stage.current){stage.current.dataset.progress=p.toFixed(5);stage.current.dataset.scene=active.id;}
  if(bar.current)bar.current.style.transform=`scaleX(${p})`;
  if(chapter.current)chapter.current.textContent=active.id==="intro"?"SCROLL TO EXPLORE":active.label;
  for(let i=0;i<scenes.length;i++){const scene=scenes[i],el=overlays.current[i];if(!el)continue;
   let opacity=0;if(scene.id==="intro")opacity=1-smooth((p-.045)/.035);else if(scene.id==="final")opacity=smooth((p-.984)/.014);else opacity=Math.min(smooth((p-scene.start)/.015),smooth((scene.end-p)/.015));
   el.style.opacity=String(opacity);el.style.transform=`translateY(${(1-opacity)*12}px)`;el.inert=opacity<.8;el.setAttribute("aria-hidden",String(opacity<.15));
  }draw.current(p);
 },[]);
 useLayoutEffect(()=>{
  gsap.registerPlugin(ScrollTrigger);if(!container.current)return;
  if(reduced){update(.04);return;}
  const clock={p:0};const context=gsap.context(()=>{gsap.to(clock,{p:1,ease:"none",onUpdate:()=>update(clock.p),scrollTrigger:{trigger:container.current,start:"top top",end:"bottom bottom",scrub:.3,invalidateOnRefresh:true}});},container);
  update(0);ScrollTrigger.refresh();return()=>context.revert();
 },[reduced,update]);
 function jump(p:number){if(!container.current)return;window.scrollTo({top:container.current.offsetTop+p*(container.current.clientHeight-innerHeight),behavior:"instant"});}
 return <div className={reduced?"journey reduced":"journey"} ref={container} id="top">
 <div className="journey-stage" ref={stage} data-progress="0" data-scene="intro" data-ready={ready}>
  <img className="journey-poster" src={asset(manifest.poster)} alt="" fetchPriority="high"/><canvas ref={canvas} className="journey-canvas" aria-hidden="true"/><div className="scene-tint" aria-hidden="true"/>
  <div className="scene-overlays">{scenes.map((scene,index)=><section key={scene.id} ref={el=>{overlays.current[index]=el;}} className={`scene-overlay copy-${["cctv","lobby"].includes(scene.id)?"left":scene.side}`} data-scene={scene.id} aria-label={scene.label}>
    <div className="scene-copy"><span className="eyebrow"><i/>{scene.label}</span>
    {scene.id==="intro"?<h1>{scene.headline.map(line=><span key={line}>{line}</span>)}</h1>:<h2>{scene.headline.map(line=><span key={line}>{line}</span>)}</h2>}
    <p>{scene.body}</p>
    {scene.id==="intro"&&<a className="text-link" href="#services">EXPLORE OUR EXPERTISE <Arrow/></a>}
    {scene.id==="final"&&<div className="final-actions"><a className="button" href="#quote">REQUEST A QUOTE <Arrow/></a>{brand.telephone&&<a className="button outline" href={brand.telephone}>CALL NOW <Arrow/></a>}</div>}
    {scene.id==="locksmith"&&brand.telephone&&<a className="text-link" href={brand.telephone}>{brand.phoneDisplay} <Arrow/></a>}
    </div>
  </section>)}</div>
  {!reduced&&<SystemHotspot scene={activeScene}/>}
  {!reduced&&<nav className="chapter-rail" aria-label="Explore the building">{scenes.filter(s=>s.id!=="intro"&&s.id!=="final"&&s.id!=="xray").map((s,i)=><button key={s.id} onClick={()=>jump((s.start+s.end)/2)} aria-label={`Explore ${s.label.split(" / ")[1]}`} title={s.label.split(" / ")[1]}><span>{String(i+1).padStart(2,"0")}</span><i/></button>)}</nav>}
  <div className="journey-bottom"><span ref={chapter}>SCROLL TO EXPLORE</span><a href="#services">{reduced?"EXPLORE OUR SERVICES":"ONE PROPERTY. EVERY CONNECTION."}<Arrow/></a></div>
  <div className="journey-progress" ref={bar}/>
  {debug&&<div className="debug-controls"><label>Journey progress<input type="range" min="0" max="1" step=".001" onChange={event=>jump(Number(event.target.value))}/></label></div>}
 </div></div>;
}

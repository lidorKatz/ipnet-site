"use client";
import {useEffect,useRef,useState} from "react";
import {Arrow} from "./Icons";
const systems:Record<string,{name:string;scope:string[];position:[number,number]}>= {
 cctv:{name:"CCTV & video surveillance",scope:["Camera installation and placement","Recording and remote viewing","Diagnostics and system repairs"],position:[62,52]},
 intercom:{name:"Video intercom",scope:["Video entry and communication","New installations and upgrades","Existing-system troubleshooting"],position:[51,59]},
 access:{name:"Access control",scope:["Readers and credentials","Connected door hardware","Installation, configuration and service"],position:[64,57]},
 lobby:{name:"Connected entry",scope:["CCTV, intercom and controlled entry","One team across connected systems","Diagnostics, repairs and upgrades"],position:[51,57]},
 network:{name:"Network infrastructure",scope:["Racks, cabinets and patch panels","Structured cabling and PoE","Cable management and fault finding"],position:[57,57]},
 wireless:{name:"Wi-Fi & connectivity",scope:["Access point installation","Coverage and network configuration","Connectivity diagnostics and repairs"],position:[52,48]},
 locksmith:{name:"Locksmith & door hardware",scope:["Residential, commercial and automotive","Locks and door hardware","24/7 emergency locksmith service"],position:[53,56]},
};
export function SystemHotspot({scene}:{scene:string}){
 const [open,setOpen]=useState(false);const root=useRef<HTMLDivElement>(null),button=useRef<HTMLButtonElement>(null);
 const system=systems[scene];
 useEffect(()=>{setOpen(false);},[scene]);
 useEffect(()=>{if(!open)return;const key=(e:KeyboardEvent)=>{if(e.key==="Escape"){setOpen(false);button.current?.focus();}};const outside=(e:PointerEvent)=>{if(e.target instanceof Node&&!root.current?.contains(e.target))setOpen(false);};window.addEventListener("keydown",key);document.addEventListener("pointerdown",outside);return()=>{window.removeEventListener("keydown",key);document.removeEventListener("pointerdown",outside);};},[open]);
 if(!system)return null;
 return <div className="system-hotspot" ref={root} style={{left:system.position[0]+"%",top:system.position[1]+"%"}}>
  <button className="hotspot-toggle" ref={button} onClick={()=>setOpen(!open)} aria-expanded={open} aria-controls="system-detail" aria-label={`Explore ${system.name}`}><span aria-hidden="true">{open?"−":"+"}</span><small>EXPLORE THIS SYSTEM</small></button>
  {open&&<aside id="system-detail" className="system-detail" aria-label={system.name}><span className="eyebrow">CONNECTED EXPERTISE</span><h3>{system.name}</h3><ul>{system.scope.map(item=><li key={item}>{item}</li>)}</ul><a className="text-link" href="#quote" onClick={()=>setOpen(false)}>DISCUSS YOUR PROPERTY <Arrow/></a></aside>}
 </div>;
}

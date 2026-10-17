"use client";
import {useEffect,useRef,useState} from "react";
import {brand} from "@/config/brand";
import {Arrow,Chat,Mark,Phone} from "./Icons";
export function Header(){
 const[open,setOpen]=useState(false);const root=useRef<HTMLElement>(null);const toggle=useRef<HTMLButtonElement>(null);const nav=useRef<HTMLElement>(null);
 useEffect(()=>{if(!open)return;nav.current?.querySelector<HTMLAnchorElement>("a")?.focus();
 const key=(event:KeyboardEvent)=>{if(event.key==="Escape"){setOpen(false);toggle.current?.focus();}};
 const outside=(event:PointerEvent)=>{if(event.target instanceof Node&&!root.current?.contains(event.target))setOpen(false);};
 window.addEventListener("keydown",key);document.addEventListener("pointerdown",outside);return()=>{window.removeEventListener("keydown",key);document.removeEventListener("pointerdown",outside);};},[open]);
 return <header className="site-header" ref={root}>
 <a className="wordmark" href="#top" aria-label="IP NET Security and Locksmith home"><Mark/><span>IP.NET<small>SECURITY &amp; LOCKSMITH</small></span></a>
 <nav className={open?"main-nav open":"main-nav"} id="main-nav" ref={nav} aria-label="Main navigation">{[["EXPERTISE","#services"],["WHO WE HELP","#properties"],["SERVICE AREA","#coverage"],["CONTACT","#quote"]].map(([label,href])=><a key={href} href={href} onClick={()=>setOpen(false)}>{label}</a>)}</nav>
 <div className="header-actions">{brand.telephone&&<a className="header-call" href={brand.telephone}><span>LOCKSMITH 24/7</span><strong>{brand.phoneDisplay}</strong></a>}<a className="header-quote" href="#quote">LET’S TALK <Arrow/></a></div>
 <button className="menu-toggle" ref={toggle} aria-controls="main-nav" aria-expanded={open} aria-label={open?"Close navigation":"Open navigation"} onClick={()=>setOpen(!open)}><i/><i/></button>
 </header>;
}
export function ContactDock(){return <nav className="contact-dock" aria-label="Quick contact">
 {brand.telephone&&<a className="dock-call" href={brand.telephone}><Phone/><span>Call now<small>24/7 emergency locksmith</small></span></a>}
 {brand.whatsapp&&<a href={brand.whatsapp} target="_blank" rel="noopener noreferrer" aria-label="Message IP NET on WhatsApp, opens a new tab"><Chat/><span>WhatsApp<small>Message our team</small></span></a>}
 <a href="#quote"><Arrow/><span>Get in touch<small>Tell us what you need</small></span></a>
 </nav>;}

"use client";
import {useRef,useState,type FormEvent} from "react";
import {brand} from "@/config/brand";
import {Arrow,Chat} from "./Icons";
const services=["CCTV / Cameras","Video Intercom","Access Control","Wi-Fi & Networking","Structured Cabling & Racks","Diagnostics & Repairs","Locksmith & Door Hardware","Emergency Locksmith","Multiple Systems","Other"];
type Inquiry={name:string;company:string;email:string;phone:string;service:string;details:string};
const empty:Inquiry={name:"",company:"",email:"",phone:"",service:"",details:""};
export function QuoteForm(){
 const[values,setValues]=useState<Inquiry>(empty),[errors,setErrors]=useState<Partial<Record<keyof Inquiry,string>>>({}),[prepared,setPrepared]=useState<Inquiry|null>(null);
 const form=useRef<HTMLFormElement>(null),title=useRef<HTMLHeadingElement>(null);
 function submit(event:FormEvent){event.preventDefault();const next:typeof errors={};
  if(values.name.trim().length<2)next.name="Please enter your name.";
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email.trim()))next.email="Please enter a valid email address.";
  if(values.phone.trim()&&!/^\+?[\d ()\-.]{7,25}$/.test(values.phone.trim()))next.phone="Please check your phone number.";
  if(!services.includes(values.service))next.service="Choose a service.";
  if(values.details.trim().length<10)next.details="Tell us a little about what you need.";
  setErrors(next);if(Object.keys(next).length){requestAnimationFrame(()=>form.current?.querySelector<HTMLInputElement>('[aria-invalid="true"]')?.focus());return;}
  const normalized=Object.fromEntries(Object.entries(values).map(([key,value])=>[key,value.trim()])) as Inquiry;setPrepared(normalized);requestAnimationFrame(()=>title.current?.focus());
 }
 if(prepared){const summary=`Hello IP NET,\n\nService: ${prepared.service}\nName: ${prepared.name}\nCompany / Property: ${prepared.company||"—"}\nEmail: ${prepared.email}\nPhone: ${prepared.phone||"—"}\n\n${prepared.details}`;
  const email=`mailto:${brand.email}?subject=${encodeURIComponent("Project inquiry: "+prepared.service)}&body=${encodeURIComponent(summary)}`;
  return <div className="inquiry-ready"><span className="eyebrow">YOUR MESSAGE IS READY</span><h3 ref={title} tabIndex={-1}>Let’s get<br/>connected.</h3><p>Choose email or WhatsApp. Review your message there, then send it to our team. Nothing has been sent yet.</p>
   <dl><div><dt>Service</dt><dd>{prepared.service}</dd></div><div><dt>Name</dt><dd>{prepared.name}</dd></div><div><dt>Contact</dt><dd>{prepared.email}</dd></div><div><dt>Details</dt><dd>{prepared.details}</dd></div></dl>
   <div className="quote-actions"><a className="button" href={email}>OPEN EMAIL <Arrow/></a>{brand.whatsapp&&<a className="button outline" href={brand.whatsapp+"?text="+encodeURIComponent(summary)} target="_blank" rel="noopener noreferrer">OPEN WHATSAPP <Chat/></a>}</div>
   <button className="text-button" onClick={()=>{setPrepared(null);requestAnimationFrame(()=>form.current?.querySelector<HTMLInputElement>("input")?.focus());}}>Edit your details</button>
  </div>;
 }
 return <form className="quote-form" ref={form} noValidate onSubmit={submit}>
 <div className="form-grid">{([{key:"name",label:"Your name",type:"text",auto:"name",required:true},{key:"company",label:"Company / Property",type:"text",auto:"organization",required:false},{key:"email",label:"Email address",type:"email",auto:"email",required:true},{key:"phone",label:"Phone number",type:"tel",auto:"tel",required:false}] as const).map(field=><div className="form-field" key={field.key}><label htmlFor={"quote-"+field.key}>{field.label}{field.required&&" *"}</label><input id={"quote-"+field.key} name={field.key} type={field.type} autoComplete={field.auto} maxLength={field.key==="phone"?25:200} required={field.required} value={values[field.key]} onChange={e=>setValues({...values,[field.key]:e.target.value})} aria-invalid={!!errors[field.key]} aria-describedby={errors[field.key]?"error-"+field.key:undefined}/>{errors[field.key]&&<p className="field-error" id={"error-"+field.key}>{errors[field.key]}</p>}</div>)}</div>
 <div className="form-field"><label htmlFor="quote-service">What can we help with? *</label><select id="quote-service" value={values.service} required onChange={e=>setValues({...values,service:e.target.value})} aria-invalid={!!errors.service} aria-describedby={errors.service?"error-service":undefined}><option value="">Select a service</option>{services.map(s=><option key={s}>{s}</option>)}</select>{errors.service&&<p id="error-service" className="field-error">{errors.service}</p>}</div>
 <div className="form-field"><label htmlFor="quote-details">Tell us about your project *</label><textarea id="quote-details" rows={4} maxLength={2000} required placeholder="Your property, your systems, and how we can help." value={values.details} onChange={e=>setValues({...values,details:e.target.value})} aria-invalid={!!errors.details} aria-describedby={errors.details?"error-details":undefined}/>{errors.details&&<p id="error-details" className="field-error">{errors.details}</p>}</div>
 <div className="form-submit"><button className="button" type="submit">REVIEW YOUR MESSAGE <Arrow/></button><p>Next, choose email or WhatsApp to send your inquiry.</p></div>
 </form>;
}

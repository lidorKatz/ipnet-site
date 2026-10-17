import type {Metadata} from "next";
import localFont from "next/font/local";
import {brand} from "@/config/brand";
import "@/styles/globals.css";
const archivo=localFont({src:"../public/fonts/archivo-600.woff2",weight:"600",variable:"--font-heading",display:"swap"});
const instrument=localFont({src:[{path:"../public/fonts/instrument-400.woff2",weight:"400"},{path:"../public/fonts/instrument-500.woff2",weight:"500"}],variable:"--font-body",display:"swap"});
const mono=localFont({src:"../public/fonts/mono-400.woff2",weight:"400",variable:"--font-mono",display:"swap"});
export const metadata:Metadata={
 metadataBase:new URL(brand.url),title:"IP NET Security & Locksmith | NYC, Northern NJ & Westchester",
 description:"CCTV, intercom, access control, Wi-Fi, structured cabling, repairs and 24/7 emergency locksmith services across NYC, Northern New Jersey and Westchester.",
 alternates:{canonical:"/"},openGraph:{title:"IP NET — One team. Total security.",description:"Security, entry and connectivity. Brought together.",url:brand.url,siteName:brand.name,locale:"en_US",type:"website"},robots:{index:true,follow:true}
};
const organization={"@context":"https://schema.org","@type":"Organization",name:brand.name,url:brand.url,email:brand.email,...(brand.telephone?{telephone:brand.telephone.slice(4)}:{}),slogan:"One team. Total security.",areaServed:["New York City","Northern New Jersey","Westchester County"]};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en" className={archivo.variable+" "+instrument.variable+" "+mono.variable}><body><script type="application/ld+json" dangerouslySetInnerHTML={{__html:JSON.stringify(organization).replace(/</g,"\\u003c")}}/><a className="skip-link" href="#services">Skip the journey — explore our services</a>{children}</body></html>;}

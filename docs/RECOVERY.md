# IP NET website recovery

## Initial recovery state

The initial checkout contained the legacy `index11 (1).html` and repository
history. The later Next.js app, authored assets, quality renders and review ZIPs
had not been committed and were absent. Those old artifacts must not be reported
as recovered or published. The site was subsequently rebuilt from the recovered
brief and confirmed business information; the owner does not need to locate ZIPs.

The user's original 23,505-byte POC brief was recovered from their uploaded
attachment and is preserved beside this document. Its placeholder-first scope
has been superseded by the latest rendering decision below.

## Current approved direction

Continue here; the user does not want a Claude handoff. Finish an English website
for IP NET SECURITY & LOCKSMITH. The user selected realism-first: an offline
rendered 3D camera journey controlled by scroll, with interactive HTML overlays,
navigation and contacts. Use actual 3D scene renders rather than presenting an
AI concept image as implemented work. First demonstrate a short entrance/lobby
sequence, then complete the full story. The full rendered sequence was not
finished before the working files became unavailable.

Retain the continuous, reversible sequence: exterior, CCTV, video intercom,
access reader and physically opening door, lobby, behind-wall cable reveal,
network rack, wireless AP, locksmith hardware, exterior pullback and contact.
Prior code used Next.js/TypeScript/React Three Fiber/Three.js/GSAP, a centralized
0–1 progress clock, camera waypoints and semantic HTML. The build was a static
export. A Blender Cycles plus Open Image Denoise study was tested, but those
scripts and assets also need recovery or reimplementation.

## Confirmed business information

- Name: IP NET SECURITY & LOCKSMITH (visual wordmark previously IP.NET).
- Customer-facing language: English; communicate with the owner in Hebrew.
- Telephone and WhatsApp: +19175310595 / 917-531-0595.
- Email: ipnet.security@gmail.com.
- Domain: ipnetsecurity.com, managed at Namecheap. No hosting access is supplied.
- NYC: all five boroughs.
- Northern NJ: Bergen, Hudson, Essex, Passaic and Morris counties.
- Westchester: Yonkers, White Plains and surrounding towns.
- Services: CCTV/IP cameras, intercom, access control, Wi-Fi/APs, networking,
  structured cabling, racks/cabinets, diagnostics/repairs/upgrades/maintenance,
  door hardware and residential/commercial/automotive locksmith.
- 24/7 applies only to emergency locksmith.
- Exclude alarms and garage-door automation.
- Slogans: One team. Total security.; Get connected. Stay protected.;
  One company. One point of contact. Complete solution.
- No invented reviews, addresses, licences, clients, projects, statistics,
  response times, manufacturer partnerships or IP.NET-owned building.

## Recovery and preservation

The new source is on `codex/rendered-site-recovery`. Remote backup was verified
by comparing local HEAD with the remote branch after pushing. The rebuilt app
uses the chosen rendered film and interactive HTML; the previous realtime
Three.js prototype is not its runtime. Consult the current README and render
manifest for the new implementation and frame-completion status.

Historical source archives previously supplied to the user:
`IP-NET-Claude-Code-Handoff.zip` or `IP-NET-NextJS-Project.zip`.
These archives predate some later model/render improvements, so validate their
contents and restore the actual baseline without claiming they include every
later change. Preserve the legacy file and inspect before extracting.

After changes, build and check the source, commit the working implementation
and verify a remote backup before relying on environment files. Provide source
and review downloads as additional backups. A local commit alone is not proof
that GitHub contains the work.

Namecheap DNS, hosting, HTTPS and actual contact delivery have not been
connected/verified. Earlier contact UI prepared email/WhatsApp drafts; it did
not have an automatic submission backend. Avoid claiming public deployment or
lead delivery from a local build.

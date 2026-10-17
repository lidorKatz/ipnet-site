# IP NET SECURITY & LOCKSMITH

English business website for NYC, Northern New Jersey and Westchester. The
interactive building journey is an original illustrative property, rendered
offline in Blender. It is not a photograph of a customer installation.

## Develop

Use Node 24 and npm 11 with the committed lockfile:

```sh
npm ci --cache /tmp/ipnet-npm-cache --no-audit --no-fund
npm run dev -- --port 3000
```

`npm run typecheck` checks TypeScript. `npm run build` verifies all 120 rendered
frames and their checksums, then exports the site to `out/`. `npm start` serves
that export on port 3000. No application server or database is required in
production. Raw authoring PNGs are excluded from the export. Fonts and journey imagery are hosted with the site.

The release build deliberately fails if the rendered film is incomplete.
`IPNET_ALLOW_PARTIAL=1 npm run build` is an explicitly incomplete authoring build,
not a release. Do not use it for deployment.

## Author the 3D film

Requires Blender 4.3+, Python 3 with Pillow, and the checksum-verified OIDN tool:

```sh
python3 scripts/install-render-tools.py
npm run assets:render -- --width 960 --samples 16 --resume --save-blend
npm run assets:prepare
npm run build
npm run preview:build
```

The renderer builds the property, materials, equipment, camera and physical
door animation from source. `config/journey.json` controls camera waypoints,
chapters and copy. It renders representative shots first for early inspection,
then the rest. Resume reuses frames only when source, sample count, dimensions
and progress match. Do not change scene source during a render.

Raw PNGs and denoising intermediates are regenerable and ignored. Optimized
WebP frames, their integrity manifest, authoring source and fonts belong in Git.
Only rerender after visual/source changes; ordinary development uses those
committed assets without installing Blender or OIDN.
Preparation can also recover verified committed WebP frames without their raw
PNG cache and merge newly rendered ranges. It reuses them only when source and
checksums match. A changed scene needs a consistent new sequence.

`preview/IP-NET-Website-Review.html` is a self-contained offline review of the
actual application, including fonts and frames. It is generated, not an alternate
design. Open it in a browser; its phone, email and WhatsApp links are real.

## Contact behavior

Confirmed public details live in `config/brand.ts`. The inquiry form validates
and prepares a message, then lets the visitor choose their email app or
WhatsApp and send it. It does not claim a message was submitted to a backend.
24/7 wording applies only to emergency locksmith work.

The optional public `NEXT_PUBLIC_BUSINESS_PHONE` overrides the confirmed number
at build time. An explicitly blank or invalid value hides phone/WhatsApp links.
No secret is needed to build or use the current contact flow.

After committing the finished source and assets, run
`python3 scripts/package-delivery.py` to create source, static-site and holding-page
ZIPs plus the standalone review in `delivery/`. The packager refuses incomplete
frames, stale exported assets or uncommitted source.
Packaging also uses FFmpeg to create a short scene-only MP4 review.

Browser checks against a running export use
`node scripts/browser-check.cjs http://127.0.0.1:3000`; after generating the review,
`node scripts/check-offline.cjs` tests it with network requests blocked. Playwright
and Chromium are installed in the cloud machine; elsewhere set `PLAYWRIGHT_MODULE`
and `CHROMIUM_PATH` to installed equivalents.

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for domain and hosting instructions and
[RECOVERY.md](docs/RECOVERY.md) for the confirmed brief and recovery history.

## Preserve work

Commit source and authored assets on the feature branch. Push and compare the
remote branch hash with local HEAD before describing the work as backed up.
Do not rely on an untracked file, a local commit or an ephemeral preview URL.
Keep the original `index11 (1).html` unchanged as the legacy reference.

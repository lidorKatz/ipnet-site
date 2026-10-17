# Verified in the cloud — 17 October 2026

The current release candidate uses 120 genuine Blender Cycles renders at
960 × 640, with a 1200 × 800 exterior poster. The optimized film assets total
2,271,406 bytes. The original scene and renderer are included in source.

Passed:

- Frozen `npm ci` installation using the committed lockfile.
- TypeScript check and strict production static-export build, with all 120
  frame checksums and exact sequence positions verified. No partial-build bypass.
- Functional Chromium checks across all ten chapters, including actual drawn
  frame selection, reverse scrolling and the bounded image cache.
- Equipment detail panels, mobile navigation, inquiry validation, message
  preparation/editing, and the confirmed call/email/WhatsApp link destinations.
- Layout checks at widths 320, 390, 768 and 1440 pixels, reduced-motion behavior,
  and a short static-poster fallback when JavaScript is disabled.
- Self-contained HTML review with all 120 frames embedded, forward/reverse
  navigation and zero external network requests.
- Recovery of all 120 committed WebP frames without raw PNG caches. Corrupted
  frames and a changed scene source were rejected rather than relabeled current.
- Editable Blender scene reopened successfully with its used display textures
  packed. Camera motion and animated states are driven by the accompanying script.
- Temporary holding page at phone and desktop widths with confirmed contact links.

Node 24.19.0, npm 11.9.0, Blender 4.3.2, FFmpeg 7.1.5 and system Chromium were
available in the tested machine. Normal website builds do not require Blender
or the external denoiser; the authored WebP assets are committed.

Limits:

- Chromium viewport emulation is not a physical iPhone/Android/Safari test.
- The form prepares an email or WhatsApp draft; the visitor reviews and sends it.
  These checks did not send messages or establish an automatic delivery backend.
- The building is an illustrative original 3D property, not client photography.
  Visual acceptance is separate from passing functional checks.
- Public hosting, Namecheap DNS, live HTTPS and real-device contact handoff have
  not been verified. Domain HTTPS checks from this cloud were blocked at the
  network proxy; that does not establish the absence of an existing host.

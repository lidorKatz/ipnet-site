# Project instructions

Read relevant installed Next guides under node_modules/next/dist/docs/ before
framework edits. Keep the original legacy HTML unchanged.

The user chose a rendered 3D journey with interactive HTML. Do not describe an
AI concept image as a finished 3D environment or a local build as a deployment.
Customer copy is English; communicate with the owner in Hebrew.

Preserve source and authored assets in Git, provide a source archive and verify
remote backup status. Local commits are not evidence of a successful push.
Never leave completed application source untracked between turns.

Business facts and the recovered original brief are in docs/. The latest user
direction takes precedence over its procedural-placeholder implementation phase.

<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->

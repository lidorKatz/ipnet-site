# Hosting and domain

Confirmed domain: **ipnetsecurity.com**, managed at **Namecheap**.
Owning the domain does not establish that a hosting account exists. No hosting
provider, live deployment or DNS change is confirmed by this repository.

## Review before publishing

1. Run `npm run typecheck`, `npm run build`, and `npm run preview:build`.
2. Check the building journey forward and backward, phone layout, menu, and
   inquiry review/edit flow. Test phone, email and WhatsApp on a real phone.
3. Review the actual business copy and illustrative scene. No customer work,
   testimonials, licensing claims or response-time guarantees are fabricated.

## Static hosting

The production folder is `out/`. It can be deployed to a static host such as
Netlify or Cloudflare Pages. A simple first release can use a manual upload of
the folder; a connected repository can build with `npm ci && npm run build`
and publish `out` using Node 24.

Use the provider's temporary HTTPS deployment address for final review before
connecting the domain. Deploying this repository is a separate action from
publishing the Codex development environment.

## Namecheap connection

After the host has created a real site:

1. Add `ipnetsecurity.com` and `www.ipnetsecurity.com` in the hosting dashboard.
2. Copy the exact DNS records the provider gives for this specific site.
3. In Namecheap, open Domain List → Manage → Advanced DNS. Update only the
   relevant website records. Preserve email/MX/TXT records and unrelated records.
4. Set the canonical domain to `https://ipnetsecurity.com`, redirect `www` to it,
   enable HTTPS and verify both addresses from outside this workspace.
5. Check calls, WhatsApp and email on the deployed site and a physical phone.

Do not guess IP addresses, CNAME targets or nameservers. Do not share Namecheap
passwords or hosting tokens in chat. A browser login or the provider's supported
integration can be used when the owner is ready to publish.

## Temporary holding page

`holding/index.html` is an independent English coming-soon page with the confirmed
business services and direct contact links. Upload that folder instead of `out/`
if a temporary page is desired. It requires the same hosting and domain setup.

## Limits

The current form opens a prepared email or WhatsApp draft. For an on-site
submission confirmation and automatic delivery, connect and verify an actual
form service before changing the success copy. No analytics, tracking cookies
or customer database are part of this build.

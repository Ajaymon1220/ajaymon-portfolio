# Dave Miye reference replica

A standalone static capture of https://davemiye.com/ made at the user's request on 4 November 2026. Includes the homepage, playground with 91 pieces, and Goals, Circa, SideQuest, PLATE and DialMe project pages. Original content, identity, images, fonts, CSS and browser interaction bundles are retained.

## Run

`npm run dev` serves http://127.0.0.1:5174.

`npm run check` validates JavaScript syntax and local HTML/CSS asset references.

The deployable site is `dist/`; no dependency installation or build is required. This is a captured production bundle, not the original editable React source project. The existing Ajay portfolio in the parent directory is untouched.

## Static hosting adaptations

- Image sources and public media/fonts are localized, bypassing Next.js image optimization.
- Page-to-page links use full navigation because the original Next.js server is unavailable.
- Contact retains the original email-app fallback and original contact address; no message submission backend is included.
- External booking and social links retain their original destinations.
- `capture.py` and `prepare.py` document capture and adaptation. Do not run them over an edited build without backing it up.

## Verification

All seven pages, 22 JavaScript files and local HTML/CSS asset references pass checks. Desktop Chrome checks verified the homepage rendering, changing greeting, theme toggle, playground navigation and video lightbox. Exhaustive mobile and interaction parity remains unverified.

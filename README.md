# Ajaymon portfolio site

The served site is `dist/`: a static Next.js build whose pages are generated from Ajaymon's own content. The layout and interactions came from a captured site; every project, image, case study, playground piece and metadata field has been replaced with Ajaymon's work.

## Editing content

1. Edit `site_content.py`: the five case studies (`PROJECTS`) and playground tiles (`PLAYGROUND`).
2. Put any new source images in `assets/`.
3. Run `python3 build_ajay.py`, then `npm run check`.

`build_ajay.py` rewrites the homepage project rail, playground dial, playground grid and the five `/work/<slug>` pages from `templates/`. For each page it writes the server HTML and the matching React hydration payload, so text must come from `site_content.py`, not from hand edits to `dist/`. The build is idempotent: running it twice produces identical files.

Homepage text that isn't project-related (intro bio, experience, "How I work" notes, logos) lives directly in `templates/home.html`.

## Your art

The avatar (hero, preloader, playground "d", contact chat) is now an interactive sprite mascot. Its component lives in `dist/mascot.js`, and its two aligned 3×3 sprite sheets live in `dist/profile/mascot/directions.png` and `reactions.png`. Replace those sheets together to update the likeness. It follows fine pointers, reacts to click/tap/keyboard, and disables gaze tracking for reduced motion.

The footer illustration remains an image slot:

- `dist/profile/art/footer-scene.svg`: 620 × 322, full footer width up to 46rem

Replace the footer file with your own drawing (SVG or PNG with the same name). No rebuild is needed, and the build never overwrites them.

## Contact notes

The "Or leave me a note" form emails `CONTACT_EMAIL` (in `site_content.py`) through formsubmit.co. The first note ever sent triggers a one-time FormSubmit activation email to that address, and notes are delivered once you click its confirm link. Hidden-field and too-fast (under 3s) submissions are dropped as spam. If delivery fails, the form falls back to opening the visitor's email app.

## Mobile

Phone-only refinements are appended to `dist/personalize.css` by the build (`MOBILE_CSS` in `build_ajay.py`), inside `@media (max-width:767px)`. Desktop styles are untouched.

## Removed from the capture

- Third-party analytics (Microsoft Clarity, Vercel Analytics) and the live CMS connection.
- The original author's projects, playground pieces, images (`media-cdn/`), testimonial, structured data, canonical URLs and social links.

`capture.py`, `prepare.py` and `personalize.py` are the original capture tools. Don't run them: they would download the original site over `dist/`.

## Run

From the repository root: `npm run dev` (http://127.0.0.1:5173), `npm run check`, `npm run build`.

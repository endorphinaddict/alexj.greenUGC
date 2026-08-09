# UGC creator site

Static HTML/CSS/JS. No build step, no dependencies, no framework. Open `index.html` in a
browser to preview locally — that's it.

```
index.html    Home: hero, hook ticker, selected work, packages, about, contact
work.html     Full portfolio grid with category filters
rates.html    Packages, deliverables, usage terms, FAQ
styles.css    All styling and design tokens
main.js       Mobile nav, work filter, footer year
```

---

## Replace before you deploy

Find-and-replace across all three HTML files:

| Placeholder | Replace with |
|---|---|
| `hello@yourdomain.com` | your real inbox |
| `yourhandle` | your Instagram / TikTok / Facebook handle |
| `YOUR_FORM_ID` | your Formspree form ID (see below) |
| `ALEX` (wordmark) | your name as you want it on the site |

Also worth a pass:

- **Prices** (`$250` / `$850` / `$1,600`) are placeholders to make the layout real. Set your
  own based on what auto-care brands in your lane actually pay.
- **Turnaround** ("5–7 days") — change to whatever you can actually hit.
- **Stats** in the hero (60K / 40K / 3 yrs) are yours, but update them as they grow.
- **Hooks** in the ticker and on the frames — swap in your actual opening lines as you post.

## Contact form

The form posts to Formspree. Sign up free at formspree.io, create a form, and paste the ID
into the `action` attribute in `index.html`. Until you do, the form won't send — the mailto
link right beside it still works, so the page is never broken.

If you'd rather skip it entirely, delete the `<form>` block. Email plus DMs is a perfectly
normal way for brands to reach a creator.

## Adding real thumbnails

Each work card is designed to look finished without an image. To add one, drop the file in an
`assets/` folder and uncomment the `<img>` line inside that card:

```html
<img class="frame__media" src="assets/thumb-01.jpg" alt="">
```

Export a frame from the video at 1080×1920. The scrim on top keeps the hook text readable, so
you don't need to pick a dark frame.

## Design tokens

Everything lives in `:root` at the top of `styles.css`.

| Token | Value | Used for |
|---|---|---|
| `--sun` | `#F4C445` | hero, contact band, accents |
| `--ink` | `#141210` | type, borders, ticker background |
| `--shell` | `#FAF7F2` | page background |
| `--asphalt` | `#241F1B` | work sections |
| `--signal` | `#1F5CFF` | links, hover states, prices |
| `--mute` | `#8A8175` | secondary text |

Change `--sun` and `--signal` to reskin the whole site.

## Notes

- Responsive down to small phones; the work grid reflows to two columns.
- The hook ticker pauses on hover and stops entirely for anyone with reduced-motion turned on.
- Keyboard focus is visible throughout.
- Fonts load from Google Fonts. If you'd rather have zero external requests, delete the two
  `<link>` tags for fonts — the system-font fallbacks in `styles.css` will take over.

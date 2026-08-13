# alexj.green — UGC creator site

Static HTML/CSS/JS. No build step, no dependencies, no framework. Open `index.html` in a
browser to preview locally — that's it.

Live at **https://endorphinaddict.github.io/alexj.greenUGC/** via GitHub Pages, deployed from
`main` on every push.

```
index.html    Single page: hero, hook ticker, work, services, about, contact
styles.css    All styling and design tokens
main.js       Mobile nav, footer year
assets/       Reel cover images (reel-01.jpg … reel-04.jpg + demo-supplement.mp4, ranked by views)
```

## The work section

Five cards, ranked by real Instagram view count, each linking to its reel. Cover images live
in `assets/` and are named by rank, so the order on the page matches the filenames.

Instagram's oEmbed/embed endpoint returns HTTP 503, so embedded players don't work — the
cards link out instead. Don't reach for `embed.js`; it was tried and removed.

### Updating the lineup

When a new reel outperforms one on the page:

1. Grab its cover: `https://www.instagram.com/p/SHORTCODE/media/?size=l` (returns a 720×1280
   JPEG). The shortcode is the `/reel/SHORTCODE/` part of the post URL.
2. Save it into `assets/` at the rank it belongs, renumbering the others.
3. Update the `href`, `alt`, and view count in that card in `index.html`.

Cards are designed to still look finished if an image is ever missing — the scrim and the
rank badge carry it.

## Contact

Email and social handles appear in the contact section and the footer. There's no form; the
mailto link and DMs are the only routes in, which is normal for a creator site.

## Design tokens

Everything lives in `:root` at the top of `styles.css`.

| Token | Value | Used for |
|---|---|---|
| `--sun` | `#F4C445` | hero, contact band, accents |
| `--ink` | `#141210` | type, borders, ticker background |
| `--shell` | `#FAF7F2` | page background |
| `--asphalt` | `#241F1B` | work section |
| `--signal` | `#1F5CFF` | links, hover states |
| `--mute` | `#8A8175` | secondary text |

Change `--sun` and `--signal` to reskin the whole site.

## Notes

- Responsive down to small phones; the work grid reflows to two columns.
- The hook ticker pauses on hover and stops entirely for anyone with reduced-motion turned on.
- Keyboard focus is visible throughout.
- Fonts load from Google Fonts. To go fully self-contained, delete the two `<link>` tags for
  fonts — the system-font fallbacks in `styles.css` take over.

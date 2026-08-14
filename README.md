# Alexander Williams — UGC creator site

Static HTML/CSS/JS. No build step, no dependencies, no framework. Open `index.html` in a
browser to preview locally — that's it.

Live at **https://endorphinaddict.github.io/alexj.greenUGC/** via GitHub Pages, deployed from
`main` on every push.

```
index.html    Single page: hero, work, services, about, contact
styles.css    All styling and design tokens
main.js       Mobile nav, footer year
assets/       reel-01…04.jpg (cover art) + demo-supplement.mp4/.jpg (self-hosted clip)
```

## The work section

Five 9:16 cards. The first four are Instagram reels ordered by real view count, each linking
to its post. The fifth is a self-hosted video that plays inline.

Instagram's oEmbed/embed endpoint returns HTTP 503, so embedded players do not work — the
reel cards link out instead. Don't reach for `embed.js`; it was tried and removed.

### Updating the lineup

When a new reel outperforms one on the page:

1. Grab its cover: `https://www.instagram.com/p/SHORTCODE/media/?size=l` (returns a 720×1280
   JPEG). The shortcode is the `/reel/SHORTCODE/` part of the post URL.
2. Save it into `assets/` at the rank it belongs, renumbering the others.
3. Update the `href`, `alt`, and view count in that card in `index.html`.

Cards still look finished if an image is ever missing — the scrim and rank badge carry it.

### Adding or replacing the self-hosted video

Phone footage is far too large to ship as-is, and GitHub rejects any file over 100MB:

```
ffmpeg -i SOURCE.MOV -vf "scale=1080:-2" -c:v libx264 -preset medium -crf 28 \
  -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart assets/demo-supplement.mp4
```

`+faststart` puts the `moov` atom ahead of the data so the clip streams instead of waiting on
a full download. Pull the poster from a frame where the product is in shot:
`ffmpeg -ss 8 -i assets/demo-supplement.mp4 -frames:v 1 -vf scale=540:-2 -q:v 4 assets/demo-supplement.jpg`.

Two traps, both hit once already:

- **Don't add `loading="lazy"`** to the work images. The trigger did not fire for this
  section and the covers silently never loaded.
- **Don't horizontally flip the demo.** It was shot on the front camera, so the shirt logo and
  tub label read backwards — but the captions were added in editing and read correctly. A flip
  fixes the objects and breaks the captions, which are the selling copy. If both must be
  right, re-export from CapCut with the clip flipped *before* the captions are laid on.

When you overwrite a file without renaming it, bump the `?v=` on its reference in
`index.html`, or browsers will keep serving the old one.

## Contact

Email and social handles appear in the contact section and the footer. There's no form; the
mailto link and DMs are the only routes in, which is normal for a creator site.

## Design tokens

Everything lives in `:root` at the top of `styles.css`. The site is dark — near-black page,
blue accents.

| Token | Value | Used for |
|---|---|---|
| `--sun` | `#1D4ED8` | filled blue surfaces: hero, contact band, badges |
| `--signal` | `#6EA0FF` | blue drawn on black: links, view counts, hovers |
| `--ink` | `#0A0B0E` | page background, masthead, footer, buttons |
| `--shell` | `#EDF0F6` | text on dark, borders |
| `--asphalt` | `#111318` | work section surface |
| `--asphalt-2` | `#181B22` | card surface |
| `--mute` | `#8C93A6` | secondary text |

The two blues are not interchangeable. `--sun` is a background that always carries white
text; `--signal` is for blue drawn *on* black, where `--sun` sinks into it. Swapping them
produces unreadable text either way.

`--edge` is a translucent light border. Anything defined as a dark border disappears against
the black page.

## Notes

- Responsive down to small phones; the work grid reflows to two columns.
- Keyboard focus is visible throughout.
- Fonts load from Google Fonts. To go fully self-contained, delete the two `<link>` tags for
  fonts — the system-font fallbacks in `styles.css` take over.

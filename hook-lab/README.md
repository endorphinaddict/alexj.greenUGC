# Hook Lab

Offline UGC hook + script generator. Open `index.html` in a browser. No build, no dependencies.

Built on the Hook → Problem → Solution → CTA framework:

- **Hook**: names a specific audience, evokes an emotion, and comes with a visual direction.
- **Problem / Solution / CTA**: "Full script" on any hook expands it into all four parts, with
  what to say, what to show, and the on-screen text. CTA follows the offer you pick (restock, sale, etc.).

## Using it

1. Enter the product and pick a category. Categories preload audience, problem, result and B-roll ideas.
2. Tap chips (or type one per line) to choose audience / problem / result. Empty fields fall back to category defaults.
3. Optionally pick hook styles, then **Generate**. Reroll, save favourites (kept in this browser), and copy.

## Extending

All content lives in `data.js`:

- `CATEGORIES`: add a product category (audiences, pains, benefits as noun phrases, B-roll ideas).
- `HOOK_TYPES`: emotion and visual direction per hook style.
- `TEMPLATES`: hook lines. Tokens: `{audience} {pain} {benefit} {product} {noun}`; `{Audience}` capitalises.
  Audiences must be plural groups and pains/benefits noun phrases, or the grammar breaks.
- `PROBLEMS` / `SOLUTIONS` / `CTAS`: script parts.

Note: this folder is served by GitHub Pages with the rest of the site (`/hook-lab/`, marked `noindex`, not linked).

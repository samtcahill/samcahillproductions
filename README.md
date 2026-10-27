# samcahillproductions.com

Portfolio site for Sam Cahill: director, DoP, editor and photographer.

A single static page (`index.html`) served by GitHub Pages at https://samcahillproductions.com.

- Projects, featured order, gear and bio live in the `<script>` near the bottom of `index.html` (`W`, `TOP`, `GEAR`, `about()`).
- `media/reel-loop.mp4`: short silent reel cut that plays behind the homepage header (falls back to a still until it's added).
- `images/portrait.jpg`: About page photo (set `PORTRAIT` in `index.html` once added).

## Per-video pages (SEO)

`work/<slug>/index.html`, `sitemap.xml` and `robots.txt` are generated from `index.html`.
After any edit to `index.html`, run `python3 build_pages.py` and commit the results.

# badge.rs

Badger, badger, badger ... a snake! The front page of [badge.rs](https://badge.rs/): a row
of dancing badgers and a snake on a hoverboard, all of them Badge.Team's own mascots.
Clicking anywhere goes to [badge.team](https://badge.team/). With love to Weebl's badgers.

Plain HTML, CSS and a canvas script, no libraries, nothing inline (the server's CSP is
`default-src 'self'`). Without script, or with reduced motion, the two of them stand still.

- `index.html`, `badge.css`, `badge.js`: the page.
- `badger.webp`, `snake.webp`: made by `tools/sprites.py` from Badge.Team's
  `konsool_mascots.svg`.
- `.htaccess`: the security headers.

Deploy: copy the files to the web root. No build step.

## Licence

The code is MIT, the badger and snake are by Stichting Badge.Team under CC BY 4.0; see
`REUSE.toml` and `LICENSES/`.

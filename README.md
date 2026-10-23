# Gerard Klijs's blog

A static site built with [vados](https://github.com/gklijs/vados), served at blog.gklijs.tech.

## Content

- `root/` -- the source tree: `main.json`, `menu.json`, and one `page.json` per page directory. A post is a
  directory under its section and year (`root/tech/2026/<slug>/`) with a `page.json` whose `content` names a `post.md` next to it.
- `imgroot/` -- the image tree: one `images.json` per directory of images to publish. Photos live in
  `imgroot/photos/`, resized to 2400 px wide with their metadata stripped (vados's largest variant is 1972 px), and each
  has a page under `root/photos/<year>/<slug>/` with the photo as its `image`.
- `year_cards.py` -- rebuilds each year page's post cards, the section's "Latest" link and the home page's latest posts
  from the posts' own `page.json`; run it after adding a post. Give the newest post the lowest `order`.
- `sass/main.scss` -- overrides Bulma's variables before importing the parts of it the site uses; rebuilt by
  `npm run build` into `public/css/main.min.css`.
- `icons.mjs` -- run by `npm run icons` after `vados generate`: publishes a subset of the Material Design Icons font
  with only the icons the generated pages use, `public/css/icons.css` for them, and the font's license and notice, with
  the full Apache-2.0 text from `licenses/`.

## Local development

```
cargo install vados
npm install
npm run build
vados check --source root --img-source imgroot
vados generate --source root --img-source imgroot --destination public
npm run icons
python3 serve.py
```

## Deployment

Deploys to [Netlify](https://www.netlify.com/): connect the repository and `netlify.toml` installs Rust, `vados`, the Sass
build and the icon subset.

## Copyright

The posts and photos are © Gerard Klijs (gklijs.tech, KvK 92872697), all rights reserved.

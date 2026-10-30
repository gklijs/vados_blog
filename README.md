# Gerard Klijs's blog

A static site built with [vados](https://github.com/gklijs/vados), served at blog.gklijs.tech.

## Content

- `root/` -- the source tree: `main.json`, `menu.json`, and one `page.json` per page directory. A post is a
  directory under its section and year (`root/tech/2026/<slug>/`) with a `page.json` whose `content` names a `post.md` next to it.
- `imgroot/` -- the image tree: one `images.json` per directory of images to publish. Photos live in
  `imgroot/photos/`, resized to 2400 px wide with their metadata stripped (vados's largest variant is 1972 px), and each
  has a page under `root/photos/<year>/<slug>/` with the photo as its `image`.
- Posts carry a `date` in their `page.json`; `tech/` and `tech/2026/` list them newest first (`childOrder: dateDesc`),
  the home page and `tech/` show the latest ones (`latest`), and `tech/2026/` publishes an Atom feed at `/tech/2026/feed.xml`.
- Posts and page text are written in British English (colour, recognise, optimising); code and identifiers keep their usual spelling.
- `sass/main.scss` -- overrides Bulma's variables before importing the parts of it the site uses; rebuilt by
  `npm run build` into `public/css/main.min.css`.

## Local development

```
cargo install vados
npm install
npm run build
vados check --source root --img-source imgroot
vados generate --source root --img-source imgroot --destination public
```

## Deployment

Deploys to [Netlify](https://www.netlify.com/): connect the repository and `netlify.toml` installs Rust, `vados`, the Sass
build.

## Copyright

The posts and photos are © Gerard Klijs (gklijs.tech, KvK 92872697), all rights reserved.

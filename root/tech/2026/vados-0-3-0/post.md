Three weeks ago I wrote that vados finally had a command line. Since then there have been two releases, 0.2.0 and now **0.3.0**, and the second one is the one that made this blog simpler instead of just bigger.

Before the release I did a dry run: I built the unreleased code and generated this blog with it next to the old version, then compared the output. That turned up a surprise in my own setup. Half of what the blog needed from scripts around vados is now vados's job, so those scripts are gone.

## Writing a blog

A page can now have a `date`, and a section can list its pages by it with `childOrder: dateDesc`. A new post shows up first without renumbering anything. Until now I gave the newest post the lowest `order` and ran a Python script to rebuild the cards on the year page and the home page. That script is deleted. The home page now just says `"latest": { "from": "/tech", "limit": 4 }`, and a page can show the newest dated pages from anywhere on the site.

The same dates drive **Atom feeds**. Set `"feed": true` on a section and vados publishes `feed.xml` with every post's summary and full content. For now a feed lists only the direct children of the page it is on. On this blog the posts sit one level down, under the year, so the feed lives at [/tech/2026/feed.xml](/tech/2026/feed.xml). I'd like it to look deeper, as `latest` already does.

## Being found

- Link previews: `og:` and Twitter tags, canonical URLs, and a 1200×630 JPEG crop of the page's image, because LinkedIn doesn't reliably show WebP.
- `sitemap.xml` and `robots.txt`, structured data for search engines, and the `rel="me"` and `fediverse:creator` tags Mastodon uses to verify you and credit you under a link.
- Every title now ends with the site's name, and every page has a proper `<h1>`.

Most of this needs one new line in `main.json`, the `siteUrl`, which is also why `vados check` now warns when it's missing.

## Faster pages

Icons used to come from the Material Design Icons web font: about 400 KB of render-blocking CSS and font for a handful of icons. In 0.3.0 they're inlined as SVG. This blog used to run a Node script after every build to cut that font down to the icons I used. That script is gone as well. The hero image is fetched early, every `<img>` has its dimensions, and on phones the tiles and social icons no longer fight over the same space.

Code blocks in Markdown are highlighted at build time now too, with a small stylesheet that is only linked on pages that have code.

## Between 0.1.0 and here

0.2.0 added a site description and a favicon, and the text vados puts on every page (skip link, navigation labels) now follows the site's language: English, Dutch, German, French or Spanish. It also fixed the breadcrumb announcing "page" instead of the page's title.

```sh
cargo install vados
```

- crates.io: [vados](https://crates.io/crates/vados)
- GitHub: [gklijs/vados](https://github.com/gklijs/vados), with the full [changelog](https://github.com/gklijs/vados/blob/main/CHANGELOG.md)

If you read this blog in a feed reader, you can now subscribe. That was the last thing it was missing.

*This blog is built with vados, too, and now with 0.3.0.*

*Photo: [Fort in the grass](/photos/2026/fort-in-the-grass), by me. Thick walls, small windows and nothing running inside: roughly what I want from a static site, too.*

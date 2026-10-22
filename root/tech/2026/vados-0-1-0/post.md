*Originally posted on LinkedIn on 7 October 2026.*

Four years ago I published vados 0.0.3 to crates.io. It was a static site generator you couldn't actually run, because I'd only shipped the library. No binary. Just vibes.

Today I'm fixing that with **vados 0.1.0**.

Some background: the project's built around Bulma (the CSS framework), and Bulma is also a Dragon Ball character. So I went looking for the fastest Dragon Ball character and found Vados, who can destroy and recreate entire planets. Turns out that's basically what a static site generator does to your output folder every build. Naming things is hard, so I let anime do it.

What's new:

- `vados init` sets up a new site, ready to deploy on Netlify.
- `vados check` tells you everything that's wrong with your site before your visitors do.
- Commands to add pages, images, menu items and social links without hand-editing JSON. My favourite kind of JSON is the kind I don't type.
- Accessibility built in: skip links, landmarks, labels on every icon button, and alt text is required, not optional.
- Luma integration, so you can embed an event or a register button on a page. I built this before I even had a Luma account, which is definitely the right order to do things in.

It's still very much a scratch-my-own-itch project, so I mostly only add what I'd use myself. But if you like Markdown, Bulma and sites that just work without a big framework behind them, give it a try:

```sh
cargo install vados
```

- crates.io: [vados](https://crates.io/crates/vados)
- GitHub: [gklijs/vados](https://github.com/gklijs/vados)

Next up: actually registering at Luma.

*This blog is built with vados, too.*

*Photo: [Batman, up close](/photos/2026/batman-up-close), by me.*

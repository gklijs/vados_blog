This morning I walked through the Bossche Broek, which is very close to home. It was grey and quiet, with a pheasant, a heron and a group of geese for company. The photo at the top is from that walk.

Two releases came out just before the weekend: [skilj](https://github.com/gklijs/SkilJ) 0.4.0 on Friday and [vados](https://github.com/gklijs/vados) 0.6.0 yesterday.

## vados 0.6.0

The part I'm happiest with is that a vados site can now serve agents. With `"markdown": true` in `main.json`, every page gets a Markdown version next to its HTML: `/blog/post` also exists as `/blog/post.md`, and the home page as `/index.md`. Each HTML page points to it with a `rel="alternate"` link of type `text/markdown`.

I got the idea from the episode of [The Changelog](https://changelog.com/podcast) with Zeno Rocha of Resend, about building for agents. More and more of the readers of a page are not people, and an agent has little use for a navbar, a footer and a few hundred class names. The Markdown version has the title, the dates, the hero image with its description, the content, and the listings of child pages and latest posts. Navigation, scripts and embedded frames are left out. It is off by default, and vados doesn't generate an `/llms.txt`.

In the [0.5.0 post](/tech/2026/vados-0-5-0-skilj-0-3-0) two things were still open. One of them is done:

- **Menu entries can be changed and removed.** `menu update-item` and `menu remove-item` select an entry by a part of its URL. An update keeps the fields you leave out, and can move the entry with `--position`.

Embedding a Luma calendar as a whole is still open.

Other things turned up as well:

- **Faster builds.** Images, pages and minification are processed in parallel. `generate --jobs N` limits the workers, and the warnings keep their order.
- **Ready-made Linux binaries** for x86_64 and aarch64, statically linked and with a checksum. `cargo binstall vados` finds them.
- **JSON Schemas** for `main.json`, `menu.json`, `page.json` and `images.json`, so an editor completes the keys and flags mistakes while you type.
- **`check` warns about unknown keys**, with a suggestion when it looks like a typo.
- **Mermaid diagrams** from fenced `mermaid` blocks, loaded only on the pages that have one.
- **19 more social providers**, including Bluesky, Instagram and email.
- **`generate` cleans up after itself.** Files from an earlier run that are no longer needed are removed, a replaced image gets new variants, and a failure is reported with its path instead of a panic.

### What it took here

- Netlify no longer installs Rust to compile vados. It downloads the release binary and checks it against the checksum, and the version is one line, `VADOS_VERSION`, in `netlify.toml`. The plugin that cached the Rust toolchain between builds is gone.
- `"markdown": true` in `main.json`, and a header in `netlify.toml` that serves `.md` files as `text/markdown`. So this post is also at [/tech/2026/vados-0-6-0-skilj-0-4-0.md](/tech/2026/vados-0-6-0-skilj-0-4-0.md).

## skilj 0.4.0

This is a breaking release again, with upgrade notes at the top of the [changelog](https://github.com/gklijs/SkilJ/blob/main/CHANGELOG.md). Every 0.3 instance has to stop before the first 0.4 instance starts. The first start also replaces protected external source content with `[redacted]`, under a lock that blocks event writes.

What I'm happiest with are the performance improvements, and that they will keep being checked:

- **Appending no longer slows down with the number of tags.** The trigger that indexes an event's tags scanned the whole tag dictionary for every inserted event. Loading 200,000 events into a bounded context with 10,000 tags went from 451 to 8,762 events per second, and with 55,000 tags from 98 to 7,958.
- **Key rotation works in batches.** Moving a bounded context's data keys to another key asks each key once per batch of 200, instead of twice per data key. With Vault Transit, 1,000 data keys at 5 ms a request move in 0.12 seconds instead of 13.
- **Less copying.** Preparing a batch of commands moves the resolved histories and snapshot states into the queue instead of copying them.

A number from one afternoon says little about next month. So there is now a script that builds the benchmarks of two commits, runs them in alternating trials and reports the raw samples with their spread. A weekly workflow runs that comparison against a durable Postgres. The model-based tests also run every week, with 200 concurrent groups, to check that concurrent commands answer as some serial order would.

The rest is mostly about upgrading and about agents:

- **An upgrade preflight.** It reports what starting this release would change in a database, without changing it: pending migrations, missing columns and indexes, and which patches rewrite rows or block writes.
- **A schema compatibility level.** A release records which older releases may keep running against the schema it upgraded, and an older one refuses with `schema_too_new`.
- **Guides for coding agents ship inside the crate**, so a project has the ones written for its skilj version. Claude Code and Codex both load them as skills.
- **An import from [Event Modeling HCL](https://event-modeling-hcl.github.io)**, which turns an exported model into a `.skilj.toml` for one bounded context.

## Getting them

```sh
cargo binstall vados
cargo add skilj
```

- vados: [crates.io](https://crates.io/crates/vados), [changelog](https://github.com/gklijs/vados/blob/main/CHANGELOG.md)
- skilj: [crates.io](https://crates.io/crates/skilj), [changelog](https://github.com/gklijs/SkilJ/blob/main/CHANGELOG.md)

Both releases were built with a lot of help from agents. What I think about that is in [Pulling the chain yourself](/society/2026/pulling-the-chain-yourself).

*This blog is built with vados, too, and now with 0.6.0.*

*Photo: [The city across the water](/photos/2026/the-city-across-the-water), by me, taken this morning.*

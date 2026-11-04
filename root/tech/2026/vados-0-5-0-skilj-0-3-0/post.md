Yesterday was my first day back at work. It's a great team, but a pretty big one, and I felt tired afterwards, which is to be expected. It was nice to make a big walk back home to recover a bit. The reflection on the water was amazing and I wanted to capture it, so that's the photo at the top.

Two releases came out around that day, so here they are: [vados](https://github.com/gklijs/vados) 0.5.0 on Monday and [skilj](https://github.com/gklijs/SkilJ) 0.3.0 today.

## vados 0.5.0

I'm not sure which part I'm happiest with. Mostly I'm happy that the four swamp sites I build with vados need less custom code, and that the dropdown in the navbar now has the right look.

In the [0.4.0 post](/tech/2026/vados-0-4-0) I named four things I kept running into. Two of them are in this release:

- **Feeds look deeper.** They can select their entries with `from` and `depth`, the way `latest` already does.
- **A navbar colour can name its theme.** `"navbarTheme": "dark"` in `main.json` says which theme belongs on a colour that a stylesheet recoloured, and a handful of `--vados-nav-*` properties set the rest.

The other two are still open: changing or removing menu entries from the command line, and embedding a Luma calendar as a whole.

Other things turned up as well:

- Dropdowns in the main menu get a real button, so a keyboard, a touch screen and a screen reader can all open them. `Escape` closes them.
- `"search": true` publishes a site search that makes no outside requests.
- A page can be an `event`, with structured data and an `.ics` file, and `agenda` lists them.
- `vados generate --check-links` checks the links, fragments and assets of the generated site, without any network access.

### What it took here

- Netlify installs 0.5.0, and now builds with `--check-links`, so a broken internal link fails the deploy.
- `"navbarTheme": "dark"` and three `--vados-nav-*` properties replace the rules that set the navbar's text by hand, along with a rule for the open menu on a phone.
- The current page in the navbar now takes the bar's text colour. This blog's is pink, so a short rule keeps it that way.

## skilj 0.3.0

This is a breaking release again, with upgrade notes at the top of the [changelog](https://github.com/gklijs/SkilJ/blob/main/CHANGELOG.md). PostgreSQL 15 is now the minimum, and the first start on 0.3 rewrites how event tags are stored, which locks event writes while it runs, so a large history needs a maintenance window.

The two biggest additions are about things an append-only log finds awkward:

- **Large payloads.** Payloads above 256 KiB are now refused by default, and the limit can be changed. For really large bytes, a payload carries a reference to a blob instead. An append checks those references under the write lock, and the bytes can be sealed under a subject's key, so forgetting that subject removes them too. They are stored in Postgres by default, or in S3 with the new `skilj-blob-s3` crate.
- **Being wrong.** You can't rewrite an event, but you can now say that it was wrong. A decision can retract an event, or correct it with a retraction and a replacement in one append. It can also mark an event as in doubt while someone looks into it, in which case the event still counts. With as-of reads you can ask what was known at a given sequence, so "what did we know back then?" still has an answer after a correction.

The idea for retractions and corrections came from being at the [AxonIQ Conference](https://www.axoniq.io/events/axoniq-conference-2026-registration) in Utrecht last week. It was nice to be in Utrecht again, because I used to study there. Getting to the conference was a twenty-minute walk through the city centre, which was pretty nostalgic. I also saw a lot of former colleagues again, and there were new people at AxonIQ working with my code.

The security changes are worth reading if you use private fields. A private-field grant, including one already made, now opens a field only while its grantor is that field's own default reader and an active Role. A sensitive field with a value but no usable subject is refused, where 0.2 stored it in plaintext.

### The hard part: scope

The hardest part was getting the scope of skilj right. I don't want it to keep growing, but it does need to be useful.

I'm still not sure about only having [pure command handlers](/tech/2026/skilj-0-2-0). With Axon, for example, you can use command handling to defer work, using the Axon Server command bus to have the right instances execute things in a certain order. But skilj should focus on both strong consistency and data security. Performance and flexibility are less important by design.

## Getting them

```sh
cargo install vados
cargo add skilj
```

- vados: [crates.io](https://crates.io/crates/vados), [changelog](https://github.com/gklijs/vados/blob/main/CHANGELOG.md)
- skilj: [crates.io](https://crates.io/crates/skilj), [changelog](https://github.com/gklijs/SkilJ/blob/main/CHANGELOG.md)

*This blog is built with vados, too, and now with 0.5.0.*

*Photo: [Last light on the water](/photos/2026/last-light-on-the-water), by me, taken on that walk home.*

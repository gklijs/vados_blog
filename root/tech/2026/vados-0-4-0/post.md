Yesterday's release was **0.3.0**. Today's is **0.4.0**, and it has one big change: vados now uses Bulma 1.0. It is a breaking one, which is why it gets its own number.

Bulma 1.0 dropped the tiles that vados used to lay out a page, so pages are now built from Bulma's columns and a two-column grid. The child tiles are placed row by row, so the reading order is the same on a phone as on a desktop. That also deleted the CSS I had written to put the cards back in order on a phone, and the `order` attributes vados used to put on them.

## Dark mode, and a way out of it

Bulma 1.0 follows the reader's colour-scheme preference. Highlighted code gets a dark set of colours too, and notifications and the navbar carry the theme that matches their colour, so text on them stays readable either way.

This blog has a fixed palette, near-black, white and magenta. Before the release I ran the unreleased branch against this blog, like last time. In my first port the post titles turned black on black in dark mode, and I wanted a way to switch it off: `"colorScheme": "light"` in `main.json` pins every page to one theme, and `"dark"` does the opposite. I tried it here first.

Then I gave the palette a dark counterpart instead, a handful of CSS variables, so this blog now follows your preference, too. The background, cards and links have dark values that pass 4.5:1 contrast, and the pin is there for sites that don't want to do that.

The same run is behind three smaller changes. The last side tile no longer stretches to the bottom of the page unless you set `stretchSideNotification`, `check` warns about a `sass/main.scss` that still loads Bulma with `@import`, and the README has a section on moving an existing site.

## What it took here

- `package.json` asks for Bulma `^1.0.4`, and `sass/main.scss` loads it with `@use ... with (...)`.
- About 50 lines of tile and phone CSS are gone, and a dozen colours became variables with a dark value.
- The open menu on a phone is dark now, where it used to be white, so a rule from the Bulma 0.9 days made its icons black on black. That rule is gone.
- Bulma 1.0 has no `$colors` map to prune, so the stylesheet grew from 80 KB to 392 KB (42 KB compressed), even loading only the parts the site uses. That's the one thing I'd call worse.
- Bulma's footer variable sets only the background, so the text colour is set by hand.
- vados picks a light or dark theme per colour assuming Bulma's defaults. I recoloured the navbar to near-black, so its text colour is set by hand, too.

## On the horizon

There is no roadmap, only a few things I keep running into. A feed only lists the direct children of the page it is on, and I'd like it to look deeper, the way `latest` already does. The theme a colour carries could be configurable, so recolouring doesn't need CSS to compensate. Menu entries can be added but not changed or removed from the command line, and a Luma calendar can't yet be embedded as a whole.

```sh
cargo install vados
```

- crates.io: [vados](https://crates.io/crates/vados)
- GitHub: [gklijs/vados](https://github.com/gklijs/vados), with the full [changelog](https://github.com/gklijs/vados/blob/main/CHANGELOG.md)

*This blog is built with vados, too, and now with 0.4.0.*

*Photo: [Geertruidenberg on the horizon](/photos/2026/on-the-horizon), by me, taken this afternoon. Zoomed in as far as the lens goes, the horizon is mostly haze. Roughly how far ahead I can see with vados, too.*

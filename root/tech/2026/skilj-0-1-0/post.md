*Originally published as a LinkedIn article on 19 October 2026. The code has since moved from Codeberg to GitHub; the links are updated.*

I tagged skilj 0.1.0 today. After a long run of 0.0.x releases that came with no promises at all, this is the first version where I'm willing to say: upgrades within 0.1 won't break your code.

So, what is it? skilj is a Rust library for building event-sourced applications on top of Postgres. You describe your domain as events (things that happened) and commands (requests to make something happen), and skilj takes care of storage, consistency, and serving it all over GraphQL and REST.

First, the name, because people ask. It's an anagram of my last name, Klijs. I only found out later that skilja is Swedish for "to separate". I'm taking that as a sign, because separating things is pretty much the whole design.

**Commands are kept apart from the history they don't care about.** Most event sourcing libraries make you pick an aggregate up front, an Account or an Order, and every command replays that aggregate's full history. skilj uses a Dynamic Consistency Boundary instead: events carry tags, and a command is checked against exactly the events that share its tags. Enrolling a student in a course can check both the student and the course in one atomic decision, without either of them having to "own" the other. No more arguing in a meeting room about which aggregate a feature belongs to. (You can still argue about naming. I can't fix everything.)

**Personal data is kept apart from the event log.** Sensitive fields are encrypted per person, so when someone asks to be forgotten, you throw away their key and their data turns into noise, while the rest of history stays intact. There are also "blind" tags, so you can enforce things like "one account per email address" without ever storing the email address in plain text.

**And reads are kept apart from writes**, with projections, snapshots and the rest.

On top of that it generates the APIs from your types. The GraphQL schema is tailored to whoever is calling, it can act as an Apollo Federation subgraph, and there are live subscriptions. And there's a list of things you usually end up building yourself: deadlines and recurring schedules, idempotency keys, command approval with a second pair of eyes, upcasting old events, parking failed deliveries so you can retry them, and bridges to Kafka, AMQP, NATS JetStream and Temporal. All of it lives in one library on one Postgres database. No extra event store to run, patch and get paged about at 3am.

Some numbers from the road to 0.1:

- 15 crates published to crates.io
- a design log in the repo that is now at section 221, with the reasoning behind each decision, including the ones I got wrong first
- one target directory that grew to 187 GB this week and filled my disk in the middle of release prep. Rust compile times are a lifestyle.

To be honest about where it stands: it's pre-1.0, it's built and maintained by one person, and it hasn't had an independent security audit. What 0.1 does promise is semantic versioning, automatic database upgrades (tested all the way back to the very first release's schema), and a minimum Rust version that's checked in CI.

If you want to kick the tires, this gives you a running project with a small wallet example:

```sh
cargo generate --git https://github.com/gklijs/SkilJ.git templates/skilj-template
```

Feedback, issues, and "why on earth did you do it like this" questions are all very welcome.

- GitHub: [gklijs/SkilJ](https://github.com/gklijs/SkilJ)
- crates.io: [skilj](https://crates.io/crates/skilj)

*Photo: [Path through the trees](/photos/2026/path-through-the-trees), by me.*

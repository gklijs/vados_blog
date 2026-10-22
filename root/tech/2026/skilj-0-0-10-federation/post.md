*Originally posted on LinkedIn on 11 October 2026. The code has since moved from Codeberg to GitHub; the link is updated.*

Apollo held their summit last week and everyone came home talking supergraphs. Our timing was good: in this release skilj's GraphQL endpoint can join a supergraph as an Apollo Federation v2 subgraph.

Quick refresher: skilj is an event-sourcing framework in Rust on Postgres. You define commands and events, and you get GraphQL and REST APIs, projections, snapshots and messaging bridges.

## Federation v2

- Plugs into Apollo Router (2 and the 3.0 preview), Hive Router or Gateway, Cosmo, or schema stitching.
- Projections become entities, and each lookup is checked against the caller's own permissions.
- CI composes the schema with both Apollo's and Hive's composition on every build.

## Commands read only what they need (Dynamic Consistency Boundaries)

- Consistency queries: a command names exactly the events its decision depends on.
- `nothing()`: for commands that need no history. On one hot account that took us from 110–160 to 2,500–5,000 commands/s.
- Snapshots as query items: a transfer between two accounts can decide on a snapshot of each.
- New warnings for slow reads and slow decides, with defaults taken from our benchmarks, so you find out before your users do.

## Speed

- Projection catch-up is 25–50× faster.
- Fewer round trips and no connection ping per command. With 1 ms to Postgres, a single caller went from 46 to about 26 ms per command.
- Batches are written as sets, and sync projections fold a whole batch at once.
- A small Kafka producer setting (`linger.ms=0`) takes outbound from about 165 to about 2,000 events/s.

## Safety

- Database epochs: after a failover or restore, a stale position is refused instead of quietly skipping events.
- Per-message idempotency keys, so NATS and AMQP redeliveries are no longer lost.
- Command dry-runs: see what a command would decide without persisting anything.
- A conformance suite that checks GraphQL and REST give the same answers.

Plus a pile of fixes, new benchmarks and deployment guidance in `docs/performance.md`.

We're still at 0.0.x, so some things broke: `nextCursor` on `GET /v1/events` is now an opaque string, `submit_command` takes snapshot states, and a few signatures changed in `skilj-graphql` and `skilj-bridge`. Read the CHANGELOG before you upgrade.

All 15 crates are on crates.io, and the code is at [gklijs/SkilJ](https://github.com/gklijs/SkilJ).

*Photo: [Where the roads meet the sea](/photos/2026/where-the-roads-meet-the-sea), by me.*

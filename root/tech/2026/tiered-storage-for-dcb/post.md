*Originally posted as a question to the DCB community on 14 October 2026. The issue it links has since moved from Codeberg to GitHub, with the same number.*

I'm working on skilj, a Rust event store on Postgres built around DCB. I've been exploring moving old event payloads to object storage such as S3, because an event store only grows. In DCB the hard part is clear: a consistency query has to see every matching event forever. A uniqueness claim from five years ago still decides today's command. So the tag index has to stay hot, and only payloads can move.

I measured it with 200k events, two tags each, on Postgres:

- ~100 B payloads: only 16% of the storage could move, so it's not worth it
- ~1 KB: 57%
- ~4 KB: 65%
- about 500–800 bytes per event stay hot whatever the payload size (row, indexes, tag index)

The open question is **when an event can safely go cold**. Age or event count is easy, but it hurts long-lived tags: a command deciding on an old account would fetch its whole history from S3. My current thinking is that an event is cold once every query that can match it is covered, by a snapshot past it or by a "latest only" query item that a newer event answers.

I'm curious:

- Has anyone hit storage limits with a DCB store, or is it more about backups and vacuum?
- How do other DCB implementations handle very long-lived tags: snapshots, or something else?
- Any other approach I'm missing?

The write-up with the numbers, a design sketch and what KurrentDB, Kafka and Axon do is in [skilj issue #92](https://github.com/gklijs/SkilJ/issues/92). Nothing is built yet, so all ideas are welcome, including "don't".

*Photo: [Floor after floor](/photos/2026/floor-after-floor), by me.*

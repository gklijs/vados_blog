*Originally posted on LinkedIn on 22 October 2026.*

Eight years ago I published version 0.1.0 of a small Rust crate. It solved one problem: reading Kafka messages that a Java service had encoded with Confluent Schema Registry. Today I released 6.0.0, the biggest update since that first version.

Some numbers I didn't expect when I started:

- 7.5 million downloads on crates.io, 1.4 million of them in the last 90 days
- 546 GitHub repositories depend on it, plus 10 published crates
- 27 contributors and 28 releases since 2018

## Why use a schema registry?

Kafka itself doesn't care what you put in a message; to Kafka it's just bytes. That's great for throughput, but it means the producer and every consumer have to agree on the format, usually without talking to each other. A schema registry turns that agreement into something you can check:

- Each message carries a small schema id, so the full schema doesn't travel with every record.
- Compatibility rules reject a breaking change before it reaches production, not after a consumer starts failing.
- Avro, Protobuf and JSON Schema all work, so teams can keep the format they already use.
- A Rust service and a Java service can read each other's data with no glue code.

## What's new in 6.0

- A new `ProtoEncoder` for Protobuf messages that are only known at runtime. It can also encode straight from JSON.
- Protobuf decoding is rebuilt on protox and prost-reflect.
- JSON Schema validation now uses the jsonschema crate, with compiled validators cached.
- The schema id can be read from and written to Kafka headers everywhere, not only in the payload.
- A declared minimum Rust version (1.88), and the crate is on the 2024 edition.

It's a major release, so there are breaking changes. The release notes have a short "Upgrading from 5.x" section.

Thanks to everyone who filed an issue, sent a PR or just used it in production. If you run Kafka with Rust, I'd love to hear what you're building.

- GitHub: [gklijs/schema_registry_converter](https://github.com/gklijs/schema_registry_converter)
- crates.io: [schema_registry_converter](https://crates.io/crates/schema_registry_converter)

*Photo: [Train in a hurry](/photos/2026/train-in-a-hurry), by me.*


[skilj](https://github.com/gklijs/SkilJ) is a Rust library for building event-sourced
applications on Postgres, and 0.1 was just released. Most event-sourcing libraries are built
around aggregates. skilj has none. This post explains why, using one example that aggregates
handle badly.

## The example: enrolling a student in a course

We have two rules:

1. A course never has more students than its capacity.
2. A student is never enrolled in more than three courses at once.

The command is `EnrollStudentInCourse { student_id, course_id }`.

With aggregates, you first choose your consistency boundaries. You would naturally get a
`Course` aggregate and a `Student` aggregate, each with its own event stream, and each able to
guarantee only its own invariants. Rule 1 belongs to `Course` and rule 2 belongs to `Student`.
A single enrolment has to satisfy both, and no single transaction can see both streams.

That leaves the usual options, and each has a cost:

- **A saga or process manager.** Reserve a seat on the course, then check the student, and
  release the seat if the student is already at three. That means two writes, a temporary
  state that other readers can see, and compensation logic you have to get right.
- **A bigger aggregate.** Make `Enrolment` or `School` the aggregate. Now every enrolment in
  the whole school competes for one stream, and every command replays a history that is
  mostly unrelated to it.
- **Give up on one rule.** Check the student limit against a read model and accept that it
  will occasionally be wrong.

None of these is a domain decision. They are workarounds for a modelling choice that had to be
made before you knew which rules you would need.

## Dynamic Consistency Boundaries

Sara Pellegrini and Milan Savić named the alternative
[Dynamic Consistency Boundaries](https://dcb.events) (DCB). Events are not appended to a
stream that belongs to an entity. Instead they go into one log per bounded context, and each
event carries **tags**. A `StudentEnrolled` event is tagged with both `student: s1` and
`course: c7`.

A command says which tags it needs. Its decision is then made against every earlier event that
carries one of those tags. That is exactly the history the command depends on: no more, and no
less.

In skilj the enrolment looks like this (trimmed from
[`skilj-demo/src/courses.rs`](https://github.com/gklijs/SkilJ/blob/main/skilj-demo/src/courses.rs)):

```rust
impl CommandType for EnrollStudentInCourse {
    type Payload = EnrollStudentInCoursePayload;
    type Event = CoursesEvent;
    const NAME: &'static str = "EnrollStudentInCourse";

    // Ask for both histories: this student's and this course's.
    fn tag_mappings() -> Vec<TagMapping> {
        vec![
            TagMapping::new("student", "student_id"),
            TagMapping::new("course", "course_id"),
        ]
    }

    fn decide(payload: &Self::Payload, matching_events: &[Self::Event]) -> CommandDecision {
        let Some(capacity) = course_capacity(matching_events, &payload.course_id) else {
            return reject("course_not_found");
        };
        let roster = active_students_in_course(matching_events, &payload.course_id);
        if roster.len() as i64 >= capacity {
            return reject("course_full");
        }
        let schedule = active_courses_for_student(matching_events, &payload.student_id);
        if schedule.len() >= MAX_ACTIVE_COURSES_PER_STUDENT {
            return reject("student_course_limit_reached");
        }
        accept("StudentEnrolled", &payload)
    }
}
```

`decide` is a pure function. It gets the union of one student's history and one course's
history, checks both rules, and returns either the events to append or a rejection. There is
no saga, no reservation and no compensation. The command that needs both facts simply asks for
both.

Other commands ask for less. `OpenCourse` only needs the `course` tag. An enrolment of a
different student in a different course shares no events with this one and never reads them.
The boundary is defined per command, which is what "dynamic" means here.

Uniqueness rules, such as "an email address can be registered once", follow the same pattern.
The command asks for the `email` tag and rejects if any event already has it. You don't need a
unique index or a reservation table. (skilj can also make that tag a keyed hash, so the address
is never stored in the clear, but that deserves its own post.)

## How skilj keeps it atomic

A pure `decide` function is only half of the story. Two enrolments racing for the last seat
must not both be accepted.

The DCB specification describes an optimistic approach: you append with a condition that says
"fail if any event matching my query was added after position N", and retry if it fails. skilj
chooses something simpler. All commands for one bounded context are serialized through a
single Postgres row lock. While a command holds the lock, skilj reads its matching events,
runs `decide`, appends the result with a gapless sequence number, and commits. Because nothing
can interleave, there is no conflict to detect and nothing to retry. skilj's test suite races
two enrolments for the last seat to check this.

Serializing commands sounds slow, and there is a ceiling, so here it is. Concurrent commands
are group-committed: callers queue up, one of them takes the lock and decides the whole batch,
and commits once. Under load the batches grow, so the lock cost is shared. On a development
machine, one bounded context handles roughly 400 to 850 commands per second when commands touch
different entities, and around 100 per second when every command hits the same entity with a
growing history. Snapshots help with the second case. The full numbers and method are in
[`docs/performance.md`](https://github.com/gklijs/SkilJ/blob/main/docs/performance.md).

Different bounded contexts never share a lock, so the real lever is to split unrelated domains
or tenants into separate contexts. If one context needs thousands of commands per second,
skilj is not the right tool, and the README says so.

## What you get on top

The tags make the rest of the library easier to build:

- **GraphQL and REST APIs** generated from the registered event and command types. Each
  caller's GraphQL schema only contains what their grants allow, and it can act as an Apollo
  Federation subgraph.
- **Projections and snapshots** for reads, so queries don't have to replay events.
- **Personal data handling.** Sensitive fields are encrypted per subject, and `forgetSubject`
  makes them unreadable without rewriting the log.
- **The things every event-sourced system ends up building:** deadlines, idempotency keys,
  upcasting, command approval, parked deliveries with redrive, and bridges to Kafka,
  AMQP 1.0, NATS JetStream and Temporal.

All of it runs on one Postgres database. There is no separate event store to operate.

## Try it

You only need Rust. The template starts its own embedded Postgres:

```sh
cargo install cargo-generate
cargo generate --git https://github.com/gklijs/SkilJ.git templates/skilj-template --name my-wallet
cd my-wallet && cargo run --bin server
```

It prints commands you can paste to make a deposit, see an overdraft rejected, and query the
balance.

skilj is pre-1.0 and has one maintainer. Releases follow semver the way Cargo does, and schema
upgrades are automatic and forward-only. I'd like to hear where the API feels wrong, which
features are missing, and whether DCB works for your domain. Issues and discussions are open at
[github.com/gklijs/SkilJ](https://github.com/gklijs/SkilJ).

*A note on the name: skilj is an anagram of my last name, Klijs. In Swedish, "skilja" means to
separate, which turned out to describe the design: each command is decided apart from
everything it doesn't touch.*

*Photo: [Sun on the water](/photos/2026/sun-on-the-water), by me.*

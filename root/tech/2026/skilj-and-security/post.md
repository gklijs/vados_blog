
I don't know every nut and bolt of [skilj](https://github.com/gklijs/SkilJ). That's an odd thing
to admit about a library I build and maintain on my own, and a worse one to admit in a post about
security. But it's true, and the rest of this post doesn't make much sense without it.

Much of skilj was written by Claude. I steer, I decide, I review, and I wrote very little of the
code myself. Not because I had a principled plan, but because it was simply too tempting. When the
code shows up faster than I can think about it, "I'll write it by hand to be sure" stops being a
serious option. So I'm slightly uncomfortable, and I'd rather say so than write the usual paragraph
about taking security very seriously.

## Skyhooks and cranes

Daniel Dennett, in [*Darwin's Dangerous Idea*](https://en.wikipedia.org/wiki/Darwin%27s_Dangerous_Idea),
makes a distinction between skyhooks and cranes. A skyhook lifts things from above, with nothing
holding it up: a mind-first force that makes design something other than mechanism. A crane also
lifts, but it stands on the ground, and you can see how it works.

In software, the old skyhook was the author. The code is fine because the person who wrote it
understood it. Review was a second person who understood it too. That was never fully true, but it
was true enough that we built our habits on it.

With AI writing the code, that skyhook is gone. Later, in
[*From Bacteria to Bach and Back*](https://philosophynow.org/issues/129/From_Bacteria_to_Bach_and_Back_by_Daniel_Dennett),
Dennett's phrase for it is "competence without comprehension". Termites build mounds that ventilate
themselves, and no termite understands ventilation. A model that writes a correct access check is in
a similar position. Searle would call it a [Chinese Room](https://plato.stanford.edu/entries/chinese-room/):
symbols shuffled by rules, with no grasp of what they mean. Dennett argued that the room's pull comes
from the details it leaves out, like how large the software would have to be. I'd like to think he's
right about the model. At the end of a long day, I'm less sure about me.

So it has to be cranes. Things that stand on the ground and can be checked:

**Tests.** AI-written code needs proper tests, at the very least. The obvious problem is that the
tests are also written by AI. A test that checks the wrong thing passes just as confidently as one
that checks the right thing. Many entries in the design log say that a fix's test was seen failing
without the fix, and what it did before. Karl Popper would recognise the idea as
[falsifiability](https://en.wikipedia.org/wiki/Falsifiability): a theory that no observation could
contradict isn't telling you anything, and neither is a test that no bug could make fail. It's the
closest thing I have to a test for the tests.

**Tests that can't quietly not run.** Many of the tests need Postgres. A test that skips because the
database didn't answer looks exactly like a test that passed. CI
[fails the build](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#ci-silent-skip-guard)
if anything skipped. That guard [had a hole of its own](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#what-the-tests-cover),
by the way, which is roughly the point of this post.

**[A spec](https://github.com/gklijs/SkilJ/blob/main/specs/skilj.allium) separate from the code**,
which says what the system guarantees. The design log records an `allium check` after changes to it.

**A design log.** [`docs/architecture.md`](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md)
runs to section 225. In Plato's [*Phaedrus*](https://websites.umich.edu/~lsarth/filecabinet/PlatoOnWriting.html),
Socrates tells of a king who warns that writing gives the appearance of wisdom rather than wisdom
itself. Socrates adds that a text can't defend itself when you question it. He would have had
opinions about generated code. The design log is my attempt at something that does answer back. Ask
it why something is the way it is, and it tells you: every decision has its reasoning, and each fix
says what was wrong. I have not read all of it in one go, and I'm not sure anyone has. (We only know
about Socrates' story because Plato wrote it down, which I choose to read as permission.)

**A list of what nothing checks.** [`CONTRIBUTING.md`](https://github.com/gklijs/SkilJ/blob/main/CONTRIBUTING.md#what-the-tests-do-and-dont-verify)
sorts the guarantees into three piles: what holds by construction, what tests verify, and what
nothing verifies. That last pile is short, and I'm more proud of it existing than of anything in the
other two.

None of that removes the real limit, which is me. There is only so much code you can review in a
day, and an AI does not get tired before you do.

## The blind watchmaker reads your code too

Richard Dawkins called natural selection ["the blind watchmaker"](https://en.wikipedia.org/wiki/The_Blind_Watchmaker):
it produces things that look designed, without seeing ahead or understanding what it makes. I find
that a fair description of how a lot of code gets written now. It's also, less comfortably, a fair
description of how a lot of code gets *attacked*. Nobody needs to understand your codebase anymore to
find the place where the authorisation check and the query disagree. They can ask a model to look,
and it will read a surprising amount of it without complaint.

That cuts both ways, and in skilj's case I've mostly been on the friendly side of it. The bugs I
caught myself were mostly about naming and about whether an API made sense to use. Some of the
security bugs came out of review passes, one of them an automated review of code a model had written.
Some examples:

- A caller allowed to *submit* commands, but not to *read* events, could submit a command it knew
  would be rejected. The rejection helpfully listed every event the decision had looked at. Read
  access, one deliberate failure at a time. ([§18](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#ultra-review-fixes))
- In a bounded context shared by several tenants, a caller with read access could query another
  tenant's projection by key. Closing that properly took
  [six sections of the log](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#cross-tenant-projection-read-fix-owner-tag),
  because once you add owner scoping to one door, you have to find all the other doors.
- A server error used to answer with Postgres' own text, like
  `relation "bc_acme_corp.events" does not exist`. Each bounded context has its own schema, so that
  message tells a stranger your tenant names and your table layout. ([§93](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#database-error-logging))
- The one-time secret for creating the first superadmin stayed valid in memory. Revoke every
  superadmin, and on any process that hadn't restarted since, whoever had read the startup log days
  earlier could claim the deployment again. ([§109](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#bootstrap-secret-first-claim))

So I think skilj is more secure than it would have been if I had written it alone in the same time.
But the bar isn't "better than me alone". skilj is about storing data, often personal data, and it's
open source, so anyone with a model and an afternoon can go through it. That bar is a lot higher, and
I can't honestly say it's cleared until someone other than me and my tools has tried.

## What skilj does prevent

The guarantee I trust most is the one that holds by construction, whatever the tests do. **No command
sneaks past its consistency check.** All commands of a bounded context are decided under one Postgres
row lock, and the check, the events and the idempotency key commit or roll back together. Two people
racing for the last seat don't both get it.
[Why skilj has no aggregates](/tech/2026/why-skilj-has-no-aggregates) goes into how that works.

The rest is ordinary code with tests behind it, which, as established, is a crane and not a skyhook:

- **Callers don't see what they can't use.** Each caller gets a GraphQL schema
  [built from their own grants](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#caller-scoped-schema),
  so another tenant's types don't even exist for them. Before that, a query that merely *mentioned* a
  type would pass or fail validation depending on whether it existed, which is a very polite way of
  handing out the tenant list.
- **Requests are [bounded](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#graphql-body-cap).**
  Body size, query depth and complexity, aliases, page sizes, subscriptions per websocket. One query
  that reads everything stopped working a while ago.
- **JWTs are checked properly**: issuer, [audience](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#jwt-audience-required),
  algorithm, expiry and [not-before](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#jwt-nbf-check).
  The not-before check was missing, so a token meant for next week worked fine today.

Then there's personal data, which is where an event log is at its most awkward. Events are supposed
to be immutable, and people have the [right to be forgotten](https://en.wikipedia.org/wiki/Right_to_be_forgotten).

- **Sensitive fields are encrypted per person.** `forgetSubject` destroys that person's key, and their
  fields become noise while the rest of history stays intact. This is called
  [crypto-shredding](https://en.wikipedia.org/wiki/Crypto-shredding).
- **[Private fields](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#private-fields-third-protection)**
  are stored as is, but redacted on every event and command read for anyone not entitled to them.
- **[Blind tags](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#blind-tags)** enforce "one
  account per email address" without storing the address. The tag is a keyed hash of the normalised
  value, with a separate key per constraint, so hashes can't be joined across bounded contexts. If the
  key leaks, it [can be rotated](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#blind-index-key-rotation),
  and skilj re-wraps every stored hash without needing the original values. It's the one place in
  skilj where being blind is the feature.
- **[Secrets](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#211-secrets-rotatable-credentials-an-adapter-fetches-never-a-normal-read)**,
  like an adapter's OAuth refresh token, are never returned by a normal query. Only the one adapter
  granted the secret can fetch it, and rotating it destroys the old version's key in the same
  transaction.

## Agents get a keyhole, not a key

One part of skilj was designed with AI on the *calling* side. I saw the need for an agent that can
operate on specific data, and only that. Giving an agent direct access to a database is risky,
because an agent is not deterministic. The same prompt can do something sensible a hundred times and
something creative the hundred-and-first. Nietzsche wrote in his notebooks that there are no facts,
only [interpretations](https://en.wikipedia.org/wiki/Perspectivism). For a language model that isn't
a provocation. It's a description of the job. Whatever text reaches the agent, a ticket, an email, a
web page, gets interpreted, and some of that text was written by someone hoping for a particular
interpretation.

So the REST API [exists for narrowly scoped callers](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#rest-wire-contract).
A token is scoped to exactly one registered type: one command it may submit, or one kind of event it
may read or create. It can be scoped to one owner as well. An agent that handles refund requests can
ask for refunds, for that customer, and do nothing else. It can't browse, it can't query around, and
it can't write SQL, however politely it's asked to.

That limits the blast radius. It does not limit intent. If an agent reads a cleverly worded support
ticket and decides a refund is in order, and its token allows refunds, skilj accepts the refund. I
don't know of a technical fix for [prompt injection](https://genai.owasp.org/), and I'm not going to
pretend skilj has one. What it has is [command approval](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#214-generic-command-approval-issue-98):
a command type can require that a submission is a proposal, which someone else approves. The agent may
ask; another account decides. It's [separation of duties](https://en.wikipedia.org/wiki/Separation_of_duties),
which is old, and which nobody had to invent for AI.

## What skilj can't prevent

Popper also wrote that our knowledge can only be finite, while our ignorance must necessarily be
infinite. I can't list the infinite part. This is the finite part I know about.

**Your `decide()` function.** skilj makes sure a command is decided against the right events,
atomically. Whether the decision is right is your code. If it lets someone withdraw more than their
balance, skilj will record that mistake with perfect consistency.

**A stolen token.** skilj checks that a token was issued by an IdP you trust. Whether the person
holding it is the person it was issued to is outside what any library can see. Dennett's last public
worries were about [counterfeit people](https://www.theatlantic.com/technology/archive/2023/05/problem-counterfeit-people/674075/):
AI convincing enough to pass for a real person. A convincing voice on the phone talking a helpdesk into
resetting an account never reaches skilj as anything but a valid token.

**Backups from before someone was forgotten.** Crypto-shredding destroys a key in the live database.
Last week's backup still has it, wrapped under the master key. With both, the forgotten person is
remembered again. Blind tags have the same shape: rotating a leaked key protects every copy taken
*after* the rotation. With the leaked key and an older copy, an attacker can hash guesses and look
them up, and email addresses are unfortunately very guessable.

**Private fields in your projections.** Redaction happens when events are read. A projection folds
events as they are stored, so if its state keeps a private field, every reader of the projection gets
it. skilj [warns at startup](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#advertised-vs-enforced)
for every projection that consumes one, because sometimes a staff-only view needs it. A warning is a
nudge, not a wall.

**SQL at compile time.** Each bounded context has its own Postgres schema, so table names are only
known at runtime, and the compile-time checked queries of [`sqlx`](https://github.com/launchbadge/sqlx)
can't be used. That's over 300 statements built with `format!`. What gets formatted in is the schema
name, which is validated and quoted, but a misspelled column compiles fine and fails when it runs. The
Postgres suites are the only check.

**A mixed-version rollout.** Add a blind tag while an older skilj version is still running, and that
older instance doesn't know the tag should be hashed. It stores the value in the clear. None of the
startup checks can catch it, because the old version predates them
([§205](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#blind-tags)).

**Dependencies.** [`cargo deny`](https://github.com/EmbarkStudios/cargo-deny) fails CI on every *known*
[advisory](https://rustsec.org/). The unknown ones are, so far, unknown.

**Your database superuser with your master key.** They can read everything. That's less a limitation
of skilj than a description of what those two things are.

**And an audit.** skilj is [pre-1.0](https://github.com/gklijs/SkilJ/blob/main/README.md#status-and-stability),
has one maintainer, and has had no independent security audit. A lot of review, much of it written
down, but nobody has been paid to break it.

## Making good mistakes

Dennett wrote in [*Intuition Pumps*](https://www.themarginalian.org/2013/05/29/intuition-pumps-daniel-dennett-on-making-mistakes/)
that the chief trick to making good mistakes is not to hide them, especially not from yourself. The
[design log](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md) is, for a large part, a
list of my mistakes and Claude's, and I've stopped trying to tell which was whose. What matters is that
each one is written down, with its fix, and where the log can show it, a test that failed before the
fix, so the same mistake has to find a new way in.

If you find one that isn't written down yet, I'd like to hear about it. If it's a real hole, please use
[GitHub's private vulnerability reporting](https://github.com/gklijs/SkilJ/security/advisories/new)
rather than an issue. I'll write it into the log either way, and credit you there if you want the
credit.

*Photo: [Batman, grappling gun](/photos/2026/batman-grappling-gun), by me. He also works alone, and has also
never been audited.*

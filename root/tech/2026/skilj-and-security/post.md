
Every library README has a sentence about security. Usually it says something reassuring and
vague. This post is the opposite. It is a list of what [skilj](https://github.com/gklijs/SkilJ),
my event-sourcing library for Rust on Postgres, actually protects against, what it can't protect
against, and why the second list got longer and more interesting once AI turned up on both
sides of the keyboard.

Let me start with a confession, because the rest makes more sense with it: **skilj is built
with Claude.** Most of the code was written by an AI, with me steering, reviewing, and
occasionally saying "no, that's wrong, and here's why." That has consequences for security, some
good and some uncomfortable, and I'd rather talk about them than pretend they aren't there.

## Competence without comprehension

Daniel Dennett had a phrase for how evolution produces termite mounds and cuckoo chicks:
**competence without comprehension**. Things can do clever work without understanding why the
work is clever. He spent a good part of his last books pointing out that this describes a lot
more than termites.

It also describes a large language model writing a row-level access check.

For decades, software security leaned on an assumption nobody wrote down: *the person who wrote
the code understood the code*. Code review was a second person who understood it too. When a
bug slipped through, at least someone had once held the whole picture in their head.

That assumption is gone. Code can now be produced faster than anyone can comprehend it, and it
compiles, and the tests pass, and it looks exactly like code written by someone who knew what
they were doing. That last part is the trouble. Bad code used to look bad.

skilj's answer is not "trust the AI" and not "don't use the AI". It's to make comprehension a
separate deliverable:

- **A design log.** [`docs/architecture.md`](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md)
  is at section 225. Every decision has its reasoning, and every bug fix says what was wrong, how
  it was found, and which test fails without the fix.
- **A behavioural spec** (`specs/skilj.allium`), separate from the Rust, that says what the
  system guarantees. Code that drifts from it gets caught.
- **Honesty about the test suite.** `CONTRIBUTING.md` sorts the guarantees into three piles:
  those that hold by construction (Postgres transactions and constraints), those tests verify,
  and those *nothing* verifies. More on that last pile below.

Dennett also wrote, in *Intuition Pumps*, that "the chief trick to making good mistakes is not to
hide them, especially not from yourself." The design log is mostly a catalogue of mistakes. That
is on purpose.

## The mirror has two sides

The same thing that lets me build a library alone lets anyone *read* it alone. An attacker no
longer needs a week to understand a codebase. They can ask a model to look for the place where
the authorization check and the query disagree, and it will happily go and look.

That sounds scary, and it is a bit, but I've been on the receiving end of the friendly version.
A good number of skilj's real security fixes were found by AI review of AI-written code:

- **A read side channel.** A caller allowed to *submit* commands, but not to *read* events,
  could craft a command that was bound to be rejected, and the rejection helpfully included every
  event the decision had looked at. So: read anything you like, one deliberate failure at a time.
  Now only admins get those events back (§18).
- **Cross-tenant reads, six times over.** In a bounded context shared by several tenants, any
  caller with read access could query another tenant's projection by key. Fixing it properly
  meant adding owner scoping to grants, and then finding every other door: raw event queries,
  command listings, snapshots, subscriptions, templates (§23 to §28). Then writes (§30).
- **A scoped admin escaping its scope** by minting an unscoped token for itself (§92).
- **Database error text in responses.** A 500 used to say
  `relation "bc_acme_corp.events" does not exist`, which tells a stranger your tenant names. Now
  the text stays in the server log, and the caller gets a trace id (§93).
- **A bootstrap secret that came back from the dead.** The one-time secret for creating the
  first superadmin stayed valid in memory, so revoking every superadmin quietly reopened the door
  for whoever had read the startup log (§109).

None of these were found by a fuzzer or a pentest. They were found by asking a model to read the
code like an adversary would. That is the new normal for defenders. It is also the new normal for
attackers, so the honest conclusion is not "AI makes us safer" but "AI makes the gap between
reviewed and unreviewed code much wider".

## What skilj does prevent

Some things are prevented by construction, which is the kind of prevention I trust most:

- **A command can't sneak past a consistency check.** Every command for a bounded context is
  decided under one Postgres row lock, and its check, its events and its idempotency key commit
  or roll back together. Two people racing for the last seat can't both get it.
- **Callers only see the schema they're allowed to see.** Each caller gets a GraphQL schema
  built from their own grants, so you can't even discover that another tenant's types exist
  (§138).
- **Requests are bounded.** Body size, query depth and complexity, aliases, pages, websocket
  subscriptions, filter patterns: every request and background path has a cap (§69 to §74, §121).
  "Send one query that reads everything" stopped working a while ago.
- **JWTs are checked properly**: issuer, audience (required, §81), algorithm, expiry, and
  not-before (§111). That last one was missing until a review noticed.

And then there's personal data, which is where an event log is at its most awkward. Events are
supposed to be immutable. GDPR says people can be forgotten. Those two get along about as well
as you'd expect.

- **Sensitive fields are encrypted per person.** `forgetSubject` destroys that person's key, and
  their fields turn into noise, while the rest of history stays intact. This is called
  crypto-shredding.
- **Private fields** are stored in the clear, but redacted on every event and command read for
  anyone not entitled to them.
- **Blind tags** let you enforce "one account per email address" without ever storing the email
  address. The tag is a keyed hash of the normalized value, with a separate key per constraint,
  so hashes can't be joined across contexts (§205). If the key leaks, you can rotate it, and
  skilj re-wraps every stored hash without needing the original values (§209).
- **Secrets**, like an adapter's OAuth refresh token, are never returned by a normal query.
  Only the one granted adapter can fetch them, and rotating a secret shreds the old version's
  key in the same transaction (§211).

## What skilj can't prevent

This is the list most READMEs skip. Karl Popper put it well: "Our knowledge can be only finite,
while our ignorance must necessarily be infinite." I can't list my infinite ignorance, but I can
list the finite part I know about.

**Your `decide()` function.** skilj makes sure a command is decided against the right events,
atomically. Whether the decision is *right* is your code. If it lets someone withdraw more than
their balance, skilj will very reliably, very consistently, and with gapless sequence numbers,
let them.

**A stolen token is a valid token.** skilj checks that a JWT was issued by the IdP you trust. It
can't check whether the human holding it is the human it was issued to. Dennett's last big public
worry was about "counterfeit people", AI that can pass as a real person well enough to fool us.
A convincing voice on the phone asking the helpdesk to reset an account isn't something a
database library can see. That fight happens at the IdP and at the helpdesk, not in skilj.

**An AI agent doing exactly what it's allowed to do.** skilj's REST API exists for narrowly
scoped callers, explicitly including AI agents: a token is scoped to exactly one registered type
(§7.1). That limits the blast radius, not the intent. If an agent reads a cleverly worded support
ticket and decides to refund it, and its token allows refunds, skilj will accept the refund. The
answer skilj offers is command approval (§214): a command type can require that a proposal is
approved by someone else first. An agent may *ask* for a refund; a human approves it. That's not
a technical fix for prompt injection. Nobody has one. It's just old-fashioned separation of
duties, which turns out to age well.

**Backups taken before someone was forgotten.** Crypto-shredding deletes a key in the live
database. A backup from last week still has that key, wrapped under the master key. If someone
has both the backup and the master key, the forgotten person is unforgotten. Same for blind tags:
rotating a leaked key protects every copy of the data taken *afterwards*, never one taken before.
With a leaked key and an old copy, an attacker can test guesses: hash `alice@example.com` and look
it up. Email addresses are, unfortunately, very guessable.

**Private fields in your projections.** A private field is redacted when an event is read. But
a projection folds events as they are stored, so if your projection keeps a private field in its
state, every reader of that projection gets it. skilj logs a warning at startup for every
projection that does this (§177), but it doesn't stop you, because sometimes a staff-only view
legitimately needs the field. A warning is not a guarantee.

**SQL at compile time.** Every bounded context has its own Postgres schema, so table names are
dynamic, so `sqlx`'s compile-time checked queries can't be used. There are over 300 statements
built with `format!`. What gets formatted in is the schema name, which is validated and quoted,
but nothing stops a wrong column name from compiling fine and failing at runtime. The Postgres test suites are the only check, and CI fails the
build if any of them silently skipped (a guard that, fittingly, itself had a hole, found in §183).

**Your database superuser, and your master key.** Anyone with superuser access to Postgres and the
encryption master key can read everything. That's not a skilj limitation so much as the definition
of those two things.

**A mixed-version rollout.** If you add a blind tag while an older skilj version is still running,
that older instance doesn't know the tag should be hashed, and will store the value in the clear.
It's the one case none of the startup checks can catch, because the old version predates them.

**Dependencies.** `cargo deny` fails CI on every known RustSec advisory and every license that
doesn't fit. "Known" is doing a lot of work in that sentence.

**And me.** skilj is pre-1.0, has one maintainer, and has had no independent security audit. Lots
of internal review, all of it written down, but no third party has been paid to try to break it.
If you need that, skilj isn't there yet, and the README says so.

## Things we used to take for granted

Let me end with a short list of assumptions that didn't survive the last couple of years:

- *"Nobody is going to read all our code."* Something will, in minutes, and it doesn't get bored.
- *"The person who wrote it understood it."* See Dennett, above.
- *"A secret printed in the startup log is harmless once it's used."* Only if "used" really
  means "dead" (§109).
- *"Error messages are for developers."* They're for whoever sends the request.
- *"Hashing the email address makes it anonymous."* Only as long as the key stays secret, and
  only for copies made after the last rotation.
- *"The caller is a person."* Increasingly it's an agent, acting on text that someone else wrote.

Heraclitus said everything flows. He wasn't talking about key rotation, but he could have been.
Security was never a state you reach; it's a habit you keep. What changed is the speed: the bugs
get written faster, found faster, and exploited faster. The only answer I have is to write down
what I know, what I don't, and what nothing checks, and to keep that list honest.

Socrates, roughly, claimed his wisdom was only that he knew he didn't know. For a security
section in a README, that's not a bad standard to aim for.

If you find something on the "can't" list that should be on the "can", or something that's
missing from both, please tell me. Privately, through
[GitHub's vulnerability reporting](https://github.com/gklijs/SkilJ/security/advisories/new), if
it's a real hole. I promise to write it down.

*Photo: [Batman, up close](/photos/2026/batman-up-close), by me. He's very serious about
security. He has also never been audited.*

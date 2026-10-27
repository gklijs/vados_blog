I tagged [skilj](https://github.com/gklijs/SkilJ) 0.2.0 today. It's a breaking release, which is what the
0.x number is for, and its theme is that access is now something you hold, not something you happen to
be called. The rest of this post explains what that means, and why a library that restricts itself to
pure decisions makes it a lot easier to get right.

In short:

- **Capabilities replace Role names.** A grant opens a gated projection or field only by holding the
  capability. Nothing implies one, not even being a superadmin.
- **Every change to access is an event**, written in the same transaction, so "what could this grant do
  on that date?" has an answer.
- **The master key lives at a key provider**, and deleting a tenant can be a cryptographic erasure.

## One at a time, and only if it fits

The photo at the top is a bridge in Molenhoek, in the Netherlands, and it's the picture I have in my
head for how skilj handles a command. One car at a time, and only if it fits. There's a width limit,
and it's signposted three times. Drivers keep testing it anyway:
[a Land Rover got stuck fast](https://www.gelderlander.nl/112-nieuws-mook-en-middelaar/land-rover-muurvast-op-beruchte-brug-in-molenhoek-auto-flink-beschadigd~a6b37a6f/)
(Dutch), [NOS counted at least ten vehicles in one week](https://nos.nl/artikel/2624714-caravans-vast-op-versmalde-brug-drie-borden-geven-het-aan)
(also Dutch), and in
[an English translation of a local report](https://openvan.camp/en/news/incident/ondanks-waarschuwingsborden-opnieuw-caravan-vast)
a caravan was the ninth to try. The bridge doesn't negotiate, and neither does skilj.

*One at a time* is the first half. All the commands of a bounded context are decided under one Postgres
row lock, so two people racing for the last seat don't both get it. *Only if it fits* is the second
half: the decision is made against exactly the events the command shares tags with, and the answer is
yes or no. (I wrote about how that works in
[Why skilj has no aggregates](/tech/2026/why-skilj-has-no-aggregates).)

What I want to point at today is the thing in the middle, the decision itself. Here is the withdrawal
from the wallet example in the template, trimmed a little:

```rust
fn decide(payload: &WithdrawPayload, matching_events: &[WalletEvent]) -> CommandDecision {
    let balance = balance_of(matching_events);
    if payload.amount > balance {
        return CommandDecision::Rejected {
            reason: format!("balance is {balance}, cannot withdraw {}", payload.amount),
            kind: "insufficient_funds".into(),
        };
    }
    CommandDecision::Accepted { events: vec![/* a Withdrawn event */] }
}
```

That is all your code gets to do. It receives the payload and the events that share the command's tags,
and it answers with a rejection or with the events to append. It's a plain synchronous function: no
database handle, no network, no clock, no idea who is calling. (Rust won't stop a function from opening
a file if it really wants to. The point is that the signature gives it nothing to hold on to.)

I did that on purpose, and it pays off in four ways.

**It's safe to run twice.** skilj decides optimistically and then again under the lock if the first
attempt raced with something. If `decide()` sent an email, that would be a bug. Because it can only
compute, running it again is merely wasteful.

**The part an AI writes is small.** In [Skyhooks, cranes and a library I didn't write](/tech/2026/skilj-and-security)
I admitted that Claude wrote much of skilj. Application code may well go the same way, and a decision
function is the best possible thing to let a model write: the whole of it fits on one screen, it can't
leak anything it can't see, and you can read it without understanding the rest of the system.

**It can't be talked out of the checks.** The order of the pipeline is not up to the decider. Below is
what happens to a command. Everything before `decide()` is the library's job, and an unauthorised caller
never reaches it.

**It's trivial to test.** Events in, decision out. No Postgres, no mocks. For the cases where you do want
the real thing, there's a dry run that authorises like a normal submission and reports what the decision
would be without writing anything.

Green means allowed, red refused, and yellow is held back or hidden. The diagrams are simplified from
[`docs/authorization.md`](https://github.com/gklijs/SkilJ/blob/main/docs/authorization.md), which has
the complete set.

<pre class="mermaid">
flowchart TD
    IN(["A command arrives<br/>(JWT or id.secret token)"]):::start --> AUTH{"Authenticated, and allowed<br/>to submit this command?"}:::decision
    AUTH -- no --> DENY["Refused.<br/>decide() never runs"]:::deny
    AUTH -- yes --> IDEM["Check the idempotency key"]:::step
    IDEM --> POLICY{"Does the command type<br/>need approval?"}:::decision
    POLICY -- yes --> PROPOSE(["Stored as a proposal.<br/>decide() runs at approval"]):::hide
    POLICY -- no --> LOCK["Lock the bounded context, read the<br/>events sharing the command's tags"]:::step
    LOCK --> DECIDE{"decide(payload,<br/>matching events)"}:::decision
    DECIDE -- Rejected --> REJ(["accepted: false,<br/>with a reason"]):::deny
    DECIDE -- Accepted --> WRITE["Append the events, encrypt sensitive fields,<br/>update projections: one transaction"]:::step
    WRITE --> DONE(["accepted: true"]):::allow

    classDef start fill:#1f4e79,stroke:#7fb3e6,color:#fff
    classDef decision fill:#3a3a5c,stroke:#9a9ad0,color:#fff
    classDef step fill:#2d3748,stroke:#718096,color:#fff
    classDef allow fill:#1e6b3a,stroke:#6fcf97,color:#fff
    classDef deny fill:#8b2635,stroke:#f2868f,color:#fff
    classDef hide fill:#6b5a1e,stroke:#e6c76f,color:#fff
</pre>

## Two ways in, two kinds of token

Everything that happens before `decide()` depends on who is calling, so it helps to know the two ways in.
People and services that use the application come in over GraphQL with a JWT from your identity provider,
which resolves to a Role and its grants. Narrow agents and automated callers come in over REST with an
`id.secret` token that is scoped to exactly one registered type, and optionally to one owner. An agent
that handles refunds can ask for refunds for that customer, and nothing else.

<pre class="mermaid">
flowchart LR
    subgraph GQL["GraphQL: HTTP and WebSocket"]
        direction LR
        JWT["Bearer JWT<br/>signed by your IdP"]:::step --> ROLE["Role<br/>matched on external_subject"]:::step
        ROLE --> GRANT["RoleAccessMapping<br/>level, scope, capabilities"]:::step
    end
    subgraph RST["REST"]
        direction LR
        TOK["Bearer id.secret"]:::step --> AT["AccessToken<br/>one type, optional owner scope"]:::step
    end
    GRANT --> BC[("Bounded context<br/>events, commands, projections")]:::store
    AT --> BC
    SUPER(["Superadmin"]):::start -. "creates Roles,<br/>bounded contexts, grants" .-> GRANT
    ADMIN(["Admin grant"]):::start -. "mints and revokes" .-> AT
    ADMIN -. "registers types" .-> BC

    classDef start fill:#1f4e79,stroke:#7fb3e6,color:#fff
    classDef step fill:#2d3748,stroke:#718096,color:#fff
    classDef store fill:#4a2d6b,stroke:#b79ae0,color:#fff
</pre>

The second track is the keyhole I described in the security post. What 0.2.0 changes is the first track:
what a grant can actually hold.

## Capabilities

Until now, a projection could be restricted to a team, and "the team" meant a Role whose *name* equalled a
string. That works until you look at it for long. A team was a naming convention, so every member's Role
had to be called `staff` and the real name was lost. An admin couldn't see that a projection required
anything. And the answer to someone outside the team was a distinct `not_on_required_team`, which told
them the projection existed. It was something I found missing, and looking closer, it was wrong in a few ways.

In 0.2.0 a grant holds named **capabilities**, and a projection or a private field can require one by
name. The rule I care about most is that **nothing implies a capability**: not an access level, not being
a superadmin, and no longer a Role's name. An admin has to be given a capability like anyone else. A
requirement nobody holds fails closed, and a caller without the capability doesn't get a refusal. They get
a schema in which the projection doesn't exist.

The second half of the design is who can hand them out, because that's where this kind of thing usually
goes wrong:

<pre class="mermaid">
flowchart TD
    A(["grantCapability or revokeCapability"]):::start --> W{"Who is calling?"}:::decision
    W -- Superadmin --> SUP["May change any grant's capabilities,<br/>its own included"]:::step
    W -- "Admin grant" --> ADM1{"Target grant is in the admin's<br/>own bounded context?"}:::decision
    ADM1 -- no --> D1["grant_not_active"]:::deny
    ADM1 -- yes --> ADM2{"Target is the admin's<br/>own grant?"}:::decision
    ADM2 -- yes --> D2["SelfGrantRefused"]:::deny
    ADM2 -- no --> ADM3{"Capability is in the admin's<br/>delegable set?"}:::decision
    ADM3 -- no --> D3["Refused"]:::deny
    ADM3 -- yes --> OK
    W -- "anyone else" --> D1
    SUP --> OK(["Applied, and recorded in the<br/>same transaction"]):::allow
    SETD["setDelegableCapabilities<br/>superadmin only"]:::step -. "defines" .-> ADM3

    classDef start fill:#1f4e79,stroke:#7fb3e6,color:#fff
    classDef decision fill:#3a3a5c,stroke:#9a9ad0,color:#fff
    classDef step fill:#2d3748,stroke:#718096,color:#fff
    classDef allow fill:#1e6b3a,stroke:#6fcf97,color:#fff
    classDef deny fill:#8b2635,stroke:#f2868f,color:#fff
</pre>

A superadmin decides which capabilities a context admin may hand out, and the admin can hand those to
other grants in their own context, never to their own. So an admin can run a team without being able to
read what the team reads: handing out access and holding it are separate things. A grant holds at most 16
capabilities, and 16 is also the limit for what it may delegate.

If you're upgrading, the change in your code is a rename:

```rust
// 0.1
const TEAM_ONLY: Option<&'static str> = Some("staff");
// 0.2
const REQUIRES_CAPABILITY: Option<&'static str> = Some("staff");
```

The other half is no longer in Rust. Everyone who used to match the team's Role name now needs the
capability, granted by a superadmin:

```graphql
mutation {
  grantCapability(roleId: "ROLE_ID", boundedContext: "support", capability: "staff") {
    capabilities
  }
}
```

Until you do, the gated projection is simply not there for them, which is the safe way round.
`capabilityOverview` shows what is required against what is held, and a name that is held but not
required is usually a typo.

## An access trail

Capabilities live on a grant, and a grant is a row. A row that gets updated forgets. "Could this grant
read the staff projection on that date?" had no answer, and the only record of a change was a log line.
In an event-sourced library that felt a bit silly.

So in 0.2.0 every change to who holds what is also an event, in the `admin` bounded context, written in
the same transaction as the change. If the event can't be written, the change isn't made. That covers
grants, revokes, capability and delegation changes, and the sharing of a record's private fields, and the
events carry ids only, never names, so there's nothing a person could ask to have forgotten.
`capabilityHistory(roleId, boundedContext, asOf)` answers what a grant held at a given moment, and says
`known: false` for any time before the trail began. Grants from before the upgrade get one baseline event
at startup, so history starts honestly at the upgrade and doesn't pretend to go further back.

This is the same idea as the wallet, turned on skilj itself. A balance is a fold over the events that
share a wallet's tag, and what a grant held on a given date is a fold over the events up to that date.
In both cases nothing is looked up in a mutable place and trusted: there is a record of what happened,
and the answer is computed from it. That's the real argument for keeping the decisions pure. Once the
decision is a function of recorded facts, the same facts can answer the questions you'll ask later, and
an auditor's question about access is no different from a customer's question about a balance.

Not everything is recorded. Denied attempts aren't, nor are reads, nor the other admin operations such as
minting tokens or registering types. The
[design log](https://github.com/gklijs/SkilJ/blob/main/docs/architecture.md#access-trail) lists the gaps.

## Keys that stay out of the process

The other large piece started with a question in the release review: could the master key be rotated?
The answer was no. It was 32 bytes handed to the builder, so it lived in the process, and every data key
was sealed under it.

Now a bounded context can have a key of its own at a key provider, and **deleting a tenant can be a
cryptographic erasure**. Once nothing uses the key and a grace period has passed, skilj deletes it at the
provider, and whatever that tenant encrypted is noise. A key you brought yourself, such as a customer's,
is followed and rotated at the provider but never retired or deleted by skilj.

The rest follows from moving the key out. With Vault or OpenBao Transit the key never enters skilj at
all, and there's a key file for local use. Rotation needs no restart, either on a schedule or at once if
a key leaks, and after the grace period the old versions are retired at the provider, so they're not just
unused but unusable. Every step is an event in the `admin` context too.

## Also in 0.2.0

- **Ordered batches.** Up to 100 commands or external events in one call, decided in the order given.
  It isn't a transaction, and a rejected item doesn't stop the ones after it. From a single caller that
  reaches the throughput of many concurrent ones, and the Kafka, AMQP and NATS bridges use it.
- **Local mode now runs with fsync on.** It had it off, which meant a power cut could lose committed
  data. It's the kind of thing a quickstart shouldn't do to anyone.
- **TLS for the Kafka bridge** is a feature flag that is on by default, so `SASL_SSL` no longer needs a
  matching `rdkafka` line in your own manifest.
- **The template builds on arm64**, and `skilj-tui`'s live views work over `wss://`.

## Upgrading

It isn't a rolling upgrade. 0.2.0 writes events with a new origin as soon as it starts, and 0.1.x panics
when it reads one it doesn't know, so stop every 0.1.x instance before starting the first 0.2.0 one, and
don't go back. The renames (`TEAM_ONLY` to `REQUIRES_CAPABILITY`, the `team` private field to
`capability`) and the key provider migration are in the
[changelog](https://github.com/gklijs/SkilJ/blob/main/CHANGELOG.md#020---2026-10-27).

The design log is now at section 230, and sections 228 to 230 are the ones behind this release. It's
still pre-1.0, built by one person, and hasn't had an independent security audit. If you find something
that isn't written down, I'd like to hear about it, and a real hole goes through
[GitHub's private vulnerability reporting](https://github.com/gklijs/SkilJ/security/advisories/new).

- GitHub: [gklijs/SkilJ](https://github.com/gklijs/SkilJ)
- crates.io: [skilj](https://crates.io/crates/skilj)

<script>
import("https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs").then(function (m) {
  var dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  m.default.initialize({ startOnLoad: false, theme: dark ? "dark" : "default" });
  m.default.run({ querySelector: "pre.mermaid" });
});
</script>

*Photo: [One at a time](/photos/2026/one-at-a-time), by me.*

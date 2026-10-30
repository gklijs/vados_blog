Every weekday at 15:15 a small newsroom opens on my machine. It gathers the news on two topics I care
about, neurodiversity and basic income, has a local model summarise it, and sends me an email digest. It
also writes a LinkedIn post and draws an illustration to go with it. Nobody is there to press a button,
and the whole operation is described in a single [swamp](https://github.com/swamp-club/swamp) workflow.

I made a short video about it, in the deadpan voice of a startup pitch deck:

<iframe src="https://www.youtube-nocookie.com/embed/s8nC8lIAcB8" title="We replaced the newsroom with one YAML file"
  loading="lazy" allowfullscreen
  allow="accelerometer; encrypted-media; picture-in-picture"
  style="aspect-ratio:16/9;width:100%;border:0"></iframe>

(The video was generated from the repository itself with a Claude Code skill, so the step names and the
incident in it are the real ones.)

## One body, two topics

The interesting part isn't the schedule, it's that there is only one pipeline. A workflow called
`daily-topic-digest` does all the work, and takes the topic as input: a slug, a display name, an accent
colour for the email, search terms for Bluesky, and the prompts for the model. Each topic then has a thin
parent workflow that supplies those inputs and owns its own trigger:

```yaml
trigger:
  schedule: "15 15 * * 1-5"
```

That's the cron line from the video. Adding a third topic means writing another thin parent, not copying
a pipeline. Changing how the digest works means changing it once.

## What happens at 15:15

The shared workflow runs in a few steps:

- **Gather.** Three jobs run side by side: the RSS and Atom feeds of the topic, a Bluesky search
  (original posts only, no replies, from the last week), and a search on X. The social sources are
  allowed to fail, because a digest without them is still a digest.
- **Summarise.** For every source, the articles that are genuinely new get a summary from a local model
  through Ollama. Articles seen on a previous day are skipped.
- **Write and send.** The model writes a short intro grounded in that day's headlines, and a separate
  standalone LinkedIn post that carries its own links. The digest goes out by email, and the post is
  published.
- **Illustrate.** A local Stable Diffusion model (SDXL) draws an editorial illustration, fresh on each
  run, which is attached to both the post and the email.

The illustration is best-effort. If the GPU is busy or unavailable, the post and the email go out as text
only, instead of not going out at all. The text steps retry for a few minutes for the same reason, so an
Ollama that is still starting up doesn't cost me a day.

<figure>
  <div style="display:flex;gap:1rem;flex-wrap:wrap">
    <img src="/img/tech/digest-basic-income-w632.webp"
         srcset="/img/tech/digest-basic-income-w425.webp 425w, /img/tech/digest-basic-income-w632.webp 632w, /img/tech/digest-basic-income-w986.webp 986w"
         sizes="(min-width: 800px) 372px, 100vw" width="632" height="632" loading="lazy"
         style="flex:1 1 16rem;min-width:0;height:auto"
         alt="Abstract illustration of overlapping geometric shapes in soft blue, grey and peach, with a transparent net stretched across them like a safety net">
    <img src="/img/tech/digest-neurodiversity-w632.webp"
         srcset="/img/tech/digest-neurodiversity-w425.webp 425w, /img/tech/digest-neurodiversity-w632.webp 632w, /img/tech/digest-neurodiversity-w986.webp 986w"
         sizes="(min-width: 800px) 372px, 100vw" width="632" height="632" loading="lazy"
         style="flex:1 1 16rem;min-width:0;height:auto"
         alt="Abstract illustration of flowing, overlapping shapes in orange, red, navy and pale blue">
  </div>
  <figcaption>The two illustrations from 29 October, for basic income and neurodiversity. Both were drawn by SDXL on my own GPU in about twenty seconds.</figcaption>
</figure>

## The day it failed silently

The video has an incident log, and it's the part I like most, because it's true. The workflow was set to
use `qwen3.6:35b-a3b` for the local model. On 2026-08-31 that model was removed from the Ollama server,
and the workflow failed silently instead of telling me.

The fix was to point the model setting at `qwen3:14b`. The lesson is the usual one: a pipeline
that degrades gracefully is nice right until you need to know that it did. A best-effort step should say
loudly that it was skipped, or you find out weeks later, from the quality of the emails.

## Why a workflow, and not a script

I could have written this as a script and a crontab line. What I get from describing it as a workflow is
that the shape of the thing is visible: which jobs depend on which, which ones may fail, which ones
retry. The description of each step sits next to the step, including the reasons for choices that would
otherwise live in my head, like why the Bluesky search only looks at the last week. (Bluesky ranks by
likes, so without that limit the same viral posts came back every day.)

The result is small enough to explain in twenty seconds, which is exactly what the video does.

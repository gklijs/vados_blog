This morning I walked through the Bossche Broek. To get to the other side of the water there you take a small ferry, and you have to power it yourself, by driving a chain. Nobody does it for you. If you stop, you float.

It was a good walk to think over last Thursday, when I was at [J-Fall](https://jfall.nl), the conference of the Dutch Java user group. Most of what stayed with me was about AI, and about what is left for us to do.

## An agent is not magic

One of the speakers made a simple agent on stage. The code was Java, the model a local one running in Ollama, and the agent created a very simple Node app and then edited it.

That demystified it for me. A harness is ordinary code around a model: it gives the model a few tools, runs what the model asks for, and feeds the result back. That's the loop.

It ties in with what I'm building on the side, an agent for projects that use [skilj](https://github.com/gklijs/SkilJ). It is also designed for local models with Ollama. Everything that is the same in every skilj project is plain Rust code, and a model only does the parts that need judgement or new text. Checking a project and diagnosing a problem use no model at all. After that talk I'm more convinced that this is the right split: the less you leave to the model, the less there is to get wrong.

## Don't be a meat proxy

Venkat Subramaniam warned us not to become meat proxies, and to keep thinking critically. The term comes from [a post by Niklas Gruhn](https://simonwillison.net/2026/Aug/3/dont-be-a-meat-proxy/): a meat proxy is someone who passes on what an AI wrote without reading or understanding it. If that's all you do, the other person could have asked the AI themselves.

Venkat has been saying this for a while. In [a keynote in April](https://www.globalnerdy.com/?p=51274) he said that programming is about thinking, not typing, and that "we can't go faster with ignorance".

I agree with him. The typing was never the hard part.

The worry itself is old. In Plato's Phaedrus, Socrates tells of an Egyptian king who is offered the invention of writing, and refuses to be impressed. People will stop using their memory, he says, and they will seem to know a lot while knowing little. That was about 2,400 years ago. Writing turned out fine, but not for the people who only copied. It worked for those who kept thinking about what they read.

There is a running joke about this now. To get it right with an agent, you end your prompt with "make no mistakes". Muse was way ahead here. In Sunburn, from 1999, they already sang "make no mistake". Maybe the LLM is just a big Muse fan.

It's funny because it doesn't work. Someone still has to check for the mistakes.

## Staying relevant

The talk by Bruno Souza was great. It was about how to stay relevant, and what I remember comes down to three things: keep in the loop, keep thinking, and be at the right place.

His example of the last one: they still make Polaroids in front of the Sagrada Família. Everyone there has a camera in their pocket, and still someone makes a living with instant photos, by standing in the right spot.

## A factory with gates

At the coaching tables I talked with Urs Peter. Software factories came up, where a piece of work goes from an issue to a reviewed change through fixed stages, with agents doing most of the steps. He said it is one of the things to invest time in. Start with your team, build trust, and then look for adoption across the company.

I don't have a team for skilj, so I started with myself. I set up the software factory of [swamp](https://github.com/swamp-club/swamp) for it. An issue becomes a brief, then a plan, the plan is reviewed, the change is made, the checks run, the code is reviewed, and then it is handed to me. The factory never commits, pushes or approves. Those stay with me, and the run stops at a few gates until I say it can go on.

The first issue through it was a deadlock, when a command came in while its bounded context was being deleted. It felt smooth, and I felt well in control. What I liked most is that it uses different models for coding and for reviewing, automatically. That is often done, but often by hand.

It is the ferry again. The chain is there, and the crossing is easy. But it only moves when I pull.

## A floor or a leash

Yesterday I watched Captain Laserhawk: A Blood Dragon Remix on Netflix. It's a bit crazy, but nice, with Rayman as a news anchor. In that world basic income is used to control people.

I follow basic income closely. I even run two small news sites about it, [one in English](https://basic-income.gklijs.tech) and [one in Dutch](https://basisinkomen.gklijs.tech). What I like about it is the opposite of control. It gives simplicity and assurance, especially to people who are less able or less well educated. The same money can be a floor to stand on or a leash, and the difference is in the conditions.

Hannah Arendt saw the question coming in 1958. In The Human Condition she wrote that automation could leave us with "a society of laborers without labor", people freed from work who have nothing else they know how to do. If agents take over more of the work, the money is one question. What we do with ourselves is the other one.

In [The same film](/society/2026/the-same-film) I wrote about choosing hope over fear. I think the answers from J-Fall are a hopeful version: keep in the loop, keep thinking, be at the right place. And I hope there will be a floor under the people for whom that is harder.

This post was written with an LLM again. It asked me a list of questions first, and the answers are mine. I still had to pull the chain.

*Photo: [Heron at the reeds](/photos/2026/heron-at-the-reeds), by me, taken on that walk. It stood still and kept watching the whole time I was there.*

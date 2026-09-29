# Pulse campaigns

Ideas for campaigns that can be hooked into Pulse, ranked by **relevance**
(how directly they plug into the weekly edition) and **efficacy** (reach and
traction for the effort). Top of each list = do first.

## The principle: one tellable thing every week

This is the heart of the strategy. No random commits: a weekly heartbeat.
Every week at least one publicly tellable thing must happen:

- Openapi MCP v0.x
- New Python SDK feature
- New CLI command
- New Agent Skill
- New example
- New integration
- New tutorial
- New benchmark
- New template

This creates something extremely important: **newsworthiness**.
You do not have to invent a project every week.
You have to have something to tell every week.

## Already live in Pulse

- API of the Week — `content/apis.yml`, synced from the API library.
- Developer spotlight — `developers` queue, public members of the organization.
- Contributor spotlight — `contributors` queue, from openapi/contributors.
- Discussion of the week — `content/topics.yml`, open discussions.
- Blog relay — `news` and `insights` queues, from openapi.com/blog.

## Tier 1 — new weekly slots in the edition

Each one is a new queue or slot in the card: highest relevance, low cost once
the queue exists.

1. **1 Useful Thing a Week** — a new example/tool/skill/template every week.
   It *is* the principle above made into a slot: the "shipped this week" line.
   Pairs with a weekly or biweekly release of at least one flagship, and with
   readable release notes, not plain commit lists.
2. **Repository of the Week** — every week relaunch and improve a different
   repo. A `repos` queue; the pinned repositories and the social preview image
   follow the campaign.
3. **Use Case of the Week** — start from the problem, not from the product.
   Fed by "Build X in 5 minutes" tutorials and 20-30 line Openapi Recipes.
4. **MCP/API Project of the Week** — spotlight an external project from the
   micro-communities below. Brings their audience in; see *Traffic pools*.
5. **Good First Issue Friday** — publish very simple issues regularly. Pulse
   already aims at recurring issues; the edition links the issue of the week.
6. **Contributor of the Month** + **Contributor Hall of Fame** — extends the
   contributors queue to a monthly award and a permanent page.
7. **Open Source Radar** — have similar pieces of software voted against each
   other inside the community (e.g. AI knowledge bases). Runs as a Discussions
   poll linked from the edition; same mechanism for **Vote for next
   integration**.
8. **Monthly challenge** — "build something using this API"; the API of the
   Week can become the API of the Month's challenge.
9. **"What we shipped this month"** — a monthly roll-up generated from the
   weekly editions; later the monthly developer newsletter.

## Tier 2 — content engines that feed the slots

They produce what Tier 1 shows off. Ranked by how fast one item reaches a
working result for a developer.

1. MCP recipes — Claude/Cursor/VS Code/agent + Openapi.
2. Agent Skills marketplace — many small, very specific skills.
3. 30-second demos — very short GIFs/videos directly in the READMEs.
4. Openapi Recipes — copy-paste recipes of 20-30 lines.
5. "Build X in 5 minutes" — extremely short tutorials.
6. Openapi Playground — examples that run immediately.
7. GitHub Codespaces ready — "Run this example" with one click.
8. Examples deployable to Vercel/Render/Cloudflare with one click.
9. Docker-first examples — `docker run` and the user is off.
10. Template repository with a "Use this template" button.
11. A public demo repository with no complicated setup.
12. Natural language → API call demo.
13. "Ask your company registry" AI demo.
14. n8n nodes/templates.
15. LangChain integration.
16. LlamaIndex integration.
17. CrewAI integration.
18. Zapier examples.
19. Starter kits — Python, PHP, JS, Rust.
20. Framework examples — Laravel, Django, FastAPI, Next.js, Symfony.
21. Public Postman collections.
22. Public Bruno collections.
23. OpenAPI specification files, easy to download and reuse.
24. llms.txt / agent-friendly docs.
25. Ready-made GitHub Copilot instructions for using Openapi.
26. A prompt library for using Openapi with LLMs.
27. CLI one-liners — a repository of useful commands.
28. Awesome Openapi — a curated repository of tools, examples and integrations.
29. "100 things you can build with Openapi" — a list that keeps growing.
30. Community examples — accept examples from users.
31. AI-generated application examples, but reviewed and actually working.
32. Absurd/fun demos every now and then: excellent for sharing.
33. Public dogfooding: Openapi uses Openapi to build Openapi tools.
34. Turn support questions into documentation.
35. Turn every interesting bug into technical content.
36. Fully reproducible case studies.
37. Comparison pages: "Openapi MCP vs direct REST".
38. Migration guides.
39. A cookbook of common errors.
40. Indexable technical FAQs.
41. SDK performance benchmarks.
42. Cross-language SDK benchmark.
43. Bundle-size benchmark for JS.
44. Latency examples.

## Tier 3 — distribution: where each edition gets relayed

Ranked by fit with developer audiences; one edition, many channels.

1. The micro-communities in *Traffic pools* below.
2. LinkedIn developer posts, not corporate ones.
3. DEV.to articles.
4. Reddit, by taking part in the communities instead of spamming links.
5. Hacker News Show HN when something genuinely interesting ships.
6. Technical YouTube Shorts derived from the demos.
7. Stack Overflow: useful answers where Openapi is relevant, without
   artificial marketing.
8. Hashnode articles.
9. A monthly developer newsletter.
10. Product Hunt for tools standalone enough to carry it.
11. Indie Hackers, to tell the story of experiments.
12. Technical guest posts.

## Tier 4 — bigger bets: good material for Pulse once they exist

Higher effort; each one, when shipped, is a strong "Useful Thing" or a Show HN.

1. Openapi Labs — a namespace for experiments that could go viral.
2. OpenAPI → MCP generator, if technically applicable.
3. OpenAPI → Agent Skill generator.
4. "Works with" matrix for Claude/Cursor/Copilot/etc.
5. MCP server leaderboard/compatibility matrix.
6. Agent benchmark: real tasks executed through Openapi.
7. GitHub Actions built on the Openapi APIs.
8. Webhook debugger.
9. Webhook local forwarder.
10. Mock server.
11. Fake/sandbox data generator.
12. API request inspector.
13. Open-source API status CLI.
14. API health checker.
15. API explorer CLI.
16. OpenAPI → typed client generator.
17. Schema → code generator.
18. A developer toolbox repository with small tools.
19. VS Code extension.
20. JetBrains plugin, possibly community-driven.
21. Terraform provider, if there are sensible use cases.
22. PRs into external ecosystems to add Openapi integrations.
23. Collaborations with small OSS projects instead of chasing only the big ones.
24. Sponsor small strategic OSS maintainers.
25. Openapi online hackathon.
26. Occasional bounties for features/integrations.
27. Swag for significant contributors, if the client puts up a budget.
28. Developer ambassadors.
29. Campus/university: free APIs for educational projects.
30. Theses/university projects built on the APIs.
31. Public roadmap.
32. Request an Integration through a GitHub issue.
33. Request an SDK.
34. Publish ecosystem statistics.
35. Open-source annual report.

## Foundations — not campaigns, but they decide whether campaigns convert

Traffic that Pulse sends is wasted if the landing repo is not ready.

1. README benchmark: installation → example → result within the first screen.
2. Answer every issue quickly: community responsiveness as strategy.
3. GitHub Discussions as a technical community.
4. A developer-first organization profile README.
5. Kill/archive strategy — close dead repos so the organization looks alive
   and curated.
6. Repository descriptions written for search.
7. Obsessively curated GitHub Topics.
8. README SEO: use the terms developers actually search for.
9. Consistent naming across all repositories.
10. A very well kept changelog.
11. Consistent semantic releases.
12. README badges that are useful, not decorative.
13. Simple architecture diagrams in the READMEs.
14. Mermaid diagrams.
15. Multilingual READMEs only where they bring real discovery.

## Measurement — close the loop

1. Weekly metrics: stars, clones, visitors, contributors, referrals — a natural
   Pulse output next to each edition.
2. Note down what generates each star/follower spike.
3. Double down only on what demonstrates traction.
4. Informal A/B testing of the READMEs.

## Traffic pools — the micro-communities to go after first

| Micro-community | Why it is interesting | Openapi strategy |
| --- | --- | --- |
| Model Context Protocol Show & Tell | very many small MCP projects | MCP/API Project of the Week |
| GitHub MCP Server Show & Tell | small MCP/AI projects | Open Source AI + API |
| APIs.guru / OpenAPI Directory | people who publish/catalogue APIs | API of the Week, Certified API |
| Hoppscotch Discussions | API developers/tooling | API tooling, polls, workflows |
| TypeSpec OpenAPI3 | API design, schemas, generators | cross-project technical discussions |
| Etsy Open API Show & Tell | developers building on real APIs | Show us what you built |
| OpenAI Evals Show & Tell | independent AI tools | Open Source AI spotlight |

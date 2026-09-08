<div align="center">

# 🤖 GitHub Repo Summarizer

**Point it at any GitHub repository. Get an instant, structured report.**

A multi-agent system that explores a repo's file tree, issues, pull requests, and branches — then renders it all as a clean, GitHub-styled documentation page.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.1-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.55.2-FF5A50?style=flat-square)](https://github.com/crewAIInc/crewAI)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-8E75B2?style=flat-square&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![MCP](https://img.shields.io/badge/MCP-github--mcp--server-000000?style=flat-square&logo=github&logoColor=white)](https://github.com/github/github-mcp-server)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

[Quick Start](#-quick-start) · [How It Works](#-how-it-works) · [Configuration](#-configuration) · [Troubleshooting](#-troubleshooting)

</div>

---

## ✨ What it does

Paste a repository URL and four AI agents go to work in sequence, each with its own GitHub tool:

| Agent | Reports on |
|:--|:--|
| 🗂️ **Structure Auditor** | Full file tree, rendered as a browsable hierarchy with links |
| 🟢 **Issue Analyst** | Open issues, grouped by theme, with prioritization advice |
| 🟣 **Pull Request Lister** | 5 most recent PRs, categorized, with review feedback |
| 🟡 **Branch Reporter** | Branches, categorized, with branching-strategy recommendations |

Results land on a single page styled with GitHub's own Primer design language — dark/light themes, collapsible cards, and a real file browser.

---

## 🚀 Quick Start

> **Requirements:** [Docker](https://docs.docker.com/get-docker/) with Compose. Nothing else — Python, Go, and the MCP server are all built inside the image.

### 1. Clone

```bash
git clone https://github.com/manojmeruva/crewai-agents-github-summarizer.git
cd crewai-agents-github-summarizer
```

### 2. Add your keys

```bash
cp .env.example .env
```

Open `.env` and fill in both values:

```ini
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
GOOGLE_API_KEY=your_gemini_key_here
```

<details>
<summary><b>Where do I get these?</b> (click to expand)</summary>

<br>

**`GITHUB_PERSONAL_ACCESS_TOKEN`** — [Create one here](https://github.com/settings/tokens)

A classic token with the **`public_repo`** scope is enough for public repositories. Add the full **`repo`** scope only if you want to analyze private ones. The token is used read-only.

**`GOOGLE_API_KEY`** — [Get one from Google AI Studio](https://aistudio.google.com/app/apikey)

Free tier is sufficient. The project uses `gemini-2.5-flash`.

</details>

### 3. Run

```bash
docker compose up --build
```

First build takes a few minutes (it compiles the Go MCP server from source). After that, startup is seconds.

### 4. Open

Visit **[http://localhost:8000](http://localhost:8000)**, paste a repository URL, and hit **Generate documentation**.

> ⏱️ A run takes **30 seconds to ~4 minutes** depending on repository size — four agents run sequentially, each making live GitHub API calls.

---

## 🧠 How It Works

```
                    ┌─────────────────────┐
   Repo URL  ──────▶│   Django  (web UI)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   CrewAI  (crew)    │   sequential process
                    └──────────┬──────────┘
                               │
       ┌───────────┬───────────┼───────────┬───────────┐
       ▼           ▼           ▼           ▼           │
   Structure     Issue        PR        Branch         │  4 agents
    Auditor     Analyst     Lister     Reporter        │  Gemini 2.5 Flash
       │           │           │           │           │
       └───────────┴───────────┴───────────┴───────────┘
                               │  each calls a tool via
                    ┌──────────▼──────────┐
                    │  mcpcurl  ──stdio──▶│  github-mcp-server v0.5.0
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │     GitHub API      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  generated_docs/    │  4 markdown files
                    │  → summary.md       │  + combined summary
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Primer-styled UI   │  cards · file browser · themes
                    └─────────────────────┘
```

Each agent owns exactly one tool. Tools shell out to **`mcpcurl`**, which speaks JSON-RPC over stdio to **`github-mcp-server`** — GitHub's official [Model Context Protocol](https://modelcontextprotocol.io/) server. Every task writes a markdown file to `generated_docs/`, and those get combined into `summary.md` for rendering.

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|:--|:--|:--|
| Web framework | [Django](https://www.djangoproject.com/) | `5.2.1` |
| Agent orchestration | [CrewAI](https://github.com/crewAIInc/crewAI) | `0.55.2` |
| LLM | [Google Gemini](https://ai.google.dev/) via `langchain-google-genai` | `gemini-2.5-flash` |
| LLM plumbing | [LangChain](https://www.langchain.com/) | `0.2.16` |
| GitHub access | [github-mcp-server](https://github.com/github/github-mcp-server) | `v0.5.0` (pinned) |
| Markdown rendering | `markdown` | `3.7` |
| Runtime | Python | `3.11-slim` |
| MCP build stage | Go | `1.25-bookworm` |
| Packaging | Docker Compose | — |

<details>
<summary><b>Why <code>github-mcp-server</code> is pinned to v0.5.0</b></summary>

<br>

Versions after `v0.5.0` moved `owner`/`repo` from CLI flags into MCP headers (`x-mcp-header`) and switched `list_issues` to cursor pagination (`--after` instead of `--page`). The tool wrappers in `mcp_manager/tools/` pass the older flag style, so newer builds fail with `unknown flag: --owner`. The pin is deliberate — see the comment in the [`Dockerfile`](Dockerfile).

</details>

---

## ⚙️ Configuration

| Variable | Required | Purpose |
|:--|:--:|:--|
| `GITHUB_PERSONAL_ACCESS_TOKEN` | ✅ | Reads repo contents, issues, PRs, and branches |
| `GOOGLE_API_KEY` | ✅ | Powers the four agents via Gemini |

The MCP server runs with the `repos,issues,pull_requests,code_security` toolsets enabled.

**Persisted volumes** (via `docker-compose.yml`): `generated_docs/` and `db.sqlite3` are mounted from the host, so generated reports survive container restarts.

---

## 🗂️ Project Layout

```
mcp_integration/
├── mcp_manager/
│   ├── agents/agents.py      # 4 agent definitions + Gemini LLM config
│   ├── tasks/tasks.py        # task prompts + output_file targets
│   ├── crews/crew.py         # sequential crew assembly
│   ├── tools/                # one MCP wrapper per agent
│   │   ├── directory_scanner.py
│   │   ├── issue_retriever.py
│   │   ├── pull_request_lister.py
│   │   └── branch_lister.py
│   ├── templates/            # Primer-styled UI
│   ├── utils.py              # mcpcurl subprocess bridge
│   └── views.py              # request handling + markdown→HTML
└── generated_docs/           # agent output lands here
```

---

## 🧯 Troubleshooting

<details>
<summary><b><code>unknown flag: --owner</code></b></summary>

<br>

The MCP server was built from a version newer than `v0.5.0`. Rebuild without cache so the pinned tag is fetched:

```bash
docker compose build --no-cache
```

</details>

<details>
<summary><b>Report shows the wrong repository, or only one section</b></summary>

<br>

Stale files in `generated_docs/` are being combined into the summary. Clear them and re-run:

```bash
rm -f mcp_integration/generated_docs/*.md
```

</details>

<details>
<summary><b>Build fails or the daemon hangs on <code>docker compose build</code></b></summary>

<br>

Usually low disk — the Go build stage needs several GB. Reclaim space with:

```bash
docker builder prune -af
docker image prune -af
```

</details>

<details>
<summary><b>Empty or truncated reports</b></summary>

<br>

Check that both keys in `.env` are set and valid. Gemini's free tier is rate-limited, so rapid consecutive runs on large repositories can get throttled. Container logs show the failing call:

```bash
docker compose logs -f
```

</details>

---

## 🗺️ Roadmap

- [ ] Stream agent progress to the UI instead of blocking on the request
- [ ] Export reports as Markdown / PDF
- [ ] Cache results per repository + commit SHA
- [ ] Support self-hosted GitHub Enterprise
- [ ] Swappable LLM backends (OpenAI, Anthropic, local models)

---

## 🤝 Contributing

Contributions are welcome. Fork the repo, create a feature branch, and open a pull request.

```bash
git checkout -b feature/your-idea
git commit -m "Add your idea"
git push origin feature/your-idea
```

Found a bug or have an idea? [Open an issue](https://github.com/manojmeruva/crewai-agents-github-summarizer/issues).

---

## 📄 License

Released under the [MIT License](LICENSE).

---

<div align="center">

**If this project helped you, consider giving it a ⭐ — it genuinely helps others find it.**

Built with [CrewAI](https://github.com/crewAIInc/crewAI) · [Django](https://www.djangoproject.com/) · [GitHub MCP Server](https://github.com/github/github-mcp-server)

</div>

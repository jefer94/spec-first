# Spec Guard

> A GitHub Action that enforces Spec-Driven Development (SDD) on pull requests.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Security](https://github.com/YOUR_ORG/spec-first/actions/workflows/security.yml/badge.svg)](https://github.com/YOUR_ORG/spec-first/actions/workflows/security.yml)

## What It Does

Spec Guard ensures that every code change starts with a specification. It uses an AI-powered LangChain agent (via OpenRouter) to review code against accepted specs, saving senior engineers time while enforcing quality.

### Workflow

```
1. Contributor opens PR with specs (.md, .feature)
   └─ Gate: Only spec/doc files allowed — code PRs are rejected

2. Authorized reviewer accepts specs (adds label)
   └─ Guard: Only maintain/admin roles can accept

3. Contributor opens implementation PR referencing spec PR
   └─ AI Review: LangChain agent validates code against specs
       ├─ ✅ Compliant → assigns senior reviewer
       └─ ❌ Violations → posts structured feedback
```

### Key Features

- **SDD Enforcement** — PRs without specs are auto-closed
- **BDD Support** — AI references Given/When/Then scenarios in feedback
- **Senior Time Savings** — AI pre-validates before human review
- **Structured Feedback** — Spec compliance first, then implementation alternatives with trade-offs
- **Prompt Injection Protection** — Sanitization railway prevents code from manipulating AI
- **Sandboxed Agent** — LangChain agent isolated from filesystem and secrets

## Quick Start

```yaml
# .github/workflows/spec-guard.yml
name: Spec Guard
on:
  pull_request:
    types: [opened, synchronize, labeled]

jobs:
  spec-guard:
    runs-on: ubuntu-latest
    steps:
      - uses: jefer94/spec-first@v1
        with:
          model: 'moonshotai/kimi-k2.5'
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `model` | yes | — | OpenRouter model identifier |
| `spec_extensions` | no | `.md,.feature` | File extensions treated as specs |
| `doc_extensions` | no | `.txt,.rst,.adoc` | File extensions treated as docs |
| `accepted_tag` | no | `specs-accepted` | Label for accepted specs |
| `ai_review_tag` | no | `ai-review` | Label to trigger AI review |
| `senior_tag` | no | `senior-review` | Label added on AI approval |
| `authorized_roles` | no | `maintain,admin` | Roles allowed to accept specs |
| `senior_members` | no | — | Usernames for senior assignment (random if empty) |
| `review_on_pr` | no | `false` | Auto-trigger AI review on code PRs |
| `msg_no_specs` | no | (built-in) | Custom message: PR has no specs |
| `msg_mixed_pr` | no | (built-in) | Custom message: PR mixes specs and code |
| `msg_unauthorized_tag` | no | (built-in) | Custom message: unauthorized tag |
| `msg_no_specs_on_tag` | no | (built-in) | Custom message: tag on code-only PR |
| `msg_ai_failure` | no | (built-in) | Custom message: AI review failure |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | yes | Your OpenRouter API key |
| `GITHUB_TOKEN` | yes | Provided automatically by GitHub Actions |

## How AI Review Works

The reviewer is a LangChain agent with tools:

| Tool | Purpose |
|------|---------|
| `read_file` | Read full file content from PR branch for context |
| `list_changed_files` | List all changed files with status |
| `read_spec` | Load accepted spec files for comparison |
| `get_repo_structure` | Inspect repo tree for architecture context |

The agent receives the diff as primary input and uses tools to gather context before producing a structured verdict.

## Security

- **Prompt injection railway** — All inputs sanitized before reaching the LLM
- **Sandboxed agent** — No filesystem access, no arbitrary network, env-only API key
- **Secret isolation** — `GITHUB_TOKEN` never reaches the LLM, only used in GitHub client layer
- **Size limits** — Tool outputs truncated to prevent context overflow

## Specifications

All behavior is specified in `specs/` with Given/When/Then scenarios and tested with Behave:

| Domain | Spec | Feature |
|--------|------|---------|
| Configuration | [`specs/configuration.md`](specs/configuration.md) | [`features/configuration.feature`](features/configuration.feature) |
| PR Gate | [`specs/pr-gate.md`](specs/pr-gate.md) | [`features/pr_gate.feature`](features/pr_gate.feature) |
| Tag Guard | [`specs/tag-guard.md`](specs/tag-guard.md) | [`features/tag_guard.feature`](features/tag_guard.feature) |
| AI Review | [`specs/ai-review.md`](specs/ai-review.md) | [`features/ai_review.feature`](features/ai_review.feature) |
| Feedback | [`specs/feedback-quality.md`](specs/feedback-quality.md) | [`features/feedback_quality.feature`](features/feedback_quality.feature) |
| Security | [`specs/security.md`](specs/security.md) | [`features/security.feature`](features/security.feature) |

## Tech Stack

- **Python 3.14** — Runtime
- **LangChain + langchain-openai** — AI agent with tools
- **OpenRouter** — LLM provider
- **PyGithub** — GitHub API client
- **Behave** — BDD testing
- **Docker** — Action container (reproducible environment)

## License

[MIT](LICENSE)

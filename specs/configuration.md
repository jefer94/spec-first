# Configuration Specification

## Purpose

Define the inputs, environment variables, and defaults for the Spec Guard GitHub Action.

---

## Requirement: Action Inputs

The action MUST accept the following inputs via `action.yml`:

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `model` | yes | — | OpenRouter model identifier |
| `api_key` | yes (env) | — | OpenRouter API key (env: `OPENROUTER_API_KEY`) |
| `spec_extensions` | no | `.md,.feature` | Comma-separated file extensions treated as spec files |
| `doc_extensions` | no | `.txt,.rst,.adoc` | Comma-separated extensions treated as documentation |
| `accepted_tag` | no | `specs-accepted` | Label indicating specs were reviewed and accepted |
| `ai_review_tag` | no | `ai-review` | Label that triggers AI diff-vs-spec analysis |
| `senior_tag` | no | `senior-review` | Label added when AI approves and assigns a senior |
| `authorized_roles` | no | `maintain,admin` | Comma-separated GitHub roles allowed to apply accepted tag |
| `senior_members` | no | — | Comma-separated GitHub usernames eligible for senior assignment. If empty, assign randomly from repo collaborators with write+ access |
| `bypass_roles` | no | `maintain,admin` | Comma-separated GitHub roles that can bypass SDD enforcement entirely. Users with these roles may submit code-only PRs without specs. |
| `review_on_pr` | no | `false` | When `true`, automatically trigger AI review on code PRs that reference accepted specs (no manual `ai_review_tag` needed) |
| `msg_no_specs` | no | (built-in) | Rejection message when PR has no spec files |
| `msg_mixed_pr` | no | (built-in) | Rejection message when PR mixes specs and code |
| `msg_unauthorized_tag` | no | (built-in) | Rejection message when unauthorized user applies accepted tag |
| `msg_no_specs_on_tag` | no | (built-in) | Rejection message when accepted tag is applied to a code-only PR |
| `msg_ai_failure` | no | (built-in) | Message when AI review fails (token/API limits) |

### Scenario: Valid configuration

- GIVEN the workflow YAML provides `model` and `OPENROUTER_API_KEY` env
- WHEN the action initializes
- THEN it MUST parse all inputs with defaults applied
- AND validate that `model` is non-empty and `api_key` is non-empty

### Scenario: Missing required input

- GIVEN `model` or `api_key` is missing
- WHEN the action initializes
- THEN it MUST fail with a clear error message naming the missing input

---

## Requirement: Auto-create labels

The action MUST ensure that all configured labels (`accepted_tag`, `ai_review_tag`, `senior_tag`) exist in the repository before any workflow runs. If a label does not exist, the action SHALL create it automatically with a sensible default color and description.

### Scenario: Labels already exist

- GIVEN the repository already has labels matching `accepted_tag`, `ai_review_tag`, and `senior_tag`
- WHEN the action initializes
- THEN it MUST skip label creation
- AND proceed normally

### Scenario: Labels do not exist

- GIVEN the repository is missing one or more of the configured labels
- WHEN the action initializes
- THEN it MUST create the missing labels with default colors and descriptions
- AND log which labels were created

### Scenario: Custom tag names with auto-creation

- GIVEN the user overrides `accepted_tag` to `"approved-specs"`
- WHEN the action initializes and `"approved-specs"` does not exist in the repo
- THEN it MUST create the `"approved-specs"` label
- AND use it for all subsequent operations

# AI Review Specification (Diff vs Specs)

## Purpose

Provide AI-powered code review that validates implementation against accepted specs, saving senior engineer time while ensuring spec compliance.

---

## Requirement: Trigger AI review

When a PR has the `accepted_tag` AND the `ai_review_tag` is added, the system MUST perform an AI-powered review of the code diff against the accepted specs.

### Scenario: AI review triggered on labeled PR

- GIVEN a PR that has the `accepted_tag` label
- AND the PR contains code changes (implementation PR, not the spec PR)
- WHEN the `ai_review_tag` label is added
- THEN the action MUST fetch the accepted specs from the spec PR (linked or referenced)
- AND fetch the code diff from the current PR
- AND invoke the LangChain agent with the diff as primary input

### Scenario: AI review auto-triggered when review_on_pr is true

- GIVEN `review_on_pr` is set to `true`
- AND a PR references an accepted spec PR (e.g., `Implements #42`)
- AND the PR contains only code files (not a spec PR)
- WHEN the PR is opened or synchronized
- THEN the action MUST automatically invoke the AI review
- AND skip the manual `ai_review_tag` requirement

### Scenario: review_on_pr is false (default)

- GIVEN `review_on_pr` is set to `false` (default)
- AND a PR contains code changes referencing accepted specs
- WHEN the PR is opened or synchronized
- THEN the action MUST NOT auto-trigger AI review
- AND wait for the `ai_review_tag` to be manually added

---

## Requirement: LangChain tools for contextual review

The AI reviewer MUST be implemented as a LangChain agent with tools. The diff is the primary input. The agent SHALL use tools to gather additional context needed to understand whether the solution is good.

### Tool: read_file

The agent MAY read full file contents from the PR branch to understand code that the diff references but does not fully show.

### Tool: list_changed_files

The agent MAY list all changed files with their status (added, modified, deleted) to understand the scope of the change.

### Tool: read_spec

The agent MUST read the accepted spec files to compare requirements against the implementation.

### Tool: get_repo_structure

The agent MAY inspect the repository tree to understand where new files fit in the existing architecture.

### Scenario: Agent uses tools to gather context before judging

- GIVEN a diff that modifies an existing function
- WHEN the agent receives the diff as input
- THEN it SHOULD use `read_file` to see the full file for context
- AND use `read_spec` to load the relevant requirements
- AND produce a compliance verdict based on both the diff and the surrounding context

### Scenario: Agent handles large PRs with multiple files

- GIVEN a PR with changes across 10+ files
- WHEN the agent receives the diff
- THEN it SHOULD use `list_changed_files` to understand scope
- AND use `read_file` selectively on files relevant to spec requirements
- AND NOT attempt to load all files into a single prompt

---

## Requirement: AI review output — approval path

If the AI determines the code is spec-compliant, the system MUST assign a senior reviewer.

### Scenario: AI approves the implementation

- GIVEN the LLM analysis concludes the code satisfies the accepted specs
- WHEN the AI review completes
- THEN the action MUST add the `senior_tag` label
- AND assign a reviewer from `senior_members` (random if multiple, or from collaborators if empty)
- AND leave a comment summarizing: spec compliance confirmed, assigned to senior for final review
- AND the comment MUST include a brief per-file summary of what was reviewed

### Scenario: AI approves with minor observations

- GIVEN the LLM finds the code is spec-compliant but has non-blocking observations
- WHEN the AI review completes
- THEN the action MUST add the `senior_tag` label
- AND assign a senior reviewer
- AND leave a comment with: compliance confirmed, observations listed as non-blocking suggestions

---

## Requirement: AI review output — rejection path

If the AI determines the code is NOT spec-compliant, the system MUST leave feedback and request changes.

### Scenario: AI rejects the implementation

- GIVEN the LLM analysis finds spec violations
- WHEN the AI review completes
- THEN the action MUST remove the `ai_review_tag` label
- AND NOT add the `senior_tag`
- AND leave a detailed comment with:
  1. **Spec compliance issues**: which requirements are unmet, referencing specific scenarios
  2. **Implementation feedback**: alternative approaches with trade-offs
- AND the feedback MUST be constructive, referencing the spec requirement by name

### Scenario: AI review fails due to token/API limits

- GIVEN the diff exceeds the model's context window or the API call fails
- WHEN the AI review is attempted
- THEN the action MUST remove the `ai_review_tag`
- AND leave a comment using the `msg_ai_failure` template
- AND suggest manual review as fallback

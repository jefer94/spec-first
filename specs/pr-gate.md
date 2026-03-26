# PR Gate Specification (Content Classification)

## Purpose

Classify PR content to enforce strict SDD (test-first). Specs MUST be submitted and approved in a **separate PR** before any code PR is allowed. Spec-only PRs are always allowed. Code-only PRs and mixed code+specs PRs are rejected. Users with `bypass_roles` may skip enforcement entirely.

---

## Requirement: Content classification

The system MUST classify every PR's changed files into three categories: spec files (matching `spec_extensions`), doc files (matching `doc_extensions`), and code files (everything else).

### Scenario: PR contains only spec and doc files

- GIVEN a PR where all changed files match `spec_extensions` or `doc_extensions`
- WHEN the action runs on `pull_request.opened` or `pull_request.synchronize`
- THEN the PR MUST be allowed to proceed
- AND the action SHOULD add a comment acknowledging spec submission

### Scenario: PR contains code AND spec files together (rejected)

- GIVEN a PR where changed files include BOTH code files AND spec files
- AND the PR author's repository role is NOT in `bypass_roles`
- WHEN the action runs on `pull_request.opened` or `pull_request.synchronize`
- THEN the action MUST close the PR
- AND leave a comment using the `msg_mixed_pr` template
- AND the comment MUST explain that specs must be submitted and approved in a separate PR first

### Scenario: PR contains only code files (no specs)

- GIVEN a PR where changed files include code but zero files match `spec_extensions`
- AND the PR author's repository role is NOT in `bypass_roles`
- WHEN the action runs on `pull_request.opened` or `pull_request.synchronize`
- THEN the action MUST close the PR
- AND lock the conversation
- AND leave a comment using the `msg_no_specs` template, listing accepted extensions
- AND the comment MUST reference the project's SDD workflow

---

## Requirement: Bypass SDD enforcement

Users with roles listed in `bypass_roles` MUST be allowed to submit any PR regardless of content. This allows maintainers, owners, and seniors to push hotfixes or infrastructure changes without spec overhead.

### Scenario: Maintainer submits code-only PR

- GIVEN a PR author whose repository role is in `bypass_roles` (e.g., `maintain`)
- AND the PR contains only code files (no specs)
- WHEN the action runs on `pull_request.opened` or `pull_request.synchronize`
- THEN the PR MUST be allowed to proceed
- AND the action SHOULD add a comment noting SDD enforcement was bypassed due to the author's role

### Scenario: Admin submits code-only PR

- GIVEN a PR author whose repository role is `admin`
- AND `admin` is listed in `bypass_roles`
- AND the PR contains only code files
- WHEN the action runs on `pull_request.opened` or `pull_request.synchronize`
- THEN the PR MUST be allowed to proceed

### Scenario: Contributor cannot bypass

- GIVEN a PR author whose repository role is NOT in `bypass_roles` (e.g., `write` or `read`)
- AND the PR contains only code files
- WHEN the action runs on `pull_request.opened` or `pull_request.synchronize`
- THEN the action MUST close the PR
- AND leave a comment using the `msg_no_specs` template

### Scenario: Custom bypass_roles configuration

- GIVEN `bypass_roles` is set to `admin` only (removing `maintain`)
- AND a PR author has `maintain` role
- AND the PR contains only code files
- WHEN the action runs
- THEN the action MUST close the PR
- AND enforce SDD as the author's role is not in the custom `bypass_roles`

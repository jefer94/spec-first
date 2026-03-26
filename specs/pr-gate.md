# PR Gate Specification (Content Classification)

## Purpose

Classify PR content to enforce that specs come first. Only spec/doc files are allowed in the initial PR iteration. Code and specs MUST NOT be mixed.

---

## Requirement: Spec-only PR detection

The system MUST classify every PR's changed files into three categories: spec files (matching `spec_extensions`), doc files (matching `doc_extensions`), and code files (everything else).

### Scenario: PR contains only spec and doc files

- GIVEN a PR where all changed files match `spec_extensions` or `doc_extensions`
- WHEN the action runs on `pull_request.opened` or `pull_request.synchronize`
- THEN the PR MUST be allowed to proceed
- AND the action SHOULD add a comment acknowledging spec submission

### Scenario: PR contains no spec files at all

- GIVEN a PR where zero changed files match `spec_extensions`
- WHEN the action runs on `pull_request.opened` or `pull_request.synchronize`
- THEN the action MUST close the PR
- AND lock the conversation
- AND leave a comment using the `msg_no_specs` template, listing accepted extensions
- AND the comment MUST reference the project's SDD workflow

### Scenario: PR mixes spec files and code files in the same push

- GIVEN a PR where changed files include BOTH spec files AND code files
- WHEN the action runs on `pull_request.opened` or `pull_request.synchronize`
- THEN the action MUST close the PR
- AND lock the conversation
- AND leave a comment using the `msg_mixed_pr` template explaining: specs and code MUST NOT be submitted together

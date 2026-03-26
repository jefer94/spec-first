# Tag Guard Specification (Authorization)

## Purpose

Enforce that only authorized team roles can mark specs as accepted. Prevent unauthorized label manipulation.

---

## Requirement: Accepted tag authorization

Only users with roles listed in `authorized_roles` MUST be allowed to apply the `accepted_tag`. The system SHALL check the labeling user's repository permission level.

### Scenario: Authorized user applies accepted tag

- GIVEN a user with `maintain` or `admin` role on the repository
- WHEN that user adds the `accepted_tag` label to a PR
- THEN the action MUST allow the label to remain
- AND take no enforcement action

### Scenario: Unauthorized user applies accepted tag

- GIVEN a user whose repository role is NOT in `authorized_roles`
- WHEN that user adds the `accepted_tag` label to a PR
- THEN the action MUST remove the label
- AND close the PR
- AND leave a comment using the `msg_unauthorized_tag` template, naming the required roles

### Scenario: Authorized user applies accepted tag to a PR with no specs

- GIVEN a PR that contains only code files (no specs)
- WHEN an authorized user adds the `accepted_tag`
- THEN the action MUST remove the label
- AND close the PR
- AND leave a comment using the `msg_no_specs_on_tag` template

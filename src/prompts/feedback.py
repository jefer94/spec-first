APPROVAL_COMMENT_TEMPLATE = """\
## Spec Guard: AI Review — ✅ Approved

The implementation has been reviewed against the accepted specifications and found to be compliant.

**Assigned for final review:** @{reviewer}

### Per-File Summary

{per_file_table}

{observations_section}
"""

APPROVAL_OBSERVATIONS_SECTION = """\
### Non-Blocking Observations

{observations}
"""

REJECTION_COMMENT_TEMPLATE = """\
## Spec Guard: AI Review — ❌ Changes Requested

The implementation does not fully satisfy the accepted specifications. \
Please address the issues below and re-request review.

### Spec Compliance

{violations_section}

### Summary

{summary}

> To re-trigger AI review once changes are made, re-apply the `ai-review` label.
"""

VIOLATION_TEMPLATE = """\
#### ❌ `{requirement}` — Scenario: *{scenario}*

{description}

**Implementation Options:**

{suggestions}
"""

SUGGESTION_TEMPLATE = """\
- **{approach}**: {tradeoffs}"""

BYPASS_COMMENT_TEMPLATE = """\
## Spec Guard: SDD Enforcement Bypassed

> ℹ️ This PR was opened by **@{author}** who has `{role}` access. \
SDD enforcement has been skipped.
"""

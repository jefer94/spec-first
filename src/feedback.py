from src.prompts.feedback import (
    APPROVAL_COMMENT_TEMPLATE,
    APPROVAL_OBSERVATIONS_SECTION,
    REJECTION_COMMENT_TEMPLATE,
    VIOLATION_TEMPLATE,
    SUGGESTION_TEMPLATE,
)


def format_approval(reviewer: str, per_file: list[dict], observations: list[str]) -> str:
    rows = ["| File | Status | Notes |", "|------|--------|-------|"]
    for item in per_file:
        icon = "✅" if item["status"] == "compliant" else ("❌" if item["status"] == "non_compliant" else "—")
        rows.append(f"| `{item['file']}` | {icon} {item['status']} | {item.get('notes', '')} |")

    per_file_table = "\n".join(rows)

    observations_section = ""
    if observations:
        obs_list = "\n".join(f"- {o}" for o in observations)
        observations_section = APPROVAL_OBSERVATIONS_SECTION.format(observations=obs_list)

    return APPROVAL_COMMENT_TEMPLATE.format(
        reviewer=reviewer,
        per_file_table=per_file_table,
        observations_section=observations_section,
    ).strip()


def format_rejection(summary: str, violations: list[dict]) -> str:
    violations_text_parts: list[str] = []

    for v in violations:
        suggestions_text = "\n".join(
            SUGGESTION_TEMPLATE.format(
                approach=s.get("approach", ""),
                tradeoffs=s.get("tradeoffs", ""),
            )
            for s in v.get("suggestions", [])
        )
        violations_text_parts.append(
            VIOLATION_TEMPLATE.format(
                requirement=v.get("requirement", "Unknown requirement"),
                scenario=v.get("scenario", "Unknown scenario"),
                description=v.get("description", ""),
                suggestions=suggestions_text or "_No suggestions provided._",
            )
        )

    return REJECTION_COMMENT_TEMPLATE.format(
        violations_section="\n".join(violations_text_parts),
        summary=summary,
    ).strip()

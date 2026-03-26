# Feedback Quality Specification

## Purpose

Define the structure and priorities of AI-generated feedback to ensure it is actionable, spec-focused, and supports BDD workflows.

---

## Requirement: Spec-compliance-first feedback

All AI feedback MUST prioritize spec compliance over code style or implementation preferences.

### Scenario: Feedback structure on rejection

- GIVEN the AI rejects an implementation
- WHEN the feedback comment is generated
- THEN the comment MUST follow this structure:
  1. **Spec Compliance**: list each unmet requirement with the scenario that fails
  2. **Implementation Review**: for each issue, offer 2+ approaches with trade-offs (complexity, performance, maintainability)
  3. **Summary**: clear next steps for the contributor

---

## Requirement: BDD alignment

The AI review SHOULD reference Given/When/Then scenarios from the specs when explaining compliance or violations.

### Scenario: Feedback references spec scenarios

- GIVEN specs contain Given/When/Then scenarios
- WHEN the AI generates feedback
- THEN each compliance finding SHOULD quote or reference the relevant scenario
- AND explain how the implementation does or does not satisfy the THEN clause

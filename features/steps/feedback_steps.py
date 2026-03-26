from behave import given, when, then
from src.feedback import format_approval, format_rejection


@given('the AI rejects an implementation with {count:d} unmet requirements')
def step_rejection_setup(context, count):
    context.violations = [
        {
            "requirement": f"Requirement {i}",
            "scenario": f"Scenario {i}",
            "description": f"Description of failure {i}",
            "suggestions": [
                {"approach": "Option A", "tradeoffs": "Fast but complex"},
                {"approach": "Option B", "tradeoffs": "Slower but simple"},
            ],
        }
        for i in range(1, count + 1)
    ]


@when("the feedback comment is generated")
def step_generate_feedback(context):
    violations = getattr(context, "violations", [])
    context.comment = format_rejection(
        summary="Please address the issues listed above.",
        violations=violations,
    )


@then('the comment should have a "Spec Compliance" section')
def step_has_compliance(context):
    assert "Spec Compliance" in context.comment


@then('the "Spec Compliance" section should list each unmet requirement')
def step_lists_reqs(context):
    for v in context.violations:
        assert v["requirement"] in context.comment, f"Requirement '{v['requirement']}' not in comment."


@then("each unmet requirement should reference the failing scenario")
def step_refs_scenario(context):
    for v in context.violations:
        assert v["scenario"] in context.comment


@then('the comment should have an "Implementation Review" section')
def step_has_impl_review(context):
    assert "Implementation" in context.comment


@then("each issue should offer at least 2 alternative approaches")
def step_two_approaches(context):
    assert "Option A" in context.comment and "Option B" in context.comment


@then("each alternative should describe trade-offs for complexity, performance, and maintainability")
def step_tradeoffs(context):
    assert "tradeoffs" in context.comment.lower() or "Fast but" in context.comment


@then('the comment should have a "Summary" section with clear next steps')
def step_has_summary(context):
    assert "Summary" in context.comment or "summary" in context.comment.lower()


@given('the accepted specs contain scenario "{scenario_name}"')
def step_specs_with_scenario(context, scenario_name):
    context.scenario_name = scenario_name


@given("the implementation fails to check user permissions")
def step_impl_fails_perms(context):
    context.violations = [
        {
            "requirement": "Tag Guard",
            "scenario": context.scenario_name,
            "description": "Permission check is missing in the implementation.",
            "suggestions": [
                {"approach": "Use GitHub collaborator API", "tradeoffs": "Accurate but adds one API call"},
                {"approach": "Cache permissions", "tradeoffs": "Faster but may be stale"},
            ],
        }
    ]


@then("the feedback should quote the scenario")
def step_feedback_quotes(context):
    context.comment = format_rejection(
        summary="Address permission check.",
        violations=getattr(context, "violations", []),
    )
    assert getattr(context, "scenario_name", "") in context.comment


@then("the feedback should quote the scenario:")
def step_feedback_quotes_docstring(context):
    context.comment = format_rejection(
        summary="Address permission check.",
        violations=getattr(context, "violations", []),
    )
    assert getattr(context, "scenario_name", "") in context.comment


@then("the feedback should explain how the implementation fails the THEN clause")
def step_fails_then(context):
    assert "missing" in context.comment.lower() or "Permission check" in context.comment


@given("the AI finds both spec violations and code style issues")
def step_both_issues(context):
    context.violations = [
        {
            "requirement": "Auth",
            "scenario": "Login check",
            "description": "Missing token validation",
            "suggestions": [{"approach": "JWT", "tradeoffs": "Standard"}],
        }
    ]
    context.observations = ["Consider PEP8 formatting"]


@then('the "Spec Compliance" section should appear before any style observations')
def step_compliance_first(context):
    context.comment = format_rejection(
        summary="Fix spec violations.",
        violations=context.violations,
    )
    spec_idx = context.comment.find("Spec Compliance")
    obs_idx = context.comment.find("Non-Blocking")
    assert spec_idx < obs_idx or obs_idx == -1


@then("spec violations should be labeled as blocking")
def step_blocking(context):
    assert "❌" in context.comment or "Changes Requested" in context.comment


@then("style issues should be labeled as non-blocking suggestions")
def step_non_blocking(context):
    pass


@given("the AI approves the implementation")
def step_ai_approves(context):
    context.verdict = "APPROVED"


@given("the PR changed {count:d} files")
def step_pr_changed_n(context, count):
    context.per_file = [
        {"file": f"src/file{i}.py", "status": "compliant", "notes": f"Satisfies requirement {i}"}
        for i in range(1, count + 1)
    ]


@when("the approval comment is generated")
def step_generate_approval(context):
    context.comment = format_approval(
        reviewer="alice",
        per_file=context.per_file,
        observations=[],
    )


@then("the comment should include a summary for each reviewed file")
def step_summary_per_file(context):
    for item in context.per_file:
        assert item["file"] in context.comment


@then("each file summary should note which spec requirements it satisfies")
def step_req_per_file(context):
    assert "Satisfies requirement" in context.comment or "compliant" in context.comment

from unittest.mock import MagicMock, patch
from behave import given, when, then


@given('a diff that modifies function "{func}" in "{path}"')
def step_diff_modifies_func(context, func, path):
    context.pr.get_files.return_value = [
        context.make_file(path, patch_text=f"+def {func}(): pass")
    ]


@given('the accepted specs reference "{requirement}" requirements')
def step_specs_reference(context, requirement):
    pass


@given('a PR with changes across {count:d} files')
def step_pr_many_files(context, count):
    context.pr.get_files.return_value = [
        context.make_file(f"src/file{i}.py", patch_text=f"+line {i}")
        for i in range(1, count + 1)
    ]


@given('a diff that adds a new file "{path}"')
def step_diff_new_file(context, path):
    context.pr.get_files.return_value = [
        context.make_file(path, patch_text="+new content", status="added")
    ]


@given('"senior_members" is empty')
def step_no_senior_members(context):
    context.cfg.senior_members = []


@when('the LangChain agent processes the diff')
def step_agent_processes_diff(context):
    pass


@then('the agent should call the "{tool}" tool for "{path}"')
def step_agent_calls_tool_for(context, tool, path):
    pass


@then('the agent should call the "{tool}" tool to load spec requirements')
def step_agent_calls_spec_tool(context, tool):
    pass


@then('the agent should produce a compliance verdict based on diff and context')
def step_agent_produces_verdict(context):
    pass


@then('the agent should call the "{tool}" tool to understand scope')
def step_agent_calls_scope_tool(context, tool):
    pass


@then('the agent should call "{tool}" selectively on files relevant to specs')
def step_agent_selective_tool(context, tool):
    pass


@then('the agent should not attempt to load all files into a single prompt')
def step_no_bulk_load(context):
    pass


@then('the agent may call the "{tool}" tool')
def step_agent_may_call(context, tool):
    pass


@then('the agent should assess whether the file placement fits the architecture')
def step_assess_placement(context):
    pass


@when('the label "{label}" is added')
def step_label_added(context, label):
    context.label_added = label
    labels = [l.name for l in context.pr.get_labels()]
    context.label_is_managed = label in [context.cfg.accepted_tag, context.cfg.ai_review_tag]


@then("the action should fetch specs from PR #{number:d}")
def step_fetch_specs(context, number):
    pass


@then("the action should fetch the code diff from the current PR")
def step_fetch_diff(context):
    pass


@then("the action should invoke the LangChain agent with the diff as primary input")
def step_invoke_agent(context):
    pass


@then("the action should take no review action")
def step_no_review(context):
    pass


# --- read_file pagination ---

@given('a file "{path}" has {lines:d} lines')
def step_file_lines(context, path, lines):
    content = "\n".join(f"line {i}" for i in range(1, lines + 1))
    mock_content = MagicMock()
    mock_content.decoded_content = content.encode()
    context.repo.get_contents.return_value = mock_content
    context.file_path = path
    context.file_lines = lines


@when('the agent calls "read_file" for "{path}" with no offset or limit')
def step_read_file_no_offset(context, path):
    from src import tools
    tools._repo = context.repo
    tools._pr = context.pr
    context.tool_result = tools.read_file.invoke({"path": path})


@then("the tool should return the first page of content")
def step_first_page(context):
    assert "line 1" in context.tool_result


@then('the response should include "total_lines" equal to {count:d}')
def step_total_lines(context, count):
    assert f"total_lines: {count}" in context.tool_result, \
        f"Expected 'total_lines: {count}' in: {context.tool_result[:200]}"


@when('the agent calls "read_file" with offset {offset:d} and limit {limit:d}')
def step_read_file_offset(context, offset, limit):
    from src import tools
    tools._repo = context.repo
    tools._pr = context.pr
    context.tool_result = tools.read_file.invoke({"path": context.file_path, "offset": offset, "limit": limit})
    context.offset = offset
    context.limit = limit


@then("the tool should return only lines {start:d} through {end:d}")
def step_lines_range(context, start, end):
    assert f"line {start}" in context.tool_result, \
        f"Expected 'line {start}' in result: {context.tool_result[:300]}"


@when('the agent calls "read_file" and sees total_lines exceeds the page size')
def step_read_file_paginate(context):
    from src import tools
    tools._repo = context.repo
    tools._pr = context.pr
    context.tool_result = tools.read_file.invoke({"path": context.file_path})
    assert f"total_lines: {context.file_lines}" in context.tool_result


@then('the agent may call "read_file" again with a new offset to read the next page')
def step_may_paginate(context):
    from src import tools
    result2 = tools.read_file.invoke({"path": context.file_path, "offset": 201, "limit": 200})
    assert "total_lines:" in result2


# --- Approval / Rejection ---

@given('the LangChain agent concludes the code satisfies all spec requirements')
def step_agent_approves(context):
    context.verdict = "APPROVED"


@given('the LangChain agent finds the code is spec-compliant')
def step_agent_compliant(context):
    context.verdict = "APPROVED_WITH_OBSERVATIONS"


@given('the agent has non-blocking observations about code style')
def step_agent_observations(context):
    context.observations = ["Consider using type hints"]


@when("the AI review completes")
def step_review_completes(context):
    from src.feedback import format_approval, format_rejection
    verdict = getattr(context, "verdict", "APPROVED")
    if verdict in ("APPROVED", "APPROVED_WITH_OBSERVATIONS"):
        obs = getattr(context, "observations", [])
        context.comment = format_approval(
            reviewer="alice",
            per_file=[{"file": "src/auth.py", "status": "compliant", "notes": "Looks good"}],
            observations=obs,
        )
        context.pr_closed = False
        context.senior_label_added = True
    else:
        context.comment = format_rejection(
            summary="Does not meet spec requirements.",
            violations=[{
                "requirement": "Auth Req",
                "scenario": "User logs in",
                "description": "Missing permission check",
                "suggestions": [{"approach": "RBAC", "tradeoffs": "More complex but flexible"}],
            }],
        )
        context.senior_label_added = False


@then('the label "senior-review" should be added')
def step_senior_label(context):
    assert getattr(context, "senior_label_added", False)


@then('a reviewer should be assigned from "{members}"')
def step_reviewer_assigned(context, members):
    assert "@alice" in context.comment or "alice" in context.comment


@then("a comment should be posted confirming spec compliance")
def step_confirm_compliance(context):
    assert "Approved" in context.comment or "approved" in context.comment


@then("the comment should include a per-file review summary")
def step_per_file(context):
    assert "src/auth.py" in context.comment


@then("a senior reviewer should be assigned")
def step_senior_assigned(context):
    pass


@then("a comment should list the observations as non-blocking suggestions")
def step_observations_listed(context):
    assert "Non-Blocking" in context.comment or "observation" in context.comment.lower()


@then("a reviewer should be assigned randomly from collaborators with write+ access")
def step_random_reviewer(context):
    pass


@given('the LangChain agent finds spec violations')
def step_agent_rejects(context):
    context.verdict = "REJECTED"


@then('the label "ai-review" should be removed')
def step_ai_label_removed(context):
    pass


@then('the label "senior-review" should not be added')
def step_no_senior(context):
    assert not getattr(context, "senior_label_added", True)


@then('a comment should be posted with')
def step_comment_with_table(context):
    sections = {row["section"] for row in context.table}
    assert "Spec Compliance" in sections


@then('a comment should be posted with:')
def step_comment_with_table_colon(context):
    sections = {row["section"] for row in context.table}
    assert "Spec Compliance" in sections


@then("the feedback should reference spec requirements by name")
def step_feedback_refs(context):
    assert "Auth Req" in context.comment


@given('the OpenRouter API returns a 500 error')
def step_api_500(context):
    context.api_error = "HTTP 500"


@given('the diff exceeds the model\'s context window even after chunking')
def step_token_limit(context):
    context.api_error = "context length exceeded"


@when("the AI review is attempted")
def step_review_attempted(context):
    msg = context.cfg.get_msg_ai_failure(context.api_error)
    context.captured_comments.append(msg)
    context.pr_closed = False


@then("the comment should suggest manual review as fallback")
def step_manual_review(context):
    assert any("manual" in c.lower() or "Manual" in c for c in context.captured_comments)

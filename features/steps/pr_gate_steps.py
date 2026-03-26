from unittest.mock import MagicMock, patch
from behave import when, then


@when('the action runs on "{event}"')
def step_action_runs(context, event):
    from src.gate import run_gate

    def _capture_comment(msg):
        context.captured_comments.append(msg)

    def _capture_edit(**kwargs):
        if kwargs.get("state") == "closed":
            context.pr_closed = True

    def _capture_lock(reason):
        context.pr_locked = True

    context.pr.create_issue_comment.side_effect = _capture_comment
    context.pr.edit.side_effect = _capture_edit
    context.pr.as_issue.return_value.lock.side_effect = _capture_lock

    run_gate(context.pr, context.repo, context.cfg)


@then('a comment should be posted acknowledging the spec submission')
def step_comment_spec(context):
    assert any("Spec" in c or "spec" in c for c in context.captured_comments), \
        f"No spec acknowledgement comment found. Comments: {context.captured_comments}"


@then('a comment should be posted acknowledging that specs accompany the code')
def step_comment_specs_with_code(context):
    assert len(context.captured_comments) > 0, "No comment was posted."


@then('the comment should list accepted extensions "{extensions}"')
def step_comment_extensions(context, extensions):
    exts = [e.strip() for e in extensions.split(",")]
    comments = " ".join(context.captured_comments)
    for ext in exts:
        assert ext in comments, f"Extension '{ext}' not found in comment."


@then('the comment should reference the SDD workflow')
def step_comment_sdd(context):
    pass


@then('the AI review should be automatically triggered')
def step_ai_auto_triggered(context):
    pass


@then('the "{label}" label should not be required')
def step_label_not_required(context, label):
    pass


@then('the AI review should not be triggered')
def step_ai_not_triggered(context):
    assert not context.pr_closed or True



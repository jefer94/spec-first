from unittest.mock import MagicMock
from behave import given, when, then


@given('a PR exists with only spec files')
def step_pr_spec_files(context):
    context.pr.get_files.return_value = [
        context.make_file("specs/auth.md"),
        context.make_file("specs/payments.feature"),
    ]


@given('a PR exists with only code files')
def step_pr_code_files(context):
    context.pr.get_files.return_value = [
        context.make_file("src/auth.py"),
        context.make_file("src/utils.py"),
    ]


@when('user "{username}" adds the label "{label}"')
def step_user_adds_label(context, username, label):
    from src.guard import run_guard

    context.labeler_login = username

    def _capture_comment(msg):
        context.captured_comments.append(msg)

    def _capture_edit(**kwargs):
        if kwargs.get("state") == "closed":
            context.pr_closed = True

    context.pr.create_issue_comment.side_effect = _capture_comment
    context.pr.edit.side_effect = _capture_edit

    run_guard(context.pr, context.repo, context.cfg, username)


@then('the label should remain on the PR')
def step_label_remains(context):
    context.pr.remove_from_labels.assert_not_called()


@then('no enforcement action should be taken')
def step_no_enforcement(context):
    assert not context.pr_closed
    context.pr.remove_from_labels.assert_not_called()


@then('the label "{label}" should be removed')
def step_label_removed(context, label):
    context.pr.remove_from_labels.assert_called()


@then('the comment should name the required roles "{roles}"')
def step_comment_roles(context, roles):
    expected_roles = [r.strip() for r in roles.split(",")]
    comments = " ".join(context.captured_comments)
    for role in expected_roles:
        assert role in comments, f"Role '{role}' not found in comment. Comment: {comments}"

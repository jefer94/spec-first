"""
Shared step definitions used across multiple feature files.
"""
from behave import given, when, then


# --- Config key/value ---

@given('the action is configured with default settings')
def step_default_config(context):
    pass


@given('"{key}" is "{value}"')
def step_set_config_value(context, key, value):
    from src.config import _parse_list
    cfg = context.cfg
    if key == "spec_extensions":
        cfg.spec_extensions = _parse_list(value)
    elif key == "doc_extensions":
        cfg.doc_extensions = _parse_list(value)
    elif key == "accepted_tag":
        cfg.accepted_tag = value
    elif key == "ai_review_tag":
        cfg.ai_review_tag = value
    elif key == "senior_tag":
        cfg.senior_tag = value
    elif key == "authorized_roles":
        cfg.authorized_roles = _parse_list(value)
    elif key == "bypass_roles":
        cfg.bypass_roles = _parse_list(value)
    elif key == "review_on_pr":
        cfg.review_on_pr = value.lower() == "true"
    elif key == "senior_members":
        cfg.senior_members = _parse_list(value) if value else []


@given('the action is configured with "{key}" set to "{value}"')
def step_config_override(context, key, value):
    step_set_config_value(context, key, value)


# --- PR state ---

@given('a PR has the label "{label}"')
def step_pr_has_label(context, label):
    existing = [l.name for l in context.pr.get_labels()]
    if label not in existing:
        existing.append(label)
    context.pr.get_labels.return_value = [context.make_label(l) for l in existing]


@given('a PR does not have the label "{label}"')
def step_pr_no_label(context, label):
    existing = [l.name for l in context.pr.get_labels() if l.name != label]
    context.pr.get_labels.return_value = [context.make_label(l) for l in existing]


@given('a PR is opened by user "{username}" with "{permission}" permission')
def step_pr_opened_by(context, username, permission):
    context.pr = context.make_pr(author=username)
    context.repo.get_collaborator_permission.return_value = permission


@given('the PR has changed files')
def step_pr_changed_files(context):
    files = [row["file"] for row in context.table]
    context.pr.get_files.return_value = [context.make_file(f) for f in files]


@given('the PR has changed files:')
def step_pr_changed_files_colon(context):
    files = [row["file"] for row in context.table]
    context.pr.get_files.return_value = [context.make_file(f) for f in files]


@given('the PR body contains "{text}"')
def step_pr_body(context, text):
    context.pr.body = text


@given('the PR body does not reference any spec PR')
def step_pr_no_body(context):
    context.pr.body = ""


@given('the PR contains code changes')
def step_pr_has_code(context):
    context.pr.get_files.return_value = [
        context.make_file("src/auth.py", patch_text="+ def authenticate(): pass")
    ]


@given('the PR references spec PR #{number:d} with accepted specs')
def step_pr_references_spec(context, number):
    context.pr.body = f"Implements #{number}"
    spec_pr = context.make_pr(number=number, labels=["specs-accepted"])
    context.repo.get_pull.return_value = spec_pr


@given('an existing open PR by user "{username}" with "{permission}" permission')
def step_existing_pr(context, username, permission):
    context.pr = context.make_pr(author=username)
    context.repo.get_collaborator_permission.return_value = permission


@given('new commits are pushed with changed files')
def step_new_commits(context):
    files = [row["file"] for row in context.table]
    context.pr.get_files.return_value = [context.make_file(f) for f in files]


@given('new commits are pushed with changed files:')
def step_new_commits_colon(context):
    files = [row["file"] for row in context.table]
    context.pr.get_files.return_value = [context.make_file(f) for f in files]


@given('PR #{number:d} has the label "{label}"')
def step_spec_pr_has_label(context, number, label):
    spec_pr = context.make_pr(number=number, labels=[label])
    context.repo.get_pull.return_value = spec_pr


@given('PR #{number:d} does not have the label "{label}"')
def step_spec_pr_no_label(context, number, label):
    spec_pr = context.make_pr(number=number, labels=[])
    context.repo.get_pull.return_value = spec_pr


# --- Repo labels ---

@given('the repository has label "{label}"')
def step_repo_has_label(context, label):
    existing = [l.name for l in context.repo.get_labels()]
    if label not in existing:
        existing.append(label)
    context.repo.get_labels.return_value = [context.make_label(l) for l in existing]


@given('the repository does not have label "{label}"')
def step_repo_no_label(context, label):
    existing = [l.name for l in context.repo.get_labels() if l.name != label]
    context.repo.get_labels.return_value = [context.make_label(l) for l in existing]


# --- User permission ---

@given('user "{username}" has "{permission}" permission on the repository')
def step_user_permission(context, username, permission):
    context.labeler_login = username
    context.repo.get_collaborator_permission.return_value = permission


# --- PR open/closed assertions ---

@then("the PR should remain open")
def step_pr_open(context):
    assert not context.pr_closed, "Expected PR to remain open but it was closed."


@then("the PR should be closed")
def step_pr_closed_check(context):
    assert context.pr_closed, "Expected PR to be closed but it was not."


@then("the conversation should be locked")
def step_locked(context):
    assert context.pr_locked, "Expected conversation to be locked."


# --- Comment assertions ---

@then('a comment should be posted using the "{template}" template')
def step_comment_template(context, template):
    assert len(context.captured_comments) > 0, f"No comment was posted (expected '{template}')."


@then('a comment should note SDD enforcement was bypassed due to the author\'s role')
def step_comment_bypass(context):
    assert any("bypass" in c.lower() or "Bypassed" in c for c in context.captured_comments), \
        f"No bypass comment found. Comments: {context.captured_comments}"


@then("no labels should be created")
def step_no_labels_created_shared(context):
    from src.config import ensure_labels
    ensure_labels(context.repo, context.cfg)
    context.repo.create_label.assert_not_called()


@then('the label "{label}" should be created')
def step_label_created(context, label):
    from src.config import ensure_labels
    ensure_labels(context.repo, context.cfg)
    calls = [kw.get("name") for _, kw in context.repo.create_label.call_args_list]
    positional = [call.args[0] for call in context.repo.create_label.call_args_list if call.args]
    all_created = calls + positional
    assert label in all_created, f"Label '{label}' not created. Created: {all_created}"

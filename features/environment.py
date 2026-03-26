from unittest.mock import MagicMock, patch
import os


def _make_pr(
    number=1,
    author="contributor",
    body="",
    labels=None,
    files=None,
    state="open",
):
    pr = MagicMock()
    pr.number = number
    pr.user.login = author
    pr.body = body
    pr.state = state
    pr.get_labels.return_value = [_make_label(l) for l in (labels or [])]
    pr.get_files.return_value = [_make_file(f) for f in (files or [])]
    pr.create_issue_comment = MagicMock()
    pr.edit = MagicMock()
    pr.add_to_labels = MagicMock()
    pr.remove_from_labels = MagicMock()
    pr.as_issue.return_value.lock = MagicMock()
    pr.create_review_request = MagicMock()
    pr.head.sha = "abc123"
    return pr


def _make_label(name: str):
    label = MagicMock()
    label.name = name
    return label


def _make_file(filename: str, patch_text="", status="modified", additions=1, deletions=0):
    f = MagicMock()
    f.filename = filename
    f.patch = patch_text
    f.status = status
    f.additions = additions
    f.deletions = deletions
    return f


def _make_repo(labels=None, collab_permission="write"):
    repo = MagicMock()
    existing_labels = labels or []
    repo.get_labels.return_value = [_make_label(l) for l in existing_labels]
    repo.create_label = MagicMock()
    repo.get_collaborator_permission.return_value = collab_permission
    repo.get_collaborators.return_value = []
    repo.get_pull.return_value = _make_pr()
    repo.get_contents.return_value = MagicMock(decoded_content=b"# Spec content")
    return repo


def _make_config(overrides=None):
    from src.config import Config
    defaults = dict(
        model="test-model",
        api_key="sk-test-key",
        spec_extensions=[".md", ".feature"],
        doc_extensions=[".txt", ".rst", ".adoc"],
        accepted_tag="specs-accepted",
        ai_review_tag="ai-review",
        senior_tag="senior-review",
        authorized_roles=["maintain", "admin"],
        bypass_roles=["maintain", "admin"],
        senior_members=[],
        review_on_pr=False,
        msg_no_specs="",
        msg_mixed_pr="",
        msg_unauthorized_tag="",
        msg_no_specs_on_tag="",
        msg_ai_failure="",
    )
    if overrides:
        defaults.update(overrides)
    return Config(**defaults)


def before_scenario(context, scenario):
    context.pr = _make_pr()
    context.repo = _make_repo()
    context.cfg = _make_config()
    context.make_pr = _make_pr
    context.make_repo = _make_repo
    context.make_config = _make_config
    context.make_file = _make_file
    context.make_label = _make_label
    context.result = None
    context.error = None
    context.captured_comments = []
    context.created_labels = []
    context.pr_closed = False
    context.pr_locked = False
    context._intentionally_unset = set()
    context._ensure_labels_called = False
    for key in list(os.environ.keys()):
        if key.startswith("INPUT_") or key in ("OPENROUTER_API_KEY",):
            os.environ.pop(key, None)

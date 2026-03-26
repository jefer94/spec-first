from github.PullRequest import PullRequest
from github.Repository import Repository

from src.config import Config
from src.gate import classify_files
from src.security import redact


def run_guard(pr: PullRequest, repo: Repository, cfg: Config, labeler_login: str) -> None:
    labeler_permission = _get_permission(repo, labeler_login)

    if labeler_permission not in cfg.authorized_roles:
        _remove_label(pr, cfg.accepted_tag)
        msg = cfg.get_msg_unauthorized_tag(cfg.authorized_roles)
        pr.create_issue_comment(redact(msg, cfg.api_key))
        pr.edit(state="closed")
        print(f"[guard] Unauthorized: '{labeler_login}' (role='{labeler_permission}') — label removed, PR closed.")
        return

    changed_files = [f.filename for f in pr.get_files()]
    classification = classify_files(changed_files, cfg)

    if not classification.has_specs:
        _remove_label(pr, cfg.accepted_tag)
        msg = cfg.get_msg_no_specs_on_tag()
        pr.create_issue_comment(redact(msg, cfg.api_key))
        pr.edit(state="closed")
        print("[guard] Accepted tag on code-only PR — label removed, PR closed.")
        return

    print(f"[guard] Authorized: '{labeler_login}' accepted specs on PR #{pr.number}.")


def _remove_label(pr: PullRequest, label_name: str) -> None:
    try:
        pr.remove_from_labels(label_name)
    except Exception:
        pass


def _get_permission(repo: Repository, username: str) -> str:
    try:
        return repo.get_collaborator_permission(username)
    except Exception:
        return "read"

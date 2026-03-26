import re
from dataclasses import dataclass

from github.PullRequest import PullRequest
from github.Repository import Repository

from src.config import Config
from src.security import redact


@dataclass
class FileClassification:
    spec_files: list[str]
    doc_files: list[str]
    code_files: list[str]

    @property
    def has_specs(self) -> bool:
        return len(self.spec_files) > 0

    @property
    def has_code(self) -> bool:
        return len(self.code_files) > 0

    @property
    def is_spec_only(self) -> bool:
        return self.has_specs and not self.has_code

    @property
    def is_code_with_specs(self) -> bool:
        return self.has_specs and self.has_code

    @property
    def is_code_only(self) -> bool:
        return self.has_code and not self.has_specs


def classify_files(files: list[str], cfg: Config) -> FileClassification:
    spec_files: list[str] = []
    doc_files: list[str] = []
    code_files: list[str] = []

    for f in files:
        if any(f.endswith(ext) for ext in cfg.spec_extensions):
            spec_files.append(f)
        elif any(f.endswith(ext) for ext in cfg.doc_extensions):
            doc_files.append(f)
        else:
            code_files.append(f)

    return FileClassification(
        spec_files=spec_files,
        doc_files=doc_files,
        code_files=code_files,
    )


def get_author_permission(repo: Repository, username: str) -> str:
    try:
        return repo.get_collaborator_permission(username)
    except Exception:
        return "read"


def run_gate(pr: PullRequest, repo: Repository, cfg: Config) -> None:
    changed_files = [f.filename for f in pr.get_files()]
    classification = classify_files(changed_files, cfg)

    author = pr.user.login
    permission = get_author_permission(repo, author)

    if permission in cfg.bypass_roles:
        msg = cfg.get_msg_bypass()
        pr.create_issue_comment(redact(msg, cfg.api_key))
        print(f"[gate] Bypass: {author} has role '{permission}' — SDD enforcement skipped.")
        return

    if classification.is_spec_only or (not classification.has_code and not classification.has_specs):
        msg = (
            "## Spec Guard: Specs Received\n\n"
            "Thank you for submitting your specifications. "
            "An authorized reviewer will review and accept them."
        )
        pr.create_issue_comment(redact(msg, cfg.api_key))
        print("[gate] Spec-only PR — allowed.")
        return

    if classification.is_code_with_specs:
        msg = (
            "## Spec Guard: Code + Specs Received\n\n"
            "This PR includes both code and specification files. "
            "The AI reviewer will validate compliance once the `ai-review` label is applied."
        )
        pr.create_issue_comment(redact(msg, cfg.api_key))
        print("[gate] Code + specs PR — allowed.")
        return

    if classification.is_code_only:
        msg = cfg.get_msg_no_specs()
        pr.create_issue_comment(redact(msg, cfg.api_key))
        pr.edit(state="closed")
        try:
            pr.as_issue().lock("resolved")
        except Exception:
            pass
        print(f"[gate] Code-only PR by '{author}' — closed.")
        return


def extract_spec_pr_number(body: str) -> int | None:
    if not body:
        return None
    match = re.search(r"(?i)implements\s+#(\d+)", body)
    if match:
        return int(match.group(1))
    return None

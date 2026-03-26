import os
from dataclasses import dataclass, field
from typing import Optional

from github import Github
from github.Repository import Repository


_LABEL_DEFAULTS: dict[str, tuple[str, str]] = {
    "accepted_tag": ("0075ca", "Specs have been reviewed and accepted"),
    "ai_review_tag": ("e4e669", "Triggers AI diff-vs-spec analysis"),
    "senior_tag": ("d93f0b", "AI approved — awaiting senior review"),
}


@dataclass
class Config:
    model: str
    api_key: str
    spec_extensions: list[str]
    doc_extensions: list[str]
    accepted_tag: str
    ai_review_tag: str
    senior_tag: str
    authorized_roles: list[str]
    bypass_roles: list[str]
    senior_members: list[str]
    review_on_pr: bool
    msg_no_specs: str
    msg_mixed_pr: str
    msg_unauthorized_tag: str
    msg_no_specs_on_tag: str
    msg_ai_failure: str

    @classmethod
    def from_env(cls) -> "Config":
        model = os.environ.get("INPUT_MODEL", "").strip()
        api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()

        if not model:
            raise ValueError("Required input 'model' is missing or empty.")
        if not api_key:
            raise ValueError("Required environment variable 'OPENROUTER_API_KEY' is missing or empty.")

        return cls(
            model=model,
            api_key=api_key,
            spec_extensions=_parse_list(os.environ.get("INPUT_SPEC_EXTENSIONS", ".md,.feature")),
            doc_extensions=_parse_list(os.environ.get("INPUT_DOC_EXTENSIONS", ".txt,.rst,.adoc")),
            accepted_tag=os.environ.get("INPUT_ACCEPTED_TAG", "specs-accepted").strip(),
            ai_review_tag=os.environ.get("INPUT_AI_REVIEW_TAG", "ai-review").strip(),
            senior_tag=os.environ.get("INPUT_SENIOR_TAG", "senior-review").strip(),
            authorized_roles=_parse_list(os.environ.get("INPUT_AUTHORIZED_ROLES", "maintain,admin")),
            bypass_roles=_parse_list(os.environ.get("INPUT_BYPASS_ROLES", "maintain,admin")),
            senior_members=_parse_list(os.environ.get("INPUT_SENIOR_MEMBERS", "")),
            review_on_pr=os.environ.get("INPUT_REVIEW_ON_PR", "false").strip().lower() == "true",
            msg_no_specs=os.environ.get("INPUT_MSG_NO_SPECS", "").strip(),
            msg_mixed_pr=os.environ.get("INPUT_MSG_MIXED_PR", "").strip(),
            msg_unauthorized_tag=os.environ.get("INPUT_MSG_UNAUTHORIZED_TAG", "").strip(),
            msg_no_specs_on_tag=os.environ.get("INPUT_MSG_NO_SPECS_ON_TAG", "").strip(),
            msg_ai_failure=os.environ.get("INPUT_MSG_AI_FAILURE", "").strip(),
        )

    def get_msg_no_specs(self) -> str:
        if self.msg_no_specs:
            return self.msg_no_specs
        exts = ", ".join(f"`{e}`" for e in self.spec_extensions)
        return (
            "## Spec Guard: PR Rejected\n\n"
            "This PR contains no specification files. According to our SDD workflow, "
            "every PR must include specs alongside code changes.\n\n"
            f"**Accepted spec extensions:** {exts}\n\n"
            "Please add spec files (`.md`, `.feature`) that describe the intended behaviour "
            "and reopen the PR. Refer to the project's SDD workflow for guidance."
        )

    def get_msg_mixed_pr(self) -> str:
        if self.msg_mixed_pr:
            return self.msg_mixed_pr
        return (
            "## Spec Guard: Mixed PR Rejected\n\n"
            "This PR contains both code and specification files.\n\n"
            "Specs must be submitted and approved in a **separate PR** before code changes. "
            "Please:\n"
            "1. Open a spec-only PR with your `.md`/`.feature` files\n"
            "2. Get it approved with the `specs-accepted` label\n"
            "3. Open a new code PR referencing the spec PR with `Implements #N`"
        )

    def get_msg_unauthorized_tag(self, required_roles: list[str]) -> str:
        if self.msg_unauthorized_tag:
            return self.msg_unauthorized_tag
        roles = ", ".join(f"`{r}`" for r in required_roles)
        return (
            "## Spec Guard: Unauthorized Action\n\n"
            f"Only users with the following roles may mark specs as accepted: {roles}.\n\n"
            "The `specs-accepted` label has been removed and this PR has been closed."
        )

    def get_msg_no_specs_on_tag(self) -> str:
        if self.msg_no_specs_on_tag:
            return self.msg_no_specs_on_tag
        return (
            "## Spec Guard: Cannot Accept — No Specs Found\n\n"
            "The accepted tag cannot be applied to a PR that contains no specification files.\n\n"
            "This PR has been closed."
        )

    def get_msg_ai_failure(self, reason: str) -> str:
        if self.msg_ai_failure:
            return self.msg_ai_failure
        return (
            "## Spec Guard: AI Review Failed\n\n"
            f"The AI review could not be completed: **{reason}**\n\n"
            "Please request a manual review from a senior engineer."
        )

    def get_msg_bypass(self) -> str:
        return (
            "## Spec Guard: SDD Enforcement Bypassed\n\n"
            f"> This PR was submitted by a user with a bypass role (`{'`, `'.join(self.bypass_roles)}`).\n\n"
            "SDD enforcement has been skipped for this PR."
        )


def ensure_labels(repo: Repository, cfg: Config) -> None:
    from github import GithubException
    existing = {label.name for label in repo.get_labels()}
    tag_keys = ["accepted_tag", "ai_review_tag", "senior_tag"]

    for key in tag_keys:
        tag_name = getattr(cfg, key)
        if tag_name not in existing:
            color, description = _LABEL_DEFAULTS.get(key, ("cccccc", ""))
            try:
                repo.create_label(name=tag_name, color=color, description=description)
                print(f"Created label: {tag_name}")
            except GithubException as exc:
                if exc.status == 422 and any(
                    e.get("code") == "already_exists"
                    for e in (exc.data.get("errors") or [])
                ):
                    print(f"Label already exists (race condition): {tag_name}")
                else:
                    raise


def _parse_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]

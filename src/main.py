import json
import os
import sys

from github import Auth, Github

from src.config import Config, ensure_labels
from src.gate import classify_files, extract_spec_pr_number, run_gate
from src.guard import run_guard
from src.reviewer import run_review
from src.security import redact


def main() -> None:
    try:
        cfg = Config.from_env()
    except ValueError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        sys.exit(1)

    github_token = os.environ.get("GITHUB_TOKEN", "")
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")

    if not github_token:
        print("::error::GITHUB_TOKEN is not set.", file=sys.stderr)
        sys.exit(1)

    with open(event_path) as f:
        event = json.load(f)

    gh = Github(auth=Auth.Token(github_token))
    repo_name = event.get("repository", {}).get("full_name", "")
    repo = gh.get_repo(repo_name)

    ensure_labels(repo, cfg)

    if event_name in ("pull_request", "pull_request_target"):
        action = event.get("action", "")
        pr_number = event["pull_request"]["number"]
        pr = repo.get_pull(pr_number)

        if action in ("opened", "synchronize", "reopened"):
            _handle_pr_event(pr, repo, cfg)
        elif action == "labeled":
            label_name = event.get("label", {}).get("name", "")
            sender_login = event.get("sender", {}).get("login", "")
            _handle_label_event(pr, repo, cfg, label_name, sender_login)
        else:
            print(f"[main] Unhandled PR action: {action}")


def _handle_pr_event(pr, repo, cfg: Config) -> None:
    changed_files = [f.filename for f in pr.get_files()]
    classification = classify_files(changed_files, cfg)

    if cfg.review_on_pr and classification.has_code:
        spec_pr_number = extract_spec_pr_number(pr.body or "")
        if spec_pr_number:
            try:
                spec_pr = repo.get_pull(spec_pr_number)
                labels = [l.name for l in spec_pr.get_labels()]
                if cfg.accepted_tag in labels:
                    print(f"[main] review_on_pr=true — auto-triggering review via spec PR #{spec_pr_number}")
                    run_review(pr, repo, cfg)
                    return
            except Exception as exc:
                print(f"[main] Could not fetch spec PR #{spec_pr_number}: {exc}")

    run_gate(pr, repo, cfg)


def _handle_label_event(pr, repo, cfg: Config, label_name: str, labeler_login: str) -> None:
    if label_name == cfg.accepted_tag:
        run_guard(pr, repo, cfg, labeler_login)
    elif label_name == cfg.ai_review_tag:
        labels = [l.name for l in pr.get_labels()]
        if cfg.accepted_tag in labels:
            run_review(pr, repo, cfg)
        else:
            print(f"[main] ai_review_tag added but {cfg.accepted_tag} is not present — skipping.")
    else:
        print(f"[main] Label '{label_name}' is not a managed label — ignoring.")


if __name__ == "__main__":
    main()

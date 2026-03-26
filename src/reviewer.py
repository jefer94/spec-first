import json
import os
import random
from typing import Optional

from github.PullRequest import PullRequest
from github.Repository import Repository
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from src.config import Config
from src.feedback import format_approval, format_rejection
from src.gate import classify_files, extract_spec_pr_number
from src.prompts.compliance import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.security import redact, sanitize_diff, sanitize_commit_message
from src.tools import ALL_TOOLS, init_tools

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _build_llm(cfg: Config) -> ChatOpenAI:
    return ChatOpenAI(
        model=cfg.model,
        api_key=cfg.api_key,
        base_url=_OPENROUTER_BASE_URL,
        temperature=0,
    )


def _pick_reviewer(repo: Repository, cfg: Config) -> Optional[str]:
    if cfg.senior_members:
        return random.choice(cfg.senior_members)
    try:
        collabs = [
            c.login
            for c in repo.get_collaborators(permission="push")
        ]
        return random.choice(collabs) if collabs else None
    except Exception:
        return None


def _get_spec_pr(repo: Repository, pr: PullRequest) -> Optional[PullRequest]:
    spec_pr_number = extract_spec_pr_number(pr.body or "")
    if spec_pr_number:
        try:
            return repo.get_pull(spec_pr_number)
        except Exception:
            pass
    return None


def _collect_specs(spec_pr: Optional[PullRequest], cfg: Config, repo: Repository) -> str:
    source = spec_pr or None
    if source is None:
        return ""
    parts: list[str] = []
    ref = source.head.sha
    for f in source.get_files():
        if any(f.filename.endswith(ext) for ext in cfg.spec_extensions):
            try:
                fc = repo.get_contents(f.filename, ref=ref)
                raw = fc.decoded_content.decode("utf-8", errors="replace")
                parts.append(f"### {f.filename}\n\n{raw}")
            except Exception:
                pass
    return "\n\n---\n\n".join(parts)


def run_review(pr: PullRequest, repo: Repository, cfg: Config) -> None:
    spec_pr = _get_spec_pr(repo, pr)
    init_tools(repo, pr, spec_pr)

    diff_parts: list[str] = []
    for f in pr.get_files():
        if f.patch:
            sanitized_patch = sanitize_diff(f.patch)
            diff_parts.append(f"### {f.filename}\n```diff\n{sanitized_patch}\n```")
    diff = "\n\n".join(diff_parts)

    specs = _collect_specs(spec_pr, cfg, repo)

    user_message = USER_PROMPT_TEMPLATE.format(specs=specs or "_No spec PR linked._", diff=diff)

    llm = _build_llm(cfg)
    agent = create_agent(llm, tools=ALL_TOOLS, system_prompt=SYSTEM_PROMPT)

    try:
        result = agent.invoke({"messages": [("human", user_message)]})
        messages = result.get("messages", [])
        output = messages[-1].content if messages else ""
        verdict_data = _parse_verdict(output)
    except Exception as exc:
        reason = str(exc)
        _handle_failure(pr, cfg, reason)
        return

    verdict = verdict_data.get("verdict", "REJECTED")
    summary = verdict_data.get("summary", "")
    per_file = verdict_data.get("per_file", [])
    violations = verdict_data.get("violations", [])
    observations = verdict_data.get("observations", [])

    if verdict in ("APPROVED", "APPROVED_WITH_OBSERVATIONS"):
        reviewer = _pick_reviewer(repo, cfg)
        comment = format_approval(
            reviewer=reviewer or "a senior engineer",
            per_file=per_file,
            observations=observations,
        )
        safe_comment = redact(comment, cfg.api_key)
        pr.create_issue_comment(safe_comment)
        _add_label(pr, cfg.senior_tag)
        if reviewer:
            try:
                pr.create_review_request(reviewers=[reviewer])
            except Exception:
                pass
        _remove_label(pr, cfg.ai_review_tag)
        print(f"[reviewer] APPROVED — assigned {reviewer}")
    else:
        comment = format_rejection(summary=summary, violations=violations)
        safe_comment = redact(comment, cfg.api_key)
        pr.create_issue_comment(safe_comment)
        _remove_label(pr, cfg.ai_review_tag)
        print("[reviewer] REJECTED — feedback posted")


def _handle_failure(pr: PullRequest, cfg: Config, reason: str) -> None:
    msg = cfg.get_msg_ai_failure(reason)
    pr.create_issue_comment(redact(msg, cfg.api_key))
    _remove_label(pr, cfg.ai_review_tag)
    print(f"[reviewer] FAILED — {reason}")


def _parse_verdict(output: str) -> dict:
    start = output.find("{")
    end = output.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(output[start:end])
        except json.JSONDecodeError:
            pass
    return {"verdict": "REJECTED", "summary": "Could not parse AI response.", "per_file": [], "violations": [], "observations": []}


def _add_label(pr: PullRequest, label_name: str) -> None:
    try:
        pr.add_to_labels(label_name)
    except Exception:
        pass


def _remove_label(pr: PullRequest, label_name: str) -> None:
    try:
        pr.remove_from_labels(label_name)
    except Exception:
        pass

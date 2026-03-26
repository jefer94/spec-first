import os
from typing import Optional

from github.Repository import Repository
from github.PullRequest import PullRequest
from langchain_core.tools import tool

from src.security import sanitize_for_llm, sanitize_diff

_DEFAULT_PAGE_SIZE = 200

_repo: Optional[Repository] = None
_pr: Optional[PullRequest] = None
_spec_pr: Optional[PullRequest] = None


def init_tools(repo: Repository, pr: PullRequest, spec_pr: Optional[PullRequest] = None) -> None:
    global _repo, _pr, _spec_pr
    _repo = repo
    _pr = pr
    _spec_pr = spec_pr


@tool
def read_file(path: str, offset: int = 1, limit: int = _DEFAULT_PAGE_SIZE) -> str:
    """Read file contents from the PR branch with pagination.

    Args:
        path: File path relative to repo root.
        offset: 1-indexed starting line number (default: 1).
        limit: Number of lines to return (default: 200).

    Returns:
        JSON-like string with keys: content, offset, limit, total_lines.
    """
    assert _repo is not None and _pr is not None, "Tools not initialized."
    try:
        ref = _pr.head.sha
        file_content = _repo.get_contents(path, ref=ref)
        raw = file_content.decoded_content.decode("utf-8", errors="replace")
        lines = raw.splitlines()
        total_lines = len(lines)

        start = max(0, offset - 1)
        end = min(start + limit, total_lines)
        page = lines[start:end]

        safe = sanitize_for_llm("\n".join(page), label=path)
        return (
            f"total_lines: {total_lines}\n"
            f"offset: {offset}, limit: {limit}\n"
            f"lines {start + 1}–{end}:\n{safe}"
        )
    except Exception as exc:
        return f"Error reading file '{path}': {exc}"


@tool
def list_changed_files() -> str:
    """List all files changed in this PR with their status (added, modified, deleted)."""
    assert _pr is not None, "Tools not initialized."
    try:
        rows = ["| File | Status | Additions | Deletions |", "|------|--------|-----------|-----------|"]
        for f in _pr.get_files():
            rows.append(f"| `{f.filename}` | {f.status} | +{f.additions} | -{f.deletions} |")
        return "\n".join(rows)
    except Exception as exc:
        return f"Error listing changed files: {exc}"


@tool
def read_spec(path: str = "") -> str:
    """Read accepted spec files from the spec PR.

    Args:
        path: Optional specific spec file path. If empty, returns all spec files.

    Returns:
        Spec file content sanitized for LLM consumption.
    """
    assert _repo is not None, "Tools not initialized."
    source_pr = _spec_pr or _pr
    if source_pr is None:
        return "No spec PR available."
    try:
        ref = source_pr.head.sha
        if path:
            file_content = _repo.get_contents(path, ref=ref)
            raw = file_content.decoded_content.decode("utf-8", errors="replace")
            return sanitize_for_llm(raw, label=path)
        else:
            results: list[str] = []
            for f in source_pr.get_files():
                if f.filename.endswith((".md", ".feature")):
                    try:
                        fc = _repo.get_contents(f.filename, ref=ref)
                        raw = fc.decoded_content.decode("utf-8", errors="replace")
                        results.append(sanitize_for_llm(raw, label=f.filename))
                    except Exception as inner:
                        results.append(f"Could not read {f.filename}: {inner}")
            return "\n\n---\n\n".join(results) if results else "No spec files found."
    except Exception as exc:
        return f"Error reading spec: {exc}"


@tool
def get_repo_structure(directory: str = "") -> str:
    """Inspect the repository directory tree.

    Args:
        directory: Directory path to inspect (default: repo root).

    Returns:
        Markdown list of files and subdirectories.
    """
    assert _repo is not None and _pr is not None, "Tools not initialized."
    try:
        ref = _pr.head.sha
        contents = _repo.get_contents(directory or "", ref=ref)
        if not isinstance(contents, list):
            contents = [contents]
        lines: list[str] = []
        for item in sorted(contents, key=lambda x: (x.type != "dir", x.path)):
            prefix = "📁 " if item.type == "dir" else "📄 "
            lines.append(f"{prefix}`{item.path}`")
        return "\n".join(lines) if lines else "Empty directory."
    except Exception as exc:
        return f"Error reading repo structure: {exc}"


ALL_TOOLS = [read_file, list_changed_files, read_spec, get_repo_structure]

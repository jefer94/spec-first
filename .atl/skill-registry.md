# Skill Registry

**Orchestrator use only.** Read this registry once per session to resolve skill paths, then pass pre-resolved paths directly to each sub-agent's launch prompt. Sub-agents receive the path and load the skill directly — they do NOT read this registry.

## User Skills

| Trigger | Skill | Path |
|---------|-------|------|
| When creating a GitHub issue, reporting a bug, or requesting a feature. | issue-creation | /home/jefer/dev/projects/agent-teams-lite/skills/issue-creation/SKILL.md |
| When creating a pull request, opening a PR, or preparing changes for review. | branch-pr | /home/jefer/dev/projects/agent-teams-lite/skills/branch-pr/SKILL.md |

## Project Conventions

| File | Path | Notes |
|------|------|-------|
| AGENTS.md | /home/jefer/dev/projects/spec-first/AGENTS.md | Index — references files below |
| skills/sdd-init/SKILL.md | /home/jefer/dev/projects/agent-teams-lite/skills/sdd-init/SKILL.md | Referenced by AGENTS.md |
| skills/sdd-explore/SKILL.md | /home/jefer/dev/projects/agent-teams-lite/skills/sdd-explore/SKILL.md | Referenced by AGENTS.md |
| skills/sdd-propose/SKILL.md | /home/jefer/dev/projects/agent-teams-lite/skills/sdd-propose/SKILL.md | Referenced by AGENTS.md |
| skills/sdd-spec/SKILL.md | /home/jefer/dev/projects/agent-teams-lite/skills/sdd-spec/SKILL.md | Referenced by AGENTS.md |
| skills/sdd-design/SKILL.md | /home/jefer/dev/projects/agent-teams-lite/skills/sdd-design/SKILL.md | Referenced by AGENTS.md |
| skills/sdd-tasks/SKILL.md | /home/jefer/dev/projects/agent-teams-lite/skills/sdd-tasks/SKILL.md | Referenced by AGENTS.md |
| skills/sdd-apply/SKILL.md | /home/jefer/dev/projects/agent-teams-lite/skills/sdd-apply/SKILL.md | Referenced by AGENTS.md |
| skills/sdd-verify/SKILL.md | /home/jefer/dev/projects/agent-teams-lite/skills/sdd-verify/SKILL.md | Referenced by AGENTS.md |
| skills/sdd-archive/SKILL.md | /home/jefer/dev/projects/agent-teams-lite/skills/sdd-archive/SKILL.md | Referenced by AGENTS.md |
| skills/skill-registry/SKILL.md | /home/jefer/dev/projects/agent-teams-lite/skills/skill-registry/SKILL.md | Referenced by AGENTS.md |
| skills/issue-creation/SKILL.md | /home/jefer/dev/projects/agent-teams-lite/skills/issue-creation/SKILL.md | Referenced by AGENTS.md |
| skills/branch-pr/SKILL.md | /home/jefer/dev/projects/agent-teams-lite/skills/branch-pr/SKILL.md | Referenced by AGENTS.md |

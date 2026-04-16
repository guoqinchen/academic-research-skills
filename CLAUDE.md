# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Academic Research Skills (ARS) is a **source-available Claude Code skill suite** for noncommercial academic research assistance. It consists of 4 skills with 24 total modes, covering research → paper writing → peer review → revision.

**Not a typical software project.** This is a markdown-based multi-agent orchestration framework. There is no build system. "Development" means editing markdown agent definitions, skill files, and reference documents.

## Suite Architecture

```
deep-research (7 modes)           →  academic-paper (10 modes)
  13-agent research team             12-agent paper writing
  RQ Brief → Annotated Bib →         Outline → Draft → Revise →
  Synthesis Report                   Format-convert

              ↓                          ↓
      academic-pipeline orchestrator (full 10-stage pipeline)
              ↓
      academic-paper-reviewer (6 modes)
        EIC + 3 reviewers + DA → Editorial Decision → Revision Roadmap
```

## Skills

Skill versions are maintained in `.claude/CLAUDE.md` (the authoritative skills overview).

## Key Patterns

### Handoff Schemas (`shared/handoff_schemas.md`)
All inter-skill data contracts are defined here. Schemas 1-9 define: RQ Brief, Annotated Bibliography, Synthesis Report, INSIGHT Collection, Paper Draft, Review Materials, Revision Response, Final Audit Report, Material Passport. Every consumer/producer agent pair is specified.

### Mode Spectrum (`shared/mode_spectrum.md`)
Modes span **Fidelity** (preserve/verify existing) → **Balanced** → **Originality** (generate new). Socratic modes are highest-oversight/Originality. Use this to understand what a given mode does without reading the full SKILL.md.

### Cross-Model Verification (`shared/cross_model_verification.md`)
Optional GPT-5.4 Pro or Gemini 3.1 Pro integration for integrity sampling and independent DA critique. Set `ARS_CROSS_MODEL` env var.

### Ground Truth Isolation (`shared/ground_truth_isolation_pattern.md`)
Three-tier `data_access_level` model (`raw` → `redacted` → `verified_only`). All skills declare this in SKILL.md frontmatter. Prevents downstream skills from leaking AI-generated content back as ground truth.

### Anti-Leakage Protocol (`academic-paper/references/anti_leakage_protocol.md`)
Knowledge Isolation Directive prioritizes session materials over LLM parametric memory. Flags `[MATERIAL GAP]` for missing content.

### AI Research Failure Modes (`academic-pipeline/references/ai_research_failure_modes.md`)
7-mode blocking checklist (Lu 2026). Triggers at Stage 2.5 and 4.5 integrity gates.

## Development Commands

### Linting & Validation

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all linters
python scripts/_skill_lint.py
python scripts/check_spec_consistency.py
python scripts/check_data_access_level.py
python scripts/check_task_type.py
python scripts/check_benchmark_report.py
python scripts/check_repro_lock.py

# Run specific lint
python scripts/_skill_lint.py path/to/SKILL.md

# Run with verbose output
python scripts/_skill_lint.py --verbose
```

### Tests

```bash
# All tests
python -m pytest scripts/test_*.py -v

# Single test file
python -m pytest scripts/test_check_spec_consistency.py -v

# Single test
python -m pytest scripts/test_check_spec_consistency.py::test_readme_mode_count -v
```

### CI

GitHub Actions workflow: `.github/workflows/spec-consistency.yml` — runs spec consistency, data access level, and task type checks on push/PR.

## Directory Structure

```
/                       # Root: README, LICENSE, CHANGELOG, MODE_REGISTRY
/.claude/               # OMC internal (CLAUDE.md, CHANGELOG)
/.github/workflows/     # CI: spec-consistency.yml
/scripts/               # Python lint/validation tools + tests
/shared/                # Cross-skill schemas, patterns, protocols
  handoff_schemas.md    # Schema 1-9: all inter-agent data contracts
  mode_spectrum.md      # Fidelity ↔ Originality spectrum
  cross_model_verification.md
  ground_truth_isolation_pattern.md
  benchmark_report_pattern.md
  artifact_reproducibility_pattern.md
/deep-research/        # SKILL.md, 13 agents/, references/, templates/
/academic-paper/       # SKILL.md, 12 agents/, references/, templates/
/academic-paper-reviewer/  # SKILL.md, 6 agents/, references/, templates/
/academic-pipeline/    # SKILL.md, orchestrator/, references/, templates/
/examples/             # Showcase + benchmark templates
```

## Agent Naming Convention

Agents are defined as markdown files in `*/agents/`. Naming: `*_agent.md`. Each contains frontmatter (name, description, role, rules) and is referenced by SKILL.md trigger conditions.

## Trigger Routing

Skills are invoked via keyword matching in SKILL.md. Trigger keywords include both English and Traditional Chinese phrases. Routing is handled by Claude Code's skill dispatch — the SKILL.md acts as the manifest.

## Important Constraints

- **IRON RULE markers** in any agent file cannot be modified without maintainer approval
- **Handoff schema changes** require discussion (open issue first)
- **No direct pushes** — all contributions via fork-and-PR
- **Version bumps** required on SKILL.md when releasing mode/agent changes
- **SPEC consistency check** validates README mode counts match MODE_REGISTRY

## License

CC BY-NC 4.0 — commercial use prohibited. See POSITIONING.md for allowed/discouraged uses.

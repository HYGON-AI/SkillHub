---
name: skillhub-contributor
description: Create, review, and onboard portable Agent Skills into Hygon SkillHub. Use when adding a new SKILL.md to the catalog, registering a local or remote component in components.d, preparing a SkillHub contribution, or diagnosing catalog validation and synchronization failures.
license: Apache-2.0
compatibility: Requires Python 3.11+ and Git. Network access is needed for reference checks or synchronizing an opt-in remote GitHub repository.
metadata:
  author: HYGON-AI
  version: "1.2.0"
---

# Contribute to Hygon SkillHub

A skill is local by default: it lives in this catalog and ships in one pull
request. Mirroring from any GitHub repository is an explicit opt-in for maintained
upstream skills; preserve their original authorship and licenses. Never hand-edit a
mirrored skill.

## Prerequisite

Locate a checkout of the HYGON-AI SkillHub repository before running catalog
commands. If the checkout is absent, stop and give the user the reviewed clone
or repository-location step. Do not assume `scripts/*.py` exists in a target
product repository or inside this installed skill.

## Choose the mode first

- **Local (default).** The skill has no owning product repository, or the team
  is content to maintain it here. Register with `local: true`; `repo` may be
  omitted and normalizes to `HYGON-AI/skillhub`. The source path must equal
  `skills/<catalog_dir>`.
- **Remote (opt-in).** A maintained skill is sourced from any GitHub
  repository. Register `repo` and `ref`, and let synchronization mirror it.

## Workflow

1. Confirm the owning team, the mode, license, and intended user prompts.
2. For a new skill, use `python3 scripts/new_skill.py --help` from the SkillHub checkout. Without `--repo` it creates a local skill; `--repo` authors a new package in a separate source checkout. For an existing upstream skill, register its real repository/path directly without scaffolding over it; confirm its card and license already meet admission requirements. Do not require or generate a separate eval dataset.
3. Use lowercase letters, digits, and hyphens for the directory and frontmatter `name`, and keep the name globally descriptive.
4. Keep `SKILL.md` focused on procedures the agent cannot infer. Put detailed knowledge in `references/`, deterministic helpers in `scripts/`, and output material in `assets/`. Do not nest another `SKILL.md`.
5. Complete the scaffold sections in `SKILL.md` and `skill-card.md`, record actual validation and limitations, then set the Skill Card lifecycle to `published`.
6. Review the generated `components.d/<component>.yml` change, or add it manually. Map every `path` to a globally unique `catalog_dir` and choose an allowlisted category.
7. Run `python3 scripts/generate_catalog.py`, then `python3 scripts/validate_skills.py`, `python3 scripts/validate_agent_skills_spec.py`, and `python3 scripts/generate_catalog.py --check` from the SkillHub root.
8. For a remote component only, preview synchronization with `python3 scripts/sync_sources.py --check --component <component-file-stem>`. The check must prove the ref, resolved commit, source digest, lock entry, and published tree agree. Apply it only after reviewing the reported destinations.
9. Verify the pinned `npx skills@1.5.23 add . --list` and `--full-depth`
   discovery commands both list exactly the registered published skills. A
   catalog-owned staging entrypoint must remain `SKILL.md.candidate` until
   promotion.
10. A local skill lands in one pull request. An existing publishable remote skill also needs only one SkillHub PR containing registration, mirror and lock. Change upstream first only if the source package needs work. Require Quality Gate, catalog validation, DCO and maintainer review before merge.

Read [onboarding.md](references/onboarding.md) for the component schema, release checklist, and troubleshooting commands.

## Guardrails

- Never place credentials, internal endpoints, customer data, or unpublished product information in a public skill.
- Never copy a skill from a private repository into a public catalog until the owning team has approved its public release.
- Do not edit mirrored files under `skills/` directly. Fix them in the source repository and synchronize again.
- Do not claim remote provenance for a local skill. A local skill has no lock entry and no content digest; its integrity rests on review, protected branches, required checks and DCO.
- Do not treat `staging/`, templates, CLI discovery, or a routing-only evaluation as published behavior evidence.
- Do not broaden tool permissions beyond what the skill workflow actually requires.
- Treat scripts as executable supply-chain content: review them, pin dependencies where practical, and test them before publication.

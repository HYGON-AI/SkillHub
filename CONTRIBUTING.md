# Contributing

Hygon SkillHub is a publication catalog. By default a skill lives here and ships
in one pull request. Mirroring from a product repository stays available as an
explicit opt-in, for teams that want a skill to evolve alongside the code it
documents.

## Repository lifecycle

- A local skill is written under `skills/<skill-name>/` here and registered with
  `local: true`. This is the default.
- A remote candidate remains in its source GitHub repository until admission.
- Catalog-owned prototypes may use `staging/<skill-name>/SKILL.md.candidate`;
  a real `SKILL.md` is forbidden anywhere below `staging/` so deep discovery
  cannot expose candidates.
- Only direct children of `skills/` are published catalog identities.
- Generated mirrors, catalog files and lock files are never repaired by hand.

Use [`scripts/contribute.py`](scripts/contribute.py) for interactive local
scaffolding and unified checks. The underlying `scripts/new_skill.py` and
[`templates/skill/`](templates/skill) remain available for advanced use. Read the
[repository layout](docs/architecture/repository-layout.md),
[admission policy](docs/governance/admission.md). Reuse the stable categories
in the [catalog taxonomy](docs/governance/taxonomy.md).

Workflow files are not enforcement by themselves. Before production release,
administrators must apply and verify the
[repository settings baseline](docs/governance/repository-settings.md).

## Publication boundary

SkillHub accepts maintained skills from any GitHub organization or personal repository. Every imported skill needs a catalog maintainer, permission for public redistribution, accurate source metadata and the same quality gates as local skills.

Third-party skills may be mirrored unchanged when their license permits it and their package meets admission requirements. Preserve original authorship, copyright, license and NOTICE; do not present catalog inclusion as HYGON authorship or an HCU adaptation. For an existing upstream skill, follow the [external import guide](docs/publishing/external-skills.md); no upstream PR is needed if the package is already complete.

## Add a local skill (default)

For a condensed walkthrough with the common failure messages, see
[Add a skill: quick start](docs/publishing/quickstart.md).

From a SkillHub checkout on your contribution branch, run:

```bash
python3 scripts/contribute.py new quality-gate-audit --with-references
```

Answer the prompts for author/team, description, reviewed license and category.
The helper reuses the existing generator to create a local skill and update
`components.d/skillhub.yml`. No separate registration step is needed. Optional
metadata flags allow non-interactive use; see `contribute.py new --help`.

Then:

1. Replace the scaffold `TODO` sections in `SKILL.md` and `skill-card.md`.
2. Set the Skill Card lifecycle to `published` once the evidence is real.
3. Regenerate and validate:

   ```bash
   python3 scripts/contribute.py check
   ```

4. Review the diff, commit with `--signoff`, push your branch and open one pull
   request in the GitHub browser with the content, registration and regenerated
   catalog. GitHub CLI (`gh`) is optional. Neither helper submits changes.

A local component may omit `repo`; when present it must equal
`HYGON-AI/skillhub`, and the skill's source path must equal
`skills/<catalog_dir>`. A local skill has no lock entry and no content digest:
its integrity rests on review, protected branches, required checks and DCO.

## Add a remote product skill (opt-in)

Use this only when a team maintains the skill in a separate GitHub
repository. Point the generator at that checkout with `--repo`:

```bash
python3 scripts/new_skill.py quality-gate-audit \
  --source-root ../quality-gate \
  --repo HYGON-AI/quality-gate \
  --ref main \
  --owner "Quality Gate Team" \
  --description "Audit a repository when publication readiness must be verified." \
  --license Apache-2.0 \
  --category "Governance and Compliance" \
  --product-name "Quality Gate" \
  --product-description "Repository publication and compliance gates." \
  --with-references
```

Then:

1. Add `skill-card.md`, required license and NOTICE material, and any self-contained resources.
2. Confirm the owning team approved public release and the source license permits redistribution.
3. Keep one `components.d/<component>.yml` per product team; do not edit another team's registry file.
4. **Merge the product-repository change first.**
5. Preview the mirror with `python3 scripts/sync_sources.py --check --component <component>`.
6. Apply the mirror, regenerate the catalog, and validate:

   ```bash
   python3 scripts/sync_sources.py --component <component>
   python3 scripts/contribute.py check
   ```

7. Verify discovery from a clean checkout, then open a pull request with the owning team as reviewers.

Remote synchronization currently runs on manual dispatch only. When the first
remote component is admitted, administrators must explicitly record whether to
restore scheduled synchronization and at what frequency.

## Generator notes

Use `--dry-run` to review destinations first. The generator refuses to
overwrite an existing skill, rejects malformed repositories, unapproved categories and
generic names, and requires a non-empty source `LICENSE` unless
`--license-file` names another reviewed license text. It copies a root
`NOTICE`, `NOTICE.txt` or `NOTICE.md` automatically; use `--notice-file` for a
different required notice. With `--with-references`, it also creates a linked
`references/details.md` scaffold and tells the agent when to read it. The
script emits a non-blocking warning for a small set of obvious standard-license
mismatches; it does not determine legal terms or compatibility. Reviewers must
confirm that `--license` matches the copied text and that all NOTICE obligations
are satisfied.

The generated Skill Card remains `staging` and its author-owned sections contain
`TODO` markers. Fill in the workflow, permissions, representative validation and
known limitations, then change the lifecycle to `published`. No eval dataset
is required or generated. Upstream evaluation files may be retained as optional
resources; this catalog does not execute or impose a dataset schema on them.

## Unified local checks

Install `requirements-dev.txt` with Python 3.11 or 3.12; Git and Node.js/npm are
also required (CI uses Node.js 22). `python3 scripts/contribute.py check` runs:

1. Catalog generation (updates README sections, `catalog.json`, `skills.sh.json`).
2. All repository unit tests.
3. Catalog policy and pinned Agent Skills reference validation.
4. Generated-file consistency and read-only remote provenance checks.
5. Pinned CLI discovery in normal and full-depth modes, validating both outputs
   against the registered names and count.

An optional skill name confirms its registration; it does not narrow the checks.
The command stops on failure and does not auto-install dependencies, apply remote
mirrors or modify Git branches/index/history. Inspect `git diff` after a failed
check too: successful generation may already have updated catalog files. Network
access is needed for npm downloads and for any registered remote sources.

This is the local check set, not the PR Quality Gate, DCO or human approval, and
it does not execute skill workflows. Existing individual scripts remain the CI
entrypoints so CI can detect stale files without regenerating them first.

## Add a catalog-owned staging prototype

Use `staging/` for a SkillHub-wide workflow that is not ready for admission.
Write the entrypoint as `SKILL.md.candidate` and complete the same admission
evidence as any other skill. Promotion is a reviewed change that moves the
candidate to `skills/`, renames the entrypoint to `SKILL.md`, registers it with
`local: true`, generates the catalog, and validates both normal and full-depth
discovery.

## Skill requirements

- Folder and frontmatter names use lowercase hyphen-case and match exactly.
- Use a globally descriptive name. Prefer `<product>-<action>` for
  product-specific workflows, while cross-product skills may use another clear
  capability name. Bare generic names such as `add-model`, `profile`,
  `benchmark`, `test`, `build`, and `deploy` are rejected.
- YAML frontmatter uses only Agent Skills fields: required `name` and
  `description`, plus optional `license`, `compatibility`, `metadata`, and
  experimental `allowed-tools`. Put vendor fields such as version, author and
  tags inside `metadata`, whose keys and values must all be strings.
- The description explains capability, trigger conditions, and the nearest important exclusion.
- Keep `SKILL.md` at or below 500 lines; move details into `references/`.
- Keep the published catalog flat. Do not place another `SKILL.md` inside a skill.
- Remove scaffold placeholders and every `.template` file before publication.
- Bundle every required dependency inside the skill directory. Do not depend on sibling skills or source-repository files that an installer will not copy.
- Add a schema-versioned `skill-card.md` with machine-readable owner, source,
  license and lifecycle frontmatter plus the required human-readable sections.
- Describe representative validation and known limitations in the Skill Card.
- Use only the standard optional directories `agents/`, `references/`, `scripts/`, and `assets/` unless a documented format requires another path.
- Put repeatable deterministic operations in tested `scripts/`.
- Do not include credentials, private endpoints, personal data, generated caches, or unrelated documentation.
- Do not request broader permissions than the workflow requires.
- Keep packages at or below 256 files, 5 MiB per file and 20 MiB total. Do not
  publish VCS metadata, virtual environments, dependency trees, caches or
  case-colliding paths.

## Pull request checklist

- [ ] The real source repository, ref and source path are recorded.
- [ ] Original authorship and any adaptations are described accurately.
- [ ] A catalog maintainer owns ongoing review and approved publication.
- [ ] The import PR passes Quality Gate, catalog validation and DCO before merge.
- [ ] Third-party attribution, license, and NOTICE requirements are preserved.
- [ ] The source and catalog licenses are compatible.
- [ ] The installed skill retains required LICENSE and NOTICE material.
- [ ] Scripts were reviewed and tested.
- [ ] `skill-card.md` identifies owner, source, license, lifecycle, runtime permissions, and validation boundary.
- [ ] The Skill Card states what was actually validated and what remains untested.
- [ ] The skill contains no nested `SKILL.md` or sibling-skill dependency.
- [ ] `python3 scripts/validate_skills.py` passes.
- [ ] `python3 scripts/validate_agent_skills_spec.py` passes against the pinned reference implementation.
- [ ] `python3 scripts/generate_catalog.py --check` passes.
- [ ] `python3 scripts/sync_sources.py --check` proves every remote ref, commit, digest, lock entry and mirror agree.
- [ ] `npx --yes skills@1.5.23 add . --list` discovers only the intended published skills.
- [ ] `npx --yes skills@1.5.23 add . --list --full-depth` also discovers only the intended published skills.
- [ ] No mirrored files were edited only in the catalog.

Use `git commit --signoff` so the contribution records [Developer Certificate of Origin](https://developercertificate.org/) agreement.

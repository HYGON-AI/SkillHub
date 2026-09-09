# Skill onboarding reference

## Scaffold command

From a SkillHub checkout, create a local skill and its registration together:

```bash
python3 scripts/contribute.py new example-skill --with-references
```

The prompts collect the author/team, description, license and an allowlisted
category. For unattended use, pass all four explicitly:

```bash
python3 scripts/contribute.py new example-skill --non-interactive \
  --owner "Maintaining Team" \
  --description "Describe the capability and when it should trigger." \
  --license Apache-2.0 \
  --category Inference \
  --with-references
```

Review with `--dry-run` when paths or repository checkouts are uncertain. The
generated card deliberately remains `staging`; complete every `TODO`, record
representative validation and limitations, and set `published` only after
the evidence is ready. A local skill then lands in one pull request. For a
new remote source skill, use `scripts/new_skill.py <name> --repo <owner>/<repository>`
with `--source-root <checkout>`, `--owner`, `--description`, `--license` and
`--category` (`--non-interactive` belongs only to the wrapper). Commit and merge
the source repository first; the component
change remains local in SkillHub until the source ref contains the reviewed
Skill. With `--with-references`, the generated `SKILL.md` links to the new
`references/details.md` scaffold so contributors can state when detailed
material should be loaded.

## Component schema

Local generation updates the shared `components.d/skillhub.yml`; do not create
a second component for the same catalog repository. A local entry looks like:

```yaml
name: Component display name
local: true
description: One sentence describing the component and its skills.
skills:
  - path: skills/example-skill
    catalog_dir: example-skill
    category: Inference
```

`repo` may be omitted and normalizes to `HYGON-AI/skillhub`; any other value is
rejected, and `path` must equal `skills/<catalog_dir>`.

A remote component is the explicit opt-in for a skill maintained by an upstream
repository:

```yaml
name: Product display name
repo: HYGON-AI/product-repository
ref: main
description: One sentence describing the product and its skills.
skills:
  - path: skills/example-skill
    catalog_dir: example-skill
    category: Inference
```

Remote components are cloned from GitHub during synchronization and carry a
`.skillhub-lock.json` entry with the resolved commit and tree digest. Local
skills carry neither.

For a catalog-owned prototype, begin with
`staging/<skill-name>/SKILL.md.candidate`. Never use a real `SKILL.md` below
`staging/`; deep discovery can install it before review. During promotion, move
the candidate into `skills/<skill-name>/`, rename the entrypoint to `SKILL.md`,
add its local component registration, and add the same Skill Card and license
evidence required from every published skill.

Each `catalog_dir` must be unique across the catalog and equal the skill's frontmatter `name`.

## Release checklist

- The owning team approved public release.
- `SKILL.md` uses only the six Agent Skills fields; `metadata` keys and values
  are strings and client/catalog fields do not leak into portable frontmatter.
- The description says both what the skill does and when it should trigger.
- The published directory is flat and contains no nested `SKILL.md`.
- `skill-card.md` uses schema version 1 and binds owner, component source,
  license and published lifecycle.
- The Skill Card records representative validation and known limitations.
  A separate eval dataset is not required.
- Relative Markdown links in `SKILL.md`, `skill-card.md`, and references resolve inside the skill directory.
- Scripts contain no embedded credentials and have been executed on a representative input.
- The source repository has an explicit compatible license.
- Required LICENSE and NOTICE material remains available after isolated installation.
- A remote component records the reviewed source branch or release tag; its lock
  pins the resolved commit and tree digest. Local components need neither.
- Local validation and catalog generation checks pass.

## Commands

```bash
python3 scripts/contribute.py check
```

This regenerates catalog files and runs all local checks, including both pinned
CLI discovery modes and their output validators. Install `requirements-dev.txt`,
Git and Node.js/npm first; the helper does not install missing dependencies.
Specifying a skill name only confirms its registration; checks remain global.

For remote imports or updates, preview and apply separately before running the
unified check:

```bash
python3 scripts/sync_sources.py --check --component product-slug
python3 scripts/sync_sources.py --component product-slug
python3 scripts/contribute.py check
```

First-import preview returns nonzero because no mirror/lock exists yet. Review
the source and destinations before applying. `contribute.py check` never applies
remote updates. Review its generated diff and submit manually with
`git commit --signoff`, a branch push and a browser PR when authorized. No `gh` is required;
PR Quality Gate, DCO and maintainer review are not replaced by local checks.

After publication, verify discovery without installing:

```bash
npx --yes skills@1.5.23 add HYGON-AI/skillhub --list
```

Install one skill non-interactively:

```bash
npx --yes skills@1.5.23 add HYGON-AI/skillhub --skill example-skill --yes
```

## Common failures

- **Unregistered directory**: add the skill to exactly one component file or remove the orphaned catalog directory.
- **Name mismatch**: make `skills/<directory>` and frontmatter `name` identical.
- **Catalog drift**: run `python3 scripts/generate_catalog.py` and commit all generated files.
- **Private clone failure**: grant the synchronization token read access to the product repository without placing the token in a URL.
- **Mirrored edit overwritten**: make the change in the source repository, merge it there, then synchronize again.

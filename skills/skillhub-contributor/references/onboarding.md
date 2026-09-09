# Skill onboarding reference

## Scaffold command

From the SkillHub checkout, create a local directory and registration together:

```bash
python3 scripts/contribute.py new example-skill --with-references
```

Review with `--dry-run` when paths are uncertain. The generated card deliberately
remains `staging`; complete every `TODO` and set `published` only after the
evidence is ready. For an existing package, use
`python3 scripts/contribute.py import ../existing-skill` instead of scaffolding
over it. With `--with-references`, the generated `SKILL.md` links to the new
`references/details.md` scaffold so contributors can state when detailed
material should be loaded.

## Component schema

Create `components.d/<slug>.yml`. A local component is the default:

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
add its local component registration, and add the same Skill Card, Eval and
license evidence required from every published skill.

Each `catalog_dir` must be unique across the catalog. Keep it equal to the skill frontmatter `name` unless a temporary compatibility alias is unavoidable.

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
- The component registry points to an immutable release branch or the team's maintained default branch.
- Local validation and catalog generation checks pass.

## Commands

```bash
python3 scripts/contribute.py check
# Remote synchronization is opt-in and separate from the local contribution flow.
python3 scripts/sync_sources.py --check --component product-slug
python3 scripts/sync_sources.py --component product-slug
```

After publication, verify discovery without installing:

```bash
npx skills add HYGON-AI/skillhub --list
```

Install one skill non-interactively:

```bash
npx skills add HYGON-AI/skillhub --skill example-skill --yes
```

## Common failures

- **Unregistered directory**: add the skill to exactly one component file or remove the orphaned catalog directory.
- **Name mismatch**: make `skills/<directory>` and frontmatter `name` identical.
- **Catalog drift**: run `python3 scripts/generate_catalog.py` and commit all generated files.
- **Private clone failure**: grant the synchronization token read access to the product repository without placing the token in a URL.
- **Mirrored edit overwritten**: make the change in the source repository, merge it there, then synchronize again.

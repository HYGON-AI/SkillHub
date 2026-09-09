# Add a skill: quick start

The normal path is a local skill: create or import it in this repository, review
the content, run one local check command, and open one pull request. For the
normative rules see
[CONTRIBUTING.md](../../CONTRIBUTING.md); for the release flow see
[publishing](README.md).

```
contribute.py new | import
  -> review SKILL.md and generated skill-card.md (already published)
  -> contribute.py check
  -> commit --signoff, open one pull request
```

## 1. Create a branch

```bash
git checkout -b feat/add-<skill-name>
```

## 2. Add the skill

For a new skill, run the interactive local scaffold:

```bash
python3 scripts/contribute.py new <skill-name>
```

The command asks for owner, description and category, then creates the
skill directory and local registration. Original contributions default to the
root Apache-2.0 license; no duplicate LICENSE file is generated. Use `--dry-run` to preview destinations,
`--with-references` to create a linked reference scaffold, or `--help` to see
flags for non-interactive automation.

For an existing skill directory, import its package instead:

```bash
python3 scripts/contribute.py import ../existing-skill
```

`import` copies one flat skill directory, including `SKILL.md`, `references/`,
`scripts/`, `assets/` and bundled LICENSE/NOTICE material. It does not execute
source files or modify the source directory. It reuses source metadata where it
is trustworthy, asks only for missing values, and always changes the imported
Skill Card lifecycle to `published`. It is a one-time local copy, not upstream
synchronization.

The category must match [the taxonomy](../governance/taxonomy.md) exactly; a
wrong value prints the allowed set. Bare generic names such as `profile`,
`benchmark`, `test`, `build` and `deploy` are rejected.

## 3. Fill in the content

This is the only step no helper can do for the author.

- **`SKILL.md`** -- replace the body, keeping the generated frontmatter. Stay at
  or below 500 lines and move detail into `references/`.
- **Bundled files** -- copy any `scripts/`, `references/` or `assets/` the skill
  needs into the skill directory. Everything it needs must be inside it.
- **`skill-card.md`** -- review the generated metadata; lifecycle already defaults
  to `published`. Runtime requirements and permissions are collected by the command
  or supplied with `--runtime-permissions`. You may refer to SKILL.md instead of
  repeating documented requirements. Non-interactive use defaults to that reference.

No separate eval file or Skill Card Validation section is required.

## 4. Check, then submit

```bash
python3 scripts/contribute.py check
```

This runs catalog generation, unit tests, policy validation, Agent Skills
validation, generated-file checks, remote-provenance checks (when present), and
normal/full-depth CLI discovery. It regenerates catalog files but never updates
a remote mirror or submits Git changes.

```bash
git add -A
git commit --signoff -m "feat(skills): add <skill-name>"
git push -u origin feat/add-<skill-name>
```

One pull request carries the content, its registration and the regenerated
catalog files. `--signoff` is required; the DCO check fails without it. Open
the pull request in the GitHub browser; `gh` is not required.

## Common failures

| Message | Cause |
| --- | --- |
| `lifecycle must equal 'published'` | The Skill Card is still `staging` |
| `unresolved scaffold placeholder` | A `TODO` or `Replace with` marker remains |
| `Catalog files are out of date` | Run `python3 scripts/contribute.py check` |
| `category must be one of: ...` | The category is not in the taxonomy allowlist |
| `template scaffold file is not publishable` | A `.template` file was copied in unrenamed |
| `Conflicting license declarations` during import | Existing declarations and an explicit `--license` disagree; resolve the conflict without overwriting source rights. Undeclared original imports default to Apache-2.0; no license or source URL prompt is required. |
| DCO check fails | The commit is missing `--signoff` |

## Remote components (opt-in)

Remote sources use GitHub `<owner>/<repository>` form; they are not restricted
to the HYGON-AI organization. This is different from `contribute.py import`,
which makes a one-time locally maintained copy. Choose the path that matches
your source:

- **Keep an existing skill synchronized:** register and mirror the existing
  package; follow [Import external skills](external-skills.md).
- **Create a new skill in a source repository:** use the authoring steps below,
  merge the source change first, then submit the SkillHub import PR.

An existing upstream package must already meet the publication contract;
do not scaffold over an existing skill.

Use the following authoring flow when a team maintains the skill in a separate GitHub
repository and wants it to evolve alongside the code it documents. Everything
above still applies; the differences are that the skill is authored elsewhere,
the change lands in two repositories, and the mirror carries provenance.

```
new_skill.py --repo ...
  -> fill TODOs in the SOURCE repository
  -> merge the source pull request FIRST
  -> sync_sources.py --check   (preview)
  -> sync_sources.py           (apply)
  -> generate_catalog.py, validate
  -> commit --signoff, open the SkillHub pull request
```

### Scaffold a new skill into the source repository

Replace the angle-bracket placeholders before running the command. `--repo`
identifies the source repository; `--owner` records the skill's author or
maintaining team and need not match the GitHub account name.

```bash
python3 scripts/new_skill.py <skill-name> \
  --source-root ../<source-checkout> \
  --repo <owner>/<repository> \
  --ref main \
  --owner "Author or maintaining team" \
  --description "What it does, when it triggers, and the nearest case that must not trigger it." \
  --license Apache-2.0 \
  --category "Operator Development" \
  --product-name "Display name" \
  --product-description "One sentence about the source project and its skills."
```

The skill files are written under `<source-checkout>/skills/<skill-name>/`,
and the registration is written to `components.d/<component>.yml` here.

### Merge the source change first

Fill in the `TODO` markers in the source repository, then merge that pull
request. Synchronization resolves the registered `ref` to a concrete commit, so
the content must already be on that ref before the mirror can be applied.

### Preview, then apply the mirror

```bash
python3 scripts/sync_sources.py --check --component <component>
```

The check fetches the source and compares its resolved commit and content with
the lock and published mirror without writing catalog files. A first import
with no mirror or lock returns nonzero for expected drift. Review the source
and registered destination before applying:

```bash
python3 scripts/sync_sources.py --component <component>
python3 scripts/generate_catalog.py
python3 scripts/validate_skills.py
python3 scripts/validate_agent_skills_spec.py
python3 scripts/generate_catalog.py --check
python3 scripts/sync_sources.py --check --component <component>
```

Applying the mirror also writes a `.skillhub-lock.json` entry recording the
resolved commit and the source-tree SHA-256 digest. Open the SkillHub pull
request with the catalog maintainer as reviewer. Quality Gate, catalog validation
and DCO must pass before merge. Manually opening a PR does not require GitHub App
credentials; automated sync PRs require the App configuration described in
[repository settings](../governance/repository-settings.md). Both paths need the
quality runner and required branch checks configured for enforced quality review.

### Rules that differ from the local path

- The mirrored files under `skills/` are generated. Never edit them here: fix
  the source repository and synchronize again, or the digest check fails.
- One repository is registered by exactly one component, and every skill in
  that component shares one `ref`. Skill-level ref overrides are not supported.
- Synchronization currently runs on manual dispatch only. Admitting the first
  remote component requires an explicit decision on whether to restore
  scheduled synchronization and at what frequency.

### Additional failures

| Message | Cause |
| --- | --- |
| `does not contain SKILL.md` | The source path is wrong, the skill was deleted, or its change is not on the registered `ref` yet |
| `drift <name>: published tree does not match resolved source` | A mirrored file was hand-edited here |
| `remote component requires repo` | `local` is false but no `repo` was given |
| `source package is not publishable` | The source directory fails the same portability gates |

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for the normative rules and
[supply-chain integrity](../security/supply-chain.md) for what the recorded
commit and digest do and do not prove.

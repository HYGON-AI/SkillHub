# Add a skill: quick start

For a local skill (the default), use two helper commands and submit with your
normal Git workflow. The helper does not create branches, stage, commit, push,
or open pull requests. **GitHub CLI (`gh`) is not required.** For the normative rules see
[CONTRIBUTING.md](../../CONTRIBUTING.md); for the release flow see
[publishing](README.md).

```
contribute.py new <name>
  -> fill TODOs, set lifecycle: published
  -> contribute.py check
  -> submit manually with Git and a browser PR
```

## Before you start (once per checkout)

External contributors fork the repository on GitHub and clone their fork.
Team members with write access can clone the repository directly. Run commands
from the checkout root, with Python 3.11 or 3.12, Git and Node.js/npm installed
(CI uses Node.js 22). Install the pinned Python dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

On Windows, use `python` if `python3` is unavailable. Initial Python dependency
installation needs PyPI/GitHub access; CLI downloads need npm access. No GPU or
model API key is required for these catalog checks.

Create your contribution branch using ordinary Git:

```bash
git checkout -b feat/add-<skill-name>
```

## 1. Create

```bash
python3 scripts/contribute.py new <skill-name>
```

Answer four prompts: author/maintaining team, capability and trigger description,
reviewed license expression, and category (choose a number or exact name).
The helper creates `skills/<skill-name>/`, copies the selected LICENSE and any
required NOTICE, and adds the registration to `components.d/skillhub.yml`.
It does not invent license terms or overwrite existing skills.

Add `--dry-run` to preview destinations, `--with-openai` for optional agent UI
metadata, or `--with-references` for a reference scaffold linked from `SKILL.md`.
Use these only when needed. For automation or to avoid prompts, provide all
four values explicitly:

```bash
python3 scripts/contribute.py new <skill-name> --non-interactive \
  --owner "Owning team" \
  --description "What it does, when it triggers, and the nearest case that must not trigger it." \
  --license Apache-2.0 \
  --category "Developer Tools"
```

The default copied license is the checkout's root LICENSE. If your reviewed
license differs, pass `--license-file <path>` and any required `--notice-file`.
The declared expression and copied text must match; reviewers confirm this.

The category must match [the taxonomy](../governance/taxonomy.md) exactly; a
wrong value prints the allowed set. Bare generic names such as `profile`,
`benchmark`, `test`, `build` and `deploy` are rejected.

## 2. Complete the content and check

This is the only step a generator cannot do.

- **`SKILL.md`** -- replace the body, keeping the generated frontmatter. Stay at
  or below 500 lines and move detail into `references/`.
- **Bundled files** -- copy any `scripts/`, `references/` or `assets/` the skill
  needs into the skill directory. Everything it needs must be inside it.
- **`skill-card.md`** -- replace each `TODO`, then **change `lifecycle: staging`
  to `published`**. State the validation boundary honestly: what was actually
  exercised, and what a passing check does not prove.

No separate eval file is needed. Describe what you actually tried, the observed
results and known limitations in the Skill Card's **Validation** section.

When the content is ready, run one command:

```bash
python3 scripts/contribute.py check
```

It generates the catalog, runs the unit tests, validates catalog policy and
Agent Skills compatibility, checks generated files and remote provenance, and
verifies normal/full-depth CLI discovery against the registered names and count.
It stops on a failure and leaves the original error visible.

You can also run `python3 scripts/contribute.py check <skill-name>` to confirm
that name is registered. **Both forms check the whole repository**, not just
one skill. Local checks do not execute skill workflows or prove their behavior.

The command may update README catalog sections, `catalog.json` and
`skills.sh.json`; inspect the diff even after a later check fails. Remote
components, if any, are fetched for comparison only. The helper does not apply
remote updates, install missing dependencies or change Git's index/history.

## 3. Submit yourself

Review and stage only this contribution's files, then commit and push:

```bash
git diff
git status --short
git add skills/<skill-name>/ components.d/skillhub.yml README.md catalog.json skills.sh.json
git commit --signoff -m "feat(skills): add <skill-name>"
git push -u origin feat/add-<skill-name>
```

Open GitHub in your browser and create a pull request from your pushed branch
to the catalog's `main` branch (from your fork if applicable). One PR carries
the content, registration and regenerated catalog files. `--signoff` is required;
the DCO check fails without it. Local success does not replace PR Quality Gate,
DCO or maintainer review. If you already use `gh`, you can use it, but it is optional.

## Common failures

| Message | Cause |
| --- | --- |
| `lifecycle must equal 'published'` | The Skill Card is still `staging` |
| `unresolved scaffold placeholder` | A template-specific marker remains; complete the Skill Card's TODOs too |
| `STALE: ...` | Catalog files drifted; rerun `contribute.py check` before submission |
| `category must be one of: ...` | The category is not in the taxonomy allowlist |
| `template scaffold file is not publishable` | A `.template` file was copied in unrenamed |
| DCO check fails | The commit is missing `--signoff` |
| `Missing Python dependencies` / `Missing tools on PATH` | Install `requirements-dev.txt`, Git and Node.js/npm; then retry |

## Remote components (opt-in)

Remote sources use GitHub `<owner>/<repository>` form; they are not restricted
to the HYGON-AI organization. Choose the path that matches your source:

- **Import an existing skill:** register and synchronize the existing package
  in one SkillHub PR; follow [Import external skills](external-skills.md).
- **Create a new skill in a source repository:** use the authoring steps below,
  merge the source change first, then submit the SkillHub import PR.

An existing upstream package must already meet the publication contract;
do not scaffold over an existing skill.

Use the following authoring flow when a team maintains the skill in a separate GitHub
repository and wants it to evolve alongside the code it documents. The same
content and validation requirements apply; the differences are that the skill is authored elsewhere,
the change lands in two repositories, and the mirror carries provenance.

```
new_skill.py --repo ...
  -> fill TODOs in the SOURCE repository
  -> merge the source pull request FIRST
  -> sync_sources.py --check   (preview)
  -> sync_sources.py           (apply)
  -> contribute.py check
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
python3 scripts/contribute.py check
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

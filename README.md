# HYGON-AI Agent Skills

<div align="center">

<img src="assets/banner.gif" alt="HYGON SkillHub: agent skills for HCU, grouped by governed catalog category" width="1200"/>

</div>

Portable [Agent Skills](https://agentskills.io/specification) for [HYGON-AI](https://github.com/HYGON-AI) software, infrastructure, training, inference, operator and general engineering workflows.

The default path is simple: **a skill lives in this repository and ships in one pull request.** You can also import a maintained skill from any GitHub organization or personal repository, preserving its upstream source, authorship and license.

## Quick start

After publication to `HYGON-AI/skillhub`, browse or install skills with the standard
[`skills` CLI](https://github.com/vercel-labs/skills). These examples use the
same CLI version as our compatibility checks and require Node.js/npm:

```bash
npx --yes skills@1.5.23 add HYGON-AI/skillhub --list
npx --yes skills@1.5.23 add HYGON-AI/skillhub
```

Install one skill into a specific agent without prompts:

```bash
npx --yes skills@1.5.23 add HYGON-AI/skillhub --skill skillhub-contributor --agent claude-code --yes
```

Pass `--agent` more than once to install into several supported agents:

```bash
npx --yes skills@1.5.23 add HYGON-AI/skillhub --skill skillhub-contributor \
  --agent claude-code --agent codex --agent cursor --yes
```

The CLI supports multiple agents, including `claude-code`, `codex` and `cursor`.
Run the installation command without `--agent` to choose interactively where
supported. Available agents depend on the CLI version and local environment;
each skill's tools, permissions and runtime requirements still apply.

## Add a skill

External contributors should fork this repository, clone their fork, and run
the following commands from its root. Team members with write access may clone
this repository directly and contribute on a branch.

Use Python 3.11 or 3.12 and Git; Node.js/npm is needed for CLI discovery (CI uses
Node.js 22). Install the pinned Python dependencies once:

```bash
python3 -m pip install -r requirements-dev.txt
```

Initial dependency installation needs access to PyPI and GitHub; CLI downloads
use npm. Catalog checks do not require a GPU or model API key. On Windows, use
`python` if your interpreter is not available as `python3`.

Create a branch, scaffold a local skill, complete its instructions and Skill
Card, then validate and open one pull request:

```bash
git checkout -b feat/add-my-skill-name
python3 scripts/new_skill.py my-skill-name \
  --owner "Owning team" \
  --description "What it does, when it triggers, and the nearest case that must not trigger it." \
  --license Apache-2.0 \
  --category "Developer Tools"
```

To create a **new skill in a separate GitHub repository**, pass
`--repo <owner>/<repository>` together with `--source-root <checkout>`.
To **import an existing skill**, register its real source and synchronize it;
follow the [external import guide](docs/publishing/external-skills.md).
Do not scaffold over an existing upstream package.

No separate eval dataset is required. Record actual validation and limitations
in the Skill Card. See the [quick start](docs/publishing/quickstart.md) for the full walkthrough and
[CONTRIBUTING.md](CONTRIBUTING.md) for the normative rules.

## Repository structure

The repository separates candidate content, source registration, published
skills, validation records, and generated metadata:

| Path | Purpose |
| --- | --- |
| [`skills/`](skills) | Flat catalog of published, independently installable skills |
| [`staging/`](staging) | Catalog-owned `SKILL.md.candidate` files that cannot be discovered |
| [`components.d/`](components.d) | One reviewed registration per component, local or remote |
| [`templates/`](templates) | Non-discoverable contribution scaffolds |
| [`assets/`](assets) | Repository-level README media; never skill content |
| [`docs/`](docs) | Architecture, admission and release policy |

Every direct child of `skills/` is one catalog identity. Published skills must
not contain nested `SKILL.md` files or depend on sibling skills. See the
[normative repository layout](docs/architecture/repository-layout.md) and
[admission policy](docs/governance/admission.md).

## Skill catalog

<!-- catalog:start -->

| Product | Description | Skills |
|---|---|---|
| **SkillHub** | Author, validate, onboard, and publish portable Agent Skills across HYGON-AI projects. | [`audit-hygon-open-source`](skills/audit-hygon-open-source), [`audit-hygon-quality-security`](skills/audit-hygon-quality-security), [`skillhub-contributor`](skills/skillhub-contributor), [`torch-trace-operator-profiler`](skills/torch-trace-operator-profiler) |

<!-- catalog:end -->

## Skills by category

<!-- categories:start -->

4 skills across 3 categories.

### Developer Tools

| Skill | Product | Description |
|---|---|---|
| [`skillhub-contributor`](skills/skillhub-contributor) | SkillHub | Create, review, and onboard portable Agent Skills into Hygon SkillHub. Use when adding a new SKILL.md to the catalog, registering a local or remote component in components.d, preparing a SkillHub contribution, or diagnosing catalog validation and synchronization failures. |

### Governance and Compliance

| Skill | Product | Description |
|---|---|---|
| [`audit-hygon-open-source`](skills/audit-hygon-open-source) | SkillHub | Assess repository release readiness by reviewing licensing, notices, source provenance, file metadata, and commit history. Use when preparing a fixed Git revision for distribution or generating a concise Chinese remediation report. |
| [`audit-hygon-quality-security`](skills/audit-hygon-quality-security) | SkillHub | Assess a fixed Git revision for release-readiness quality and security issues, compare against a declared baseline when needed, and generate a concise Chinese remediation report. Use before release to review code quality, dependency risk, workflow integrity, and secret exposure. |

### Performance and Profiling

| Skill | Product | Description |
|---|---|---|
| [`torch-trace-operator-profiler`](skills/torch-trace-operator-profiler) | SkillHub | Analyze a torch.profiler Chrome/Perfetto JSON trace to attribute time across Python scopes, ATen operators, GPU kernels, runtime API overhead and memory copies. Use when diagnosing a slow PyTorch operator, custom extension, Triton kernel or submodule from a captured trace. |

<!-- categories:end -->

## How publication works

A local skill, which is the default:

1. The skill is written under `skills/<skill-name>/` in this repository.
2. A `components.d/<component>.yml` file registers it with `local: true`.
3. Admission review checks ownership, licensing, self-containment, intended use, and the validation results and limitations recorded in the Skill Card.
4. Validation checks naming, frontmatter, resources, Skill Cards, licenses, secrets, and generated catalog drift.
5. One pull request lands the content, its registration and the regenerated catalog.

A remote component, when a catalog maintainer opts in:

1. Select a self-contained skill from any maintained GitHub repository; see the [external import guide](docs/publishing/external-skills.md).
2. A `components.d/<component>.yml` file records the repository, ref and source path.
3. Synchronization mirrors the registered content and records the resolved commit and digest.
4. Registration, mirror, lock and regenerated catalog files go into one SkillHub PR; the same admission and validation requirements apply before merge.

Later remote updates use the manual synchronization workflow, which opens or
updates a PR. Automated PR creation requires a configured GitHub App; manually
preparing an import and opening a PR does not require that App.

Catalog maintainers can run:

```bash
python3 scripts/generate_catalog.py
python3 scripts/validate_skills.py
python3 scripts/validate_agent_skills_spec.py
python3 scripts/generate_catalog.py --check
```

For remote components, also run
`python3 scripts/sync_sources.py --check --component <component-file-stem>`.
The quick start and CONTRIBUTING include the remaining test and CLI discovery steps.

See [CONTRIBUTING.md](CONTRIBUTING.md) for both paths.

Catalog-owned prototypes may use `staging/`. Remote candidates stay
in their source repositories until admission; `staging/` is not a second
source mirror. A candidate entrypoint is named `SKILL.md.candidate` until its
reviewed promotion into `skills/`, preventing deep-discovery clients from
installing staging content.

## Trust model

The catalog publishes reviewed content; it does not make arbitrary third-party skills trusted. Consumers should still review executable scripts and permissions before installation.

A **local skill** is reviewed here and has no `.skillhub-lock.json` entry or
remote content digest. Its intended protection is Git history, protected
branches, required checks, CODEOWNERS review and DCO sign-off.

**Deployment status:** the PR Quality Gate workflow is configured in code, but
the current repository still needs an isolated `quality` runner and required
branch checks; automated synchronization also needs GitHub App credentials.
Until these are configured and verified, workflow files alone do not enforce
review or block merging. See the [repository settings checklist](docs/governance/repository-settings.md).

A **remote component** additionally records its repository, ref, and source path
in [`catalog.json`](catalog.json), with synchronized commits and tree digests in
[`.skillhub-lock.json`](.skillhub-lock.json). See
[supply-chain integrity](docs/security/supply-chain.md) for what each mode does
and does not prove.

CLI discovery confirms that the installer can find the registered skills.
Published status additionally
requires the owner, license, source, lifecycle and validation limits recorded
in `skill-card.md`. No separate eval dataset is required.
The catalog additionally enforces exact remote commit/digest provenance and a
pinned Agent Skills reference-validation pass; neither check alone proves that
a Skill's operational behavior is correct.

## Source attribution

Source repositories remain the source of truth for mirrored skills, including personal and third-party GitHub repositories. The catalog preserves upstream authorship and license terms and records each repository, ref and path in `catalog.json`. Imports require quality checks and maintainer review; inclusion does not imply HYGON authorship or HCU adaptation.

## License

Repository code and catalog-owned skill content are licensed under the [Apache License 2.0](LICENSE) unless stated otherwise. Mirrored skill content remains under its source license, and imported skills must carry a license compatible with public redistribution.

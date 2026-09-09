# Import external skills

SkillHub accepts GitHub organization and personal repositories. An existing,
publishable upstream package needs one SkillHub PR; its repository does not
need to install our CI. Local contributions remain the default.

## First import

1. Confirm the license permits redistribution, preserve upstream attribution
   and required LICENSE/NOTICE files, and identify a catalog maintainer in the
   PR. The upstream package must already include a matching Skill Card.
   If it lacks them, ask upstream to add them or maintain a licensed local copy
   with original attribution. Do not patch a remote mirror by hand.
2. Create a contribution branch and add `components.d/tool-skills.yml`:

   ```yaml
   name: Tool Skills
   repo: someone/tool-skills
   ref: main
   description: Maintained application log analysis skills.
   skills:
     - path: skills/log-analyzer
       catalog_dir: log-analyzer
       category: Developer Tools
   ```

   Replace the example repository and path with the actual source. `ref` is an
   existing branch or release tag. `catalog_dir` must be globally unique and
   match the Skill's frontmatter `name`. Skill Card source
   metadata must match the registered repository and source path. One component
   registers one repository and one ref.
3. Import and validate from the SkillHub root:

   ```bash
   python scripts/sync_sources.py --component tool-skills
   python scripts/generate_catalog.py
   python -m unittest discover -s tests
   python scripts/validate_skills.py
   python scripts/validate_agent_skills_spec.py
   python scripts/generate_catalog.py --check
   python scripts/sync_sources.py --check --component tool-skills
   ```

   Apply mode creates the mirror and lock entry. `--check` reports drift and
   exits nonzero for a first import without a mirror/lock; that is expected.
   Follow CONTRIBUTING's normal and full-depth CLI discovery checks as well.
4. Commit with sign-off and open a SkillHub PR containing the registration,
   mirror, `.skillhub-lock.json` and generated catalog files. Quality Gate,
   catalog validation and DCO must pass, followed by maintainer review.
   Do not merge a source-only registration before its mirror and lock.

## Subsequent updates

After the first import is merged, run **Sync Opt-in Product Skills** manually
from Actions. It fetches registered sources, validates packages, updates mirrors
and locks, then uses the configured GitHub App to create/update a PR. All PR
checks run again. No automatic merge is performed. If the source ref moves
during review, re-sync; the provenance check compares against the current ref.

For automated PRs, administrators must first configure the App and isolated
quality runner described in [repository settings](../governance/repository-settings.md).
Until then, maintainers can prepare the import locally and open a PR, but must
wait for the quality runner and required checks before publishing it.

## Failures

- Missing ref, deleted Skill, invalid package or failed quality check: fix the
  source/registration and retry; do not merge a partial import.
- Sync operates in an expendable checkout and may have updated earlier packages
  before a later source fails. The workflow stops before pushing a PR. For a
  local multi-component failure, inspect/discard only generated changes on your
  contribution branch and rerun; do not assume repository-wide rollback.
- Private sources require narrowly scoped read credentials and explicit public
  redistribution approval; access to a repository alone is not permission.
- A name collision requires an upstream rename or a separately maintained local
  adaptation. Changing only `catalog_dir` does not rename the remote package.

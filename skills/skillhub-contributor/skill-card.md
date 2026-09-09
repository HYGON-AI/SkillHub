---
schema_version: 1
owner: HYGON-AI SkillHub maintainers
source:
  repo: HYGON-AI/skillhub
  path: skills/skillhub-contributor
license: Apache-2.0
lifecycle: published
---

# Skill Card

## Summary

Creates, reviews, registers, synchronizes, and validates portable skills for
the HYGON-AI organization catalog.

## Owner

HYGON-AI SkillHub maintainers.

## Source

- Repository: `HYGON-AI/skillhub`
- Path: `skills/skillhub-contributor`
- Lifecycle: `published`
- Ownership: catalog-owned

## License

Apache-2.0. The full license text is bundled in this installed skill directory.

## Runtime and permissions

Requires a checkout of SkillHub, Python 3.11 or newer, its development dependencies
and Git; full local checks require Node.js/npm. Network access is needed for
dependency downloads and any registered remote sources. GitHub CLI is optional.
Scaffolding and `contribute.py check` need local write access: the latter updates
catalog metadata before running checks. Individual validators and synchronization
preview do not update catalog content. The helper never stages, commits, pushes
or opens PRs, and submission needs separate user authorization.

## Validation

The catalog's unit tests, structural validation, generated catalog check, and
skills CLI discovery are the applicable evidence. Contribution-helper tests cover
prompted and unattended scaffolding, cancellation without partial output, and
failure propagation from checks and both CLI output validators. They do not prove that a
newly contributed skill behaves correctly; each skill should describe actual
validation and limitations in its Skill Card, without a separate eval form.
A local skill has no lock entry or content digest, so its
integrity evidence is review, protected branches, required checks and DCO
rather than remote provenance.
Local checks do not run the PR Quality Gate or establish that server-side
branch protection, DCO and maintainer review have passed.

# Contribution templates

Templates are deliberately non-discoverable: every scaffold-only file uses a
`.template` suffix. Published packages reject any remaining `.template` file.

Prefer `python3 scripts/contribute.py new <name>` for local skills: it prompts
for metadata and reuses `new_skill.py` to write the final filenames,
fills deterministic identity fields, copies reviewed license material, and
builds the component registration. These templates remain the manual fallback.

For manual creation, copy `templates/skill/` to this checkout's
`skills/<skill-name>/`, rename the package files listed in
`README.md.template`, delete that scaffold README, replace every placeholder,
and validate the installed directory in isolation before requesting catalog
admission.

For opt-in remote authoring, use `scripts/new_skill.py --repo` with a separate
source checkout. Do not run either scaffold generator over an existing skill.

#!/usr/bin/env python3
"""Scaffold a local skill or run the existing catalog checks; never submit Git changes."""

# Copyright (c) 2026 Hygon Information Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

import argparse
import importlib
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


class ContributionError(ValueError):
    """An actionable setup or check failure."""


def local_module(name):
    return importlib.import_module(f"{__package__}.{name}" if __package__ else name)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Create a local skill or generate and validate the catalog. No Git submission.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser("new", help="scaffold a local skill; prompt for missing metadata")
    new.add_argument("name", help="globally descriptive lowercase-hyphen skill name")
    new.add_argument("--owner", help="original author or maintaining team")
    new.add_argument("--description", help="capability and trigger-boundary description")
    new.add_argument("--license", help="reviewed SPDX expression; never chosen automatically")
    new.add_argument("--category", help="exact category from the taxonomy")
    new.add_argument("--license-file", help="reviewed license text; defaults to the root LICENSE")
    new.add_argument("--notice-file", help="required notice; defaults to an existing root NOTICE")
    new.add_argument("--with-openai", action="store_true", help="create agents/openai.yaml")
    new.add_argument("--with-references", action="store_true", help="create a linked reference scaffold")
    new.add_argument("--dry-run", action="store_true", help="show destinations without writing")
    new.add_argument("--non-interactive", action="store_true", help="fail if required metadata is missing")
    check = commands.add_parser("check", help="regenerate catalog files and run all local checks")
    check.add_argument(
        "name", nargs="?",
        help="confirm this skill is registered; checks still cover the whole repository",
    )
    return parser.parse_args(argv)


def prompt_value(label, categories=None):
    if categories:
        for number, category in enumerate(categories, 1):
            print(f"  {number}. {category}")
    while True:
        try:
            value = input(f"{label}: ").strip()
        except EOFError as exc:
            raise ContributionError(
                "Input ended before metadata was complete; no scaffold was written. "
                "Provide --owner, --description, --license and --category for non-interactive use."
            ) from exc
        if categories:
            if value in {str(i) for i in range(1, len(categories) + 1)}:
                return categories[int(value) - 1]
            if value in categories:
                return value
            print("Choose a listed number or an exact category name.")
        elif value:
            return value
        else:
            print("A non-empty value is required.")


def new_skill(args, root):
    generator = local_module("new_skill")
    fields = (
        ("owner", "Author or maintaining team"),
        ("description", "What it does and when it should (or should not) trigger"),
        ("license", "Reviewed SPDX expression (for example Apache-2.0; must match the copied text)"),
        ("category", "Category number or name"),
    )
    missing = [f"--{field}" for field, _ in fields if not getattr(args, field)]
    if missing and args.non_interactive:
        raise ContributionError("Missing required metadata: " + ", ".join(missing))
    argv = [args.name, "--local", f"--catalog-root={root}"]
    for field, label in fields:
        value = getattr(args, field)
        if not value:
            value = prompt_value(
                label, sorted(generator.ALLOWED_CATEGORIES) if field == "category" else None,
            )
        argv.append(f"--{field}={value}")
    for field in ("license_file", "notice_file"):
        if getattr(args, field):
            argv.append(f"--{field.replace('_', '-')}={getattr(args, field)}")
    for field in ("with_openai", "with_references", "dry_run"):
        if getattr(args, field):
            argv.append(f"--{field.replace('_', '-')}")
    try:
        config = generator.config_from_args(generator.parse_args(argv))
        generator.create_scaffold(config, root / "templates" / "skill")
    except generator.ScaffoldError as exc:
        raise ContributionError(str(exc)) from exc
    if not args.dry_run:
        print(f"NEXT: after editing, run python scripts/contribute.py check {config.name}")
    return 0


def check_environment():
    missing_modules = [
        name for name in ("yaml", "skills_ref") if importlib.util.find_spec(name) is None
    ]
    missing_tools = [name for name in ("git", "node", "npx") if not shutil.which(name)]
    problems = []
    if missing_modules:
        problems.append(
            "Missing Python dependencies ({}). Run: {} -m pip install -r requirements-dev.txt".format(
                ", ".join(missing_modules), subprocess.list2cmdline([sys.executable]),
            )
        )
    if missing_tools:
        problems.append(
            f"Missing tools on PATH: {', '.join(missing_tools)}. Install Git and Node.js/npm "
            "(CI uses Node.js 22), then reopen the terminal. GitHub CLI (gh) is not needed."
        )
    if problems:
        raise ContributionError("\n".join(problems))
    return shutil.which("npx")


def run(command, root, *, capture=False, input_text=None):
    environment = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", NO_COLOR="1")
    return subprocess.run(
        command, cwd=root, env=environment, check=False,
        input=input_text, stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
    )


def require_success(result, label):
    if result.returncode:
        raise ContributionError(f"{label} failed (exit {result.returncode}); later checks were not run.")


def check_catalog(args, root):
    npx = check_environment()
    if args.name:
        catalog = local_module("skillhub")
        try:
            names = {
                spec["catalog_dir"]
                for component in catalog.load_components(root)
                for spec in component["skills"]
            }
        except catalog.CatalogError as exc:
            raise ContributionError(str(exc)) from exc
        if args.name not in names:
            raise ContributionError(f"Skill '{args.name}' is not registered in components.d.")
        print(f"Checking contribution '{args.name}'; all repository checks still apply.", flush=True)
    print(
        "This command regenerates README/catalog files, then validates the whole repository.\n"
        "Remote sources, if registered, are fetched for comparison only; mirrors are not updated.\n"
        "No branch, Git index, commit, push or pull request is created.", flush=True,
    )
    stages = (
        ("Generate catalog", ["scripts/generate_catalog.py"]),
        ("Unit tests", ["-m", "unittest", "discover", "-s", "tests"]),
        ("Catalog policy", ["scripts/validate_skills.py"]),
        ("Agent Skills specification", ["scripts/validate_agent_skills_spec.py"]),
        ("Generated catalog consistency", ["scripts/generate_catalog.py", "--check"]),
        ("Remote provenance", ["scripts/sync_sources.py", "--check"]),
    )
    for number, (label, arguments) in enumerate(stages, 1):
        print(f"[{number}/8] {label}", flush=True)
        require_success(run([sys.executable, *arguments], root), label)
    for number, extra in enumerate(([], ["--full-depth"]), 7):
        label = "CLI discovery" + (" (full-depth)" if extra else "")
        print(f"[{number}/8] {label}", flush=True)
        result = run([npx, "--yes", "skills@1.5.23", "add", ".", "--list", *extra], root, capture=True)
        if result.returncode:
            print(result.stdout or "", end="", flush=True)
        require_success(result, label)
        require_success(
            run([sys.executable, "scripts/validate_cli_discovery.py"], root, input_text=result.stdout),
            label + " output validation",
        )
    print(
        "PASS: all local checks passed. Review the generated diff and submit manually.\n"
        "This does not execute skill workflows or prove their behavior. "
        "PR Quality Gate, DCO and maintainer review are still required.\n"
        "Use git commit --signoff and open a pull request in the GitHub browser; gh is optional."
    )
    return 0


def main(argv=None, *, root=ROOT):
    args = parse_args(argv)
    if sys.version_info < (3, 11):
        print("ERROR: Python 3.11 or newer is required (CI tests 3.11 and 3.12).")
        return 1
    try:
        return new_skill(args, root) if args.command == "new" else check_catalog(args, root)
    except ImportError as exc:
        print(f"ERROR: missing Python dependency: {exc}. Install with python -m pip install -r requirements-dev.txt")
    except (ContributionError, OSError) as exc:
        print(f"ERROR: {exc}")
        print("HINT: see docs/publishing/quickstart.md. No changes were submitted; inspect git diff before retrying.")
    except KeyboardInterrupt:
        print("\nCancelled. No changes were submitted; inspect git diff before retrying.")
        return 130
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

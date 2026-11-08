#!/usr/bin/env python3
# Part of the Human-Approved Agent Playbook by DababonPro IT Solutions.
# Copyright (c) 2026 DababonPro IT Solutions. MIT licence; full text in the LICENSE file in this skill's folder.
"""Check a change against the repo's feature map.

Standard library only (Python 3.11+). Exit codes: 0 pass, 1 check failed, 2 the map or git could not be read.

Usage:
    python check_feature_map.py --base origin/main
    python check_feature_map.py --base origin/main --worktree --run
"""

import argparse
import fnmatch
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_MAP = "features.toml"
DEFAULT_TIMEOUT = 600
DEFAULT_SKIP_PATTERNS = [
    r"\.(skip|skipIf|only|todo)\b",
    r"\b(xit|xtest|xdescribe|fit|fdescribe)\s*\(",
    r"@(\w+\.)*(mark\.)?(skip\w*|xfail)\b",
    r"\bpytestmark\b",
    r"\bskipTest\s*\(",
    r"\bSkipTest\b",
    r"\bexpectedFailure\b",
    r"\bt\.Skip(f|Now)?\(",
    r"#\[ignore\b",
    r"@(Disabled|Ignore)\b",
    r"\[(Ignore|Fact\(Skip|Theory\(Skip)",
]


class MapError(Exception):
    pass


@dataclass
class Report:
    failures: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    touched: list = field(default_factory=list)
    proofs: list = field(default_factory=list)

    def fail(self, code, message):
        self.failures.append(f"{code}: {message}")


def git(*args, check=True):
    result = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and result.returncode != 0:
        raise MapError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def glob_to_regex(pattern):
    """Gitignore-style globs: ** crosses folders, * and ? stay inside one."""
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile(f"^{out}$")


def matches(path, patterns):
    return any(glob_to_regex(p).match(path) for p in patterns)


def load_map(text, source):
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise MapError(f"{source} is not valid TOML: {exc}") from exc
    features = data.get("feature", [])
    seen = set()
    for feature in features:
        fid = feature.get("id")
        if not fid or fid in seen:
            raise MapError(f"{source}: every feature needs a unique id, found {fid!r}")
        seen.add(fid)
        if not feature.get("code"):
            raise MapError(f"{source}: feature {fid} has no code paths")
        for key in ("must_stay_true", "code", "proof"):
            value = feature.get(key, [])
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise MapError(f"{source}: feature {fid}: {key} must be a list of strings")
    return data.get("settings", {}), features


def changed_files(base, worktree):
    """(status, path) pairs. Renames count as a delete of the old path and an add of the new one."""
    args = ["diff", "--name-status", "-M", "-z"]
    args += [base] if worktree else [f"{base}...HEAD"]
    rows = []
    fields = git(*args).stdout.split("\0")
    i = 0
    while i + 1 < len(fields):
        status = fields[i][0]
        if status == "R":
            rows += [("D", fields[i + 1]), ("A", fields[i + 2])]
            i += 3
        else:
            rows.append((status, fields[i + 1]))
            i += 2
    if worktree:
        rows += [("A", p) for p in ls_files("--others", "--exclude-standard")]
    return rows


def ls_files(*args):
    return [p for p in git("ls-files", "-z", *args).stdout.split("\0") if p]


def diff_lines(base, worktree, path, sign):
    args = ["diff", "-U0"]
    args += [base] if worktree else [f"{base}...HEAD"]
    lines, in_hunk = [], False
    for line in git(*args, "--", path, check=False).stdout.splitlines():
        if line.startswith("diff --git"):
            in_hunk = False
        elif line.startswith("@@"):
            in_hunk = True
        elif in_hunk and line.startswith(sign):
            lines.append(line[1:])
    return lines


def needs_person(report, approved, code, message):
    if approved:
        report.notes.append(f"Approved {code}: {message}")
    else:
        report.fail(code, f"{message} (needs human approval)")


def check_map_changes(base, map_path, settings, features, report, approved):
    """A weakened map is how a regression gets through, so any weakening needs a person."""
    old = git("show", f"{base}:{map_path}", check=False)
    if old.returncode != 0:
        if map_path in git("ls-tree", "-r", "--name-only", base).stdout.splitlines():
            raise MapError(f"could not read {map_path} from {base}: {old.stderr.strip()}")
        report.notes.append(f"No {map_path} on {base}, so this is treated as first adoption.")
        return []
    old_settings, old_features = load_map(old.stdout, f"{base}:{map_path}")
    current = {f["id"]: f for f in features}
    weakened = []
    defaults = {"mapped_paths": ["**"], "test_paths": [], "skip_patterns": DEFAULT_SKIP_PATTERNS}
    for key, default in defaults.items():
        for item in old_settings.get(key, default):
            if item not in settings.get(key, default):
                weakened.append(f"settings: {key} entry changed or removed: {item}")
    for item in settings.get("ignore", []):
        if item not in old_settings.get("ignore", []):
            weakened.append(f"settings: ignore entry added: {item}")
    old_by_id = {f["id"]: f for f in old_features}
    for feature in features:
        for item in feature.get("proof", []):
            if item not in old_by_id.get(feature["id"], {}).get("proof", []):
                weakened.append(f"{feature['id']}: proof entry added: {item}")
    for before in old_features:
        fid = before["id"]
        after = current.get(fid)
        if after is None:
            weakened.append(f"feature {fid} removed")
            continue
        for promise in before.get("must_stay_true", []):
            if promise not in after.get("must_stay_true", []):
                weakened.append(f"{fid}: promise changed or removed: {promise}")
        for key in ("code", "proof"):
            for item in before.get(key, []):
                if item not in after.get(key, []):
                    weakened.append(f"{fid}: {key} entry changed or removed: {item}")
    for item in weakened:
        needs_person(report, approved, "MAP-WEAKENED", item)
    return [f["id"] for f in features if f != old_by_id.get(f["id"])]


def run_proofs(touched, settings, report):
    timeout = int(settings.get("proof_timeout", DEFAULT_TIMEOUT))
    seen = set()
    for feature in touched:
        for command in feature.get("proof", []):
            if command in seen:
                continue
            seen.add(command)
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding="utf-8",
                                        errors="replace", timeout=timeout)
            except subprocess.TimeoutExpired:
                report.fail("PROOF-FAILED", f"{feature['id']}: timed out after {timeout}s: {command}")
                report.proofs.append(f"TIMEOUT  {command}")
                continue
            if result.returncode == 0:
                report.proofs.append(f"PASS  {command}")
                last = (result.stdout + result.stderr).strip().splitlines()[-1:]
                report.notes.append(f"Proof output, last line: {command}: {last[0] if last else '(no output)'}")
            else:
                tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-15:])
                report.fail("PROOF-FAILED", f"{feature['id']}: {command}\n{tail}")
                report.proofs.append(f"FAIL  {command}")


def check(base, map_path, worktree=False, run=False, promises_approved=False):
    report = Report()
    map_path = Path(map_path).as_posix()
    base = git("merge-base", base, "HEAD").stdout.strip()
    path = Path(map_path)
    if not path.exists():
        raise MapError(f"{map_path} not found")
    settings, features = load_map(path.read_text(encoding="utf-8"), map_path)
    mapped_paths = settings.get("mapped_paths", ["**"])
    ignore = list(settings.get("ignore", [])) + [map_path]
    test_paths = settings.get("test_paths", [])
    skip_patterns = settings.get("skip_patterns", DEFAULT_SKIP_PATTERNS)

    tracked = ls_files()
    if worktree:
        tracked += ls_files("--others", "--exclude-standard")
    for feature in features:
        for pattern in feature["code"]:
            if not any(matches(f, [pattern]) for f in tracked):
                report.fail("STALE-MAP", f"{feature['id']}: {pattern} matches no file")

    touched_ids = check_map_changes(base, map_path, settings, features, report, promises_approved)

    rows = changed_files(base, worktree)
    for status, file in rows:
        is_test = matches(file, test_paths)
        if is_test and status in ("D", "T"):
            needs_person(report, promises_approved, "TEST-REMOVED", f"{file} was deleted, moved or replaced")
        if is_test and status not in ("D", "T"):
            for line in diff_lines(base, worktree, file, "+"):
                if any(re.search(p, line) for p in skip_patterns):
                    needs_person(report, promises_approved, "TEST-WEAKENED", f"{file}: skip or focus marker added: {line.strip()}")
            # Removing a skip marker or a blank line strengthens a test or changes nothing, so it needs no person.
            removed = [ln for ln in diff_lines(base, worktree, file, "-")
                       if ln.strip() and not any(re.search(p, ln) for p in skip_patterns)]
            if status == "M" and removed:
                needs_person(report, promises_approved, "TEST-EDITED", f"{file}: existing test lines changed or removed")
        owners = [f for f in features if matches(file, f["code"])]
        if is_test and not owners and status != "D":
            owners = features
        for feature in owners:
            if feature["id"] not in touched_ids:
                touched_ids.append(feature["id"])
        needs_owner = matches(file, mapped_paths) and not matches(file, ignore) and not is_test
        if not owners and needs_owner and status != "D":
            report.fail("UNMAPPED", f"{file} belongs to no feature")

    touched = [f for f in features if f["id"] in touched_ids]
    report.touched = touched
    for feature in touched:
        if not feature.get("proof"):
            report.fail("NO-PROOF", f"{feature['id']} has no proof command")
        if not feature.get("must_stay_true"):
            report.fail("NO-PROMISE", f"{feature['id']} has no must_stay_true lines")

    if run:
        if any(f.startswith(("MAP-WEAKENED", "STALE-MAP", "TEST-EDITED")) for f in report.failures):
            report.notes.append("Proofs not run, because the map itself failed a check.")
        else:
            run_proofs(touched, settings, report)
    elif touched:
        report.notes.append("Proofs not run. Add --run to run them, and do not call this verified until they pass.")
    return report


def print_report(report):
    print(f"Features touched: {len(report.touched)}")
    for feature in report.touched:
        print(f"\n  {feature['id']} (owner: {feature.get('owner') or 'not set'})")
        for promise in feature.get("must_stay_true", []):
            print(f"    must stay true: {promise}")
    if report.proofs:
        print("\nProofs:")
        for line in report.proofs:
            print(f"  {line}")
    if report.notes:
        print("\nNotes:")
        for line in report.notes:
            print(f"  {line}")
    if report.failures:
        print(f"\nFAILED ({len(report.failures)}):")
        for line in report.failures:
            print(f"  {line}")
    else:
        print("\nPASSED")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", default="origin/main", help="the branch or commit to compare against")
    parser.add_argument("--map", default=DEFAULT_MAP, help="path to the feature map, relative to the repo root")
    parser.add_argument("--worktree", action="store_true", help="include uncommitted and untracked files")
    parser.add_argument("--run", action="store_true", help="run the proof commands of touched features")
    parser.add_argument("--promises-approved", action="store_true",
                        help="a person approved these weakenings. Set this only from CI, behind required code-owner review")
    args = parser.parse_args(argv)
    try:
        report = check(args.base, args.map, args.worktree, args.run, args.promises_approved)
    except MapError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print_report(report)
    return 1 if report.failures else 0


if __name__ == "__main__":
    sys.exit(main())

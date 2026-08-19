import json
import os
import sys
from collections import Counter, defaultdict
from urllib.parse import unquote, urlparse


def load_run(path):
    with open(path) as f:
        data = json.load(f)
    return data["runs"][0]


def build_rule_index(run):
    rules = run.get("tool", {}).get("driver", {}).get("rules", [])
    index = {}
    for rule in rules:
        description = rule.get("fullDescription", {}).get("text") or rule.get(
            "shortDescription", {}
        ).get("text", "")
        index[rule["id"]] = {
            "description": description.strip(),
            "helpUri": rule.get("helpUri", ""),
        }
    return index


def clean_path(uri):
    if uri.startswith("file://"):
        path = unquote(urlparse(uri).path)
        cwd = os.getcwd()
        if path.startswith(cwd + os.sep):
            return path[len(cwd) + 1 :]
        return path
    return uri


def result_location(result):
    locations = result.get("locations") or []
    if not locations:
        return "(no location)"
    loc = locations[0].get("physicalLocation", {})
    uri = clean_path(loc.get("artifactLocation", {}).get("uri", "?"))
    line = loc.get("region", {}).get("startLine", "?")
    return f"{uri}:{line}"


def main():
    if len(sys.argv) != 2:
        print("Usage: summarize_sarif.py <sarif-file>")
        sys.exit(1)

    sarif_file = sys.argv[1]
    try:
        run = load_run(sarif_file)
    except FileNotFoundError:
        print(f"{sarif_file} not found, skipping")
        return

    results = run.get("results", [])
    rule_index = build_rule_index(run)

    counts = Counter(r["ruleId"] for r in results)
    by_rule = defaultdict(list)
    for r in results:
        by_rule[r["ruleId"]].append(r)

    print(f"Total diagnostics: {len(results)}")
    print()
    print("--- Counts by rule ---")
    for rule_id, count in counts.most_common():
        print(f"{count:5d}  {rule_id}")

    for rule_id, count in counts.most_common():
        print()
        print(f"=== {rule_id} ({count} finding{'s' if count != 1 else ''}) ===")
        meta = rule_index.get(rule_id, {})
        if meta.get("description"):
            print(f"What it checks: {meta['description']}")
        if meta.get("helpUri"):
            print(f"Docs: {meta['helpUri']}")
        for r in by_rule[rule_id]:
            loc = result_location(r)
            message = r.get("message", {}).get("text", "").strip()
            print(f"  - {loc} — {message}")


if __name__ == "__main__":
    main()

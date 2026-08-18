import json
import sys
from collections import Counter

def load_results(paths):
    results = []
    for path in paths:
        try:
            with open(path) as f:
                data = json.load(f)
            for run in data.get("runs", []):
                results.extend(run.get("results", []))
        except FileNotFoundError:
            print(f"{path} not found, skipping")
    return results

def main():
    if len(sys.argv) < 3:
        print("Usage: summarize_sarif.py <sarif-file> <rule-id> [<rule-id> ...]")
        sys.exit(1)

    sarif_file = sys.argv[1]
    highlight_rules = sys.argv[2:]

    results = load_results([sarif_file])
    counts = Counter(r["ruleId"] for r in results)

    print(f"Total diagnostics: {len(results)}")
    print()
    print("--- Counts by rule ---")
    for rule_id, count in counts.most_common():
        print(f"{count:5d}  {rule_id}")

    for highlight_rule in highlight_rules:
        print()
        print(f"--- {highlight_rule} detail ---")
        matches = [r for r in results if r["ruleId"] == highlight_rule]
        if not matches:
            print("None found.")
        for r in matches:
            loc = r["locations"][0]["physicalLocation"]
            path = loc["artifactLocation"]["uri"]
            line = loc["region"]["startLine"]
            print(f"{path}:{line} - {r['message']['text']}")

if __name__ == "__main__":
    main()
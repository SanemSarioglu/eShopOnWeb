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
    sarif_files = sys.argv[1:-1]
    highlight_rule = sys.argv[-1]

    results = load_results(sarif_files)
    counts = Counter(r["ruleId"] for r in results)

    print(f"Total diagnostics: {len(results)}")
    print()
    print("--- Counts by rule ---")
    for rule_id, count in counts.most_common():
        print(f"{count:5d}  {rule_id}")

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
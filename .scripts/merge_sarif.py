import json
import sys


def main():
    if len(sys.argv) < 3:
        print("Usage: merge_sarif.py <output-file> <sarif-file> [<sarif-file> ...]")
        sys.exit(1)

    output_path = sys.argv[1]
    input_paths = sys.argv[2:]

    merged_rules = {}
    merged_results = []

    template = None
    for path in input_paths:
        try:
            with open(path) as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"{path} not found, skipping")
            continue

        run = data["runs"][0]
        if template is None:
            template = data

        for rule in run.get("tool", {}).get("driver", {}).get("rules", []):
            merged_rules[rule["id"]] = rule

        merged_results.extend(run.get("results", []))

    if template is None:
        print("No input SARIF files found, nothing to merge")
        sys.exit(1)

    merged = {
        "$schema": template.get("$schema"),
        "version": template.get("version", "2.1.0"),
        "runs": [
            {
                "tool": {
                    "driver": {
                        **template["runs"][0]["tool"]["driver"],
                        "rules": list(merged_rules.values()),
                    }
                },
                "results": merged_results,
            }
        ],
    }

    with open(output_path, "w") as f:
        json.dump(merged, f)

    print(f"Merged {len(input_paths)} file(s) into {output_path}: {len(merged_results)} total results")


if __name__ == "__main__":
    main()

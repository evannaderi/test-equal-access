import json
import sys
from collections import Counter

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def analyze_rule_differences(json1, json2):
    results1 = json1.get('results', [])
    results2 = json2.get('results', [])

    # Extract rule IDs
    rules1 = [result['ruleId'] for result in results1]
    rules2 = [result['ruleId'] for result in results2]

    # Count occurrences of each rule
    rule_count1 = Counter(rules1)
    rule_count2 = Counter(rules2)

    # Identify unique rules
    unique_rules1 = set(rules1) - set(rules2)
    unique_rules2 = set(rules2) - set(rules1)

    # Print analysis
    print(f"Total rules in JSON 1: {len(rules1)}")
    print(f"Total rules in JSON 2: {len(rules2)}")
    print(f"\nUnique rules in JSON 1: {len(unique_rules1)}")
    print(f"Unique rules in JSON 2: {len(unique_rules2)}")

    print("\nRules unique to JSON 1:")
    for rule in unique_rules1:
        print(f"  - {rule} (occurs {rule_count1[rule]} times)")

    print("\nRules unique to JSON 2:")
    for rule in unique_rules2:
        print(f"  - {rule} (occurs {rule_count2[rule]} times)")

    print("\nRules with different occurrence counts:")
    all_rules = set(rules1) | set(rules2)
    for rule in all_rules:
        count1 = rule_count1[rule]
        count2 = rule_count2[rule]
        if count1 != count2:
            print(f"  - {rule}: JSON 1 ({count1} times), JSON 2 ({count2} times)")

def main():
    # Read file paths from stdin
    file_paths = sys.stdin.read().splitlines()
    if len(file_paths) != 2:
        print("Please provide exactly two JSON file paths.")
        return

    json1 = load_json(file_paths[0])
    json2 = load_json(file_paths[1])

    analyze_rule_differences(json1, json2)

if __name__ == "__main__":
    main()


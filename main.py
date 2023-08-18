import sys

from backward_chaining import eval_query
from parse import parse_input


if __name__ == "__main__":
    input_filename = sys.argv[1]
    with open(input_filename, "r") as f:
        input_lines = f.readlines()

    rules, initial_facts, queries = parse_input(input_lines)
    print(queries)
    print("Current Knowledge Base:\n")
    print(rules)
    print("========================\n")

    print(eval_query(rules, initial_facts, queries))

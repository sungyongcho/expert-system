import sys

from backward_chaining import eval_query
from parse import KnowledgeBaseDAG, parse_input, parse_oneline


if __name__ == "__main__":
    input_filename = sys.argv[1]

    kb = KnowledgeBaseDAG()

    with open(input_filename, "r") as f:
        for input_line in f:
            queries = parse_oneline(kb, input_line)
            if queries is not None:
                print("Current Knowledge Base:\n")
                print(kb)
                print(eval_query(kb, kb.facts, queries))
        # input_lines = f.readlines()

    # rules, initial_facts, queries = parse_input(input_lines)
    # print(queries)
    # print(rules)
    # print("========================\n")

    # print(eval_query(rules, initial_facts, queries))

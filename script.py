from functools import partial
import sys
import re
from typing import Tuple, List, Dict

from collections import defaultdict


class KnowledgeBaseDAG:
    def __init__(self):
        self.graph = defaultdict(set)
        self.negated = defaultdict(bool)

    def add_rule(self, rule: str, result: str):
        rule_tokens = tokenize_expr(rule)
        self.graph[result].add(tuple(rule_tokens))

    def update_fact(self, fact: str, negated: bool = False):
        self.negated[fact] = negated

    def get_rules_for_fact(self, fact: str):
        return self.graph.get(fact, set())

    def is_fact_negated(self, fact: str):
        return self.negated.get(fact, False)

    def __str__(self):
        output = ""
        for key in self.graph:
            rules = ", ".join(str(rule) for rule in self.graph[key])
            output += f"{key} => {rules}\n"
        return output


def parse_input(input_lines: List[str]) -> Tuple[KnowledgeBaseDAG, str, str]:
    kb = KnowledgeBaseDAG()
    initial_facts, queries = "", ""
    mode = "rules"

    for line in input_lines:
        line = line.split("#")[0].strip()

        if not line:
            continue

        if line.startswith("="):
            initial_facts = line[1:].strip()
            mode = "facts"
        elif line.startswith("?"):
            queries = line[1:].strip()
            break
        elif mode == "rules":
            if "<=>" in line:
                left, right = line.split("<=>")
                kb.add_rule(left.strip(), right.strip())
                kb.add_rule(right.strip(), left.strip())
            else:
                key, value = line.split("=>")
                kb.add_rule(key.strip(), value.strip())

    return kb, initial_facts, queries


OP_AND = "+"
OP_OR = "|"
OP_XOR = "^"


def eval_expr(kb: KnowledgeBaseDAG, facts, tokens):
    if not tokens:
        return False

    token = tokens.pop(0).strip()

    if token == "!":
        return not eval_expr(kb, facts, tokens)
    elif token == "(":
        result = eval_expr(kb, facts, tokens)
        while tokens[0] != ")":
            t = tokens.pop(0).strip()
            if t == "+":
                result = result and eval_expr(kb, facts, tokens)
            elif t == "|":
                result = result or eval_expr(kb, facts, tokens)
            elif t == "^":
                result = result != eval_expr(kb, facts, tokens)
        del tokens[0]
        return result
    else:
        token_value = token in facts
        if kb.is_fact_negated(token):
            return not token_value
        else:
            return token_value


def evaluate_condition(kb: KnowledgeBaseDAG, facts: str, condition: str) -> str:
    tokens = tokenize_expr(condition)
    try:
        result = eval_expr(kb, facts, tokens)
        if not tokens:
            return "T" if result else "F"
        return "U"  # Undetermined - remaining tokens
    except:
        return "E"  # Error in evaluation


def tokenize_expr(expr):
    expr = expr.replace("!", "! ").replace("+", " + ").replace("|", " | ")
    expr = expr.replace("^", " ^ ").replace("(", " ( ").replace(")", " ) ")
    tokens = re.split(r'\s+', expr.strip())
    return tokens


def evaluate_rules(kb: KnowledgeBaseDAG, initial_facts: str, queries: str) -> str:
    # Update facts with the initial facts
    for fact in initial_facts:
        kb.update_fact(fact)

    results = []
    for query in queries:
        result = evaluate_condition(kb, initial_facts, query)
        results.append(result)

    return "".join(results)


if __name__ == "__main__":
    input_filename = sys.argv[1]
    with open(input_filename, "r") as f:
        input_lines = f.readlines()

    rules, initial_facts, queries = parse_input(input_lines)
    print("Current Knowledge Base:")
    print(rules)
    # print(rules, initial_facts, queries)
    print(queries)
    results = evaluate_rules(rules, initial_facts, queries)
    print("Results:", results)

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
        rpn_tokens = convert_to_rpn(rule_tokens)
        self.graph[result].add(tuple(rpn_tokens))

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
    stack = []
    for token in tokens:
        if token == '+':
            b = stack.pop()
            a = stack.pop()
            stack.append(a and b)
        else:
            stack.append(kb.is_fact_negated(token) or (token in facts))

    return stack[0]


def apply_rules(kb: KnowledgeBaseDAG, facts: str):
    new_facts = set(facts)
    changes = True

    while changes:
        changes = False
        for rule, products in kb.graph.items():
            if all(fact in new_facts for fact in rule):
                for product in products:
                    if product not in new_facts:
                        new_facts.add(product)
                        changes = True

    return new_facts


def evaluate_condition(kb: KnowledgeBaseDAG, facts: str, condition: str) -> str:
    facts = apply_rules(kb, facts)
    tokens = tokenize_expr(condition)
    rpn_tokens = convert_to_rpn(tokens)
    result = eval_expr(kb, facts, rpn_tokens)
    return "T" if result else "F"


def tokenize_expr(expr):
    expr = expr.replace("!", "! ").replace("+", " + ").replace("|", " | ")
    expr = expr.replace("^", " ^ ").replace("(", " ( ").replace(")", " ) ")
    tokens = re.split(r'\s+', expr.strip())
    return tokens


def convert_to_rpn(tokens):
    output = []
    stack = []

    for token in tokens:
        if token in (OP_AND, OP_OR, OP_XOR):
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            output.append(token)

    while stack:
        output.append(stack.pop())

    return output


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
    print("Current Knowledge Base:", rules)
    results = evaluate_rules(rules, initial_facts, queries)
    print("Results:", results)

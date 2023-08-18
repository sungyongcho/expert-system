from functools import partial
import re
from typing import Tuple, List, Dict

from collections import defaultdict


class KnowledgeBaseDAG:
    def __init__(self):
        self.graph = {}
        self.negated = defaultdict(bool)

    def add_rule(self, rule: str, result: str):
        rule_tokens = tokenize_expr(rule)
        result_tokens = tokenize_expr(result)
        rpn_expression = convert_to_rpn(rule_tokens)
        rpn_result = convert_to_rpn(result_tokens)
        # 키가 딕셔너리에 없으면 빈 set을 할당한 후 추가
        if tuple(result_tokens) not in self.graph:
            self.graph[tuple(rpn_result)] = tuple(rpn_expression)

    def update_fact(self, fact: str, negated: bool = False):
        self.negated[fact] = negated

    def get_rules_for_fact(self, fact: str):
        return self.graph.get(fact, set())

    def is_fact_negated(self, fact: str):
        return self.negated.get(fact, False)

    def __str__(self):
        output = ""
        for key in self.graph:
            output += f"{key} => {self.graph[key]}\n"
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
OP_NOT = "!"


def tokenize_expr(expr):
    expr = expr.replace("!", "! ").replace("+", " + ").replace("|", " | ")
    expr = expr.replace("^", " ^ ").replace("(", " ( ").replace(")", " ) ")
    tokens = re.split(r'\s+', expr.strip())
    return tokens


def convert_to_rpn(regex):
    """Converts a regular expression to Reverse Polish Notation (RPN)"""
    precedence = {'!': 3, '&': 2, '|': 1, '^': 1}
    rpn_tokens = []
    operator_stack = []

    idx = 0
    while idx < len(regex):
        token = regex[idx]
        if token.isupper():
            # Operand (single character)
            rpn_tokens.append(token)
        elif token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                rpn_tokens.append(operator_stack.pop())
            operator_stack.pop()  # Discard the left parenthesis
        else:
            while (operator_stack and
                   operator_stack[-1] != '(' and
                   precedence.get(operator_stack[-1], 0) >= precedence.get(token, 0)):
                rpn_tokens.append(operator_stack.pop())
            operator_stack.append(token)

        idx += 1

        if idx < len(regex) and regex[idx] == '!':
            operator_stack.append(regex[idx])
            idx += 1

    while operator_stack:
        # Pop any remaining operators from the stack to the output
        rpn_tokens.append(operator_stack.pop())

    return ''.join(rpn_tokens)

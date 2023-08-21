from functools import partial
import re
from typing import Tuple, List, Dict

from collections import defaultdict


class KnowledgeBaseDAG:
    def __init__(self):
        self.rules = {}
        self.facts = []
        self.reasoning = False
        self.interactive = False
        # self.negated = defaultdict(bool)

    def add_rule(self, rule: str, result: str):
        tokens_value = tokenize_expr(rule)
        tokens_key = tokenize_expr(result)
        rpn_value = convert_to_rpn(tokens_value)
        rpn_key = convert_to_rpn(tokens_key)
        # 키가 딕셔너리에 없으면 빈 set을 할당한 후 추가
        if tuple(rpn_key) in self.rules:
            self.rules[tuple(rpn_key)].append(tuple(rpn_value))
        else:
            self.rules[tuple(rpn_key)] = [tuple(rpn_value)]

    # def update_fact(self, fact: str, negated: bool = False):
    #     self.negated[fact] = negated

    def set_facts(self, facts: str):
        self.facts.clear()
        self.facts = list(facts)

    def add_facts(self, facts: str):
        for fact in facts.replace(" ", ""):
            if fact.isalpha() and fact not in self.facts:
                self.facts.append(fact)

    # def get_rules_for_fact(self, fact: str):
    #     return self.rules.get(fact, set())

    # def is_fact_negated(self, fact: str):
    #     return self.negated.get(fact, False)

    def __str__(self):
        output = ""
        for key in self.rules:
            output += f"{key}: {self.rules[key]}\n"
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


def parse_oneline(kb: KnowledgeBaseDAG, line: str) -> str:

    line = line.split("#")[0].strip()
    if not line:
        return

    if line.startswith("="):
        if len(line) > 1 and all(character.isupper() for character in line[1:]):
            facts = line[1:].strip()
            kb.set_facts(facts)
        elif len(line) == 1:
            return None
        else:
            return -100
    elif line.startswith("?") and all(character.isupper() for character in line[1:]):
        queries = line[1:].strip()
        print(queries)
        return queries
    elif "<=>" in line:
        if line.count("<=>") > 1:
            return -1
        left, right = line.split("<=>")
        if not left or not right:
            return -2
        elif not is_valid_string(left, ALLOWED_CHARS) or \
                not is_valid_string(right, ALLOWED_CHARS):
            return -3
        kb.add_rule(left.strip(), right.strip())
        kb.add_rule(right.strip(), left.strip())
    elif "=>" in line:
        if line.count("=>") > 1:
            return -4
        key, value = line.split("=>")
        if not key or not value:
            return -5
        elif not is_valid_string(key.strip(), ALLOWED_CHARS) or \
                not is_valid_string(value.strip(), ALLOWED_CHARS):
            print(key.strip(), value.strip())
            return -6
        elif not (is_parentheses_balanced(tokenize_expr(key.strip())) and is_parentheses_balanced(tokenize_expr(value.strip()))):
            return -7
        elif not is_valid_expression(tokenize_expr(key.strip())) or  \
                not is_valid_expression(tokenize_expr(value.strip())):
            return -8
        kb.add_rule(key.strip(), value.strip())
    else:
        return -9999

    return None


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
    negation_counter = 0

    idx = 0
    while idx < len(regex):
        token = regex[idx]

        if token == '!':
            negation_counter += 1
            idx += 1
            continue

        if token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                rpn_tokens.append(operator_stack.pop())
            operator_stack.pop()  # Discard the left parenthesis
        else:
            if token.isupper():
                # Operand (single character)
                rpn_tokens.append(token)
                if negation_counter % 2 != 0:
                    rpn_tokens.append('!')
                    negation_counter = 0
            else:
                while (operator_stack and
                        operator_stack[-1] != '(' and
                        precedence.get(operator_stack[-1], 0) >= precedence.get(token, 0)):
                    rpn_tokens.append(operator_stack.pop())
                operator_stack.append(token)

            negation_counter = 0

        idx += 1

    while operator_stack:
        # Pop any remaining operators from the stack to the output
        rpn_tokens.append(operator_stack.pop())

    return ''.join(rpn_tokens)


ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ+|^!() "


def is_valid_string(s, allowed_chars):
    return all(c in allowed_chars for c in s)


def is_parentheses_balanced(expression):
    stack = []
    opening_parentheses = "("
    closing_parentheses = ")"
    matching_parentheses = {")": "("}
    # Check if paerenthesis character exists
    if not (opening_parentheses in expression or closing_parentheses in expression):
        return True

    for char in expression:
        if char in opening_parentheses:
            stack.append(char)
        elif char in closing_parentheses:
            if not stack or stack.pop() != matching_parentheses[char]:
                return False

    return len(stack) == 0


def is_valid_expression(tokens):
    binary_operators = ['+', '|', '^']
    valid_operands = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    operand_count = 0
    operator_count = 0

    for token in tokens:
        if token == '!':
            continue  # Skip '!' (not operator)
        elif token in ['(', ')']:
            continue  # Skip parentheses
        elif token in binary_operators:
            operator_count += 1
        elif token in valid_operands:
            operand_count += 1
        else:
            return False  # Invalid token found

    # Check if the number of operators is one less than the number of operands
    return operand_count == operator_count + 1

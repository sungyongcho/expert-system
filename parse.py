from functools import partial
import re
import sys
from typing import Tuple, List, Dict

from collections import defaultdict


class KnowledgeBaseDAG:
    def __init__(self):
        self.rules = {}
        self.rev_rules = {}
        self.facts = []
        self.reasoning = False
        self.interactive = False
        self.query_given = False
        self.facts_given = False
        # self.negated = defaultdict(bool)

    def add_rule(self, rule: str, result: str):
        # tokens_value = tokenize_expr(rule)
        # tokens_key = tokenize_expr(result)
        rpn_value = convert_to_rpn(rule)
        rpn_key = convert_to_rpn(result)
        # 키가 딕셔너리에 없으면 빈 set을 할당한 후 추가
        if tuple(rpn_key) in self.rules:
            self.rules[tuple(rpn_key)].append(tuple(rpn_value))
        else:
            self.rules[tuple(rpn_key)] = [tuple(rpn_value)]

        if tuple(rpn_value) in self.rev_rules:
            self.rev_rules[tuple(rpn_value)].append(tuple(rpn_key))
        else:
            self.rev_rules[tuple(rpn_value)] = [tuple(rpn_key)]

    # def update_fact(self, fact: str, negated: bool = False):
    #     self.negated[fact] = negated

    def set_facts(self, facts: str):
        self.facts.clear()
        self.facts = list(facts)

    def add_facts(self, facts: str):
        for fact in facts.replace(" ", ""):
            if fact.isalpha() and fact not in self.facts:
                self.facts.append(fact)

    def get_key(self, element: tuple, dic: dict):
        for key, value in dic.items():
            if element in value:
                return key

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
        kb.facts_given = True
        if len(line) > 1 and all(character.isupper() for character in line[1:]):
            facts = line[1:].strip()
            kb.set_facts(facts)
        elif len(line) == 1:
            return None
        else:
            return -100
    elif line.startswith("?") and all(character.isupper() for character in line[1:]):
        kb.query_given = True
        queries = line[1:].strip()
        return queries
    elif "<=>" in line:
        result = check_valid_rule(line, "<=>")
        if isinstance(result, tuple) and len(result) == 2:
            left, right = result
            kb.add_rule(left, right)
            kb.add_rule(right, left)
        else:
            return result
    elif "=>" in line:
        result = check_valid_rule(line, "=>")
        if isinstance(result, tuple) and len(result) == 2:
            key, value = result
            kb.add_rule(key, value)
        else:
            return result
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


def distribute_negation(tokens):
    """Distributes the negation in a tokenized regular expression"""
    distributed_tokens = []
    distribute = False

    for i in range(len(tokens)):
        if tokens[i] == '!':
            if i+1 < len(tokens) and tokens[i+1] == '(':
                distribute = True
            else:
                distributed_tokens.append(tokens[i])
        elif tokens[i] == '(':
            distributed_tokens.append(tokens[i])
        elif tokens[i] == ')':
            if distribute:
                distribute = False
            distributed_tokens.append(tokens[i])
        # assuming operands are alphabets
        elif (tokens[i].isupper() or tokens[i].islower()) and distribute:
            distributed_tokens.extend(['!', tokens[i]])
        elif tokens[i] == '+' and distribute:
            distributed_tokens.append('|')
        elif tokens[i] == '|' and distribute:
            distributed_tokens.append('+')
        else:
            if not distribute:
                distributed_tokens.append(tokens[i])

    return distributed_tokens


def convert_to_rpn(regex):
    """Converts a regular expression to Reverse Polish Notation (RPN)"""
    print("===============", regex, file=sys.stderr)
    regex = distribute_negation(regex)
    print("222222222222222", regex, file=sys.stderr)
    precedence = {'!': 4, '+': 3, '|': 2, '^': 1}  # corrected precedences
    rpn_tokens = []
    operator_stack = []

    for token in regex:
        if token.isupper():  # Operand
            rpn_tokens.append(token)
        elif token == '!':
            operator_stack.append(token)
        elif token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack[-1] != '(':
                rpn_tokens.append(operator_stack.pop())
            operator_stack.pop()  # Discard left parenthesis from stack
        else:
            while (operator_stack and
                   operator_stack[-1] != '(' and
                   precedence[operator_stack[-1]] >= precedence[token]):
                rpn_tokens.append(operator_stack.pop())

            operator_stack.append(token)

    while operator_stack:  # Pop any remaining operators from stack into output
        rpn_tokens.append(operator_stack.pop())

    return ''.join(rpn_tokens)


def check_valid_rule(line, delim):
    if line.count(delim) > 1:
        return -1
    left, right = line.split(delim)
    if not left or not right:
        return -2
    left = tokenize_expr(left.strip())
    right = tokenize_expr(right.strip())
    print("aaa", left, right, file=sys.stderr)
    if not (is_valid_string(left, ALLOWED_CHARS) and is_valid_string(right, ALLOWED_CHARS)):
        return -3
    if not (has_valid_parenthesis(left) and has_valid_parenthesis(right)):
        return -4
    if not (is_parentheses_balanced(left) and is_parentheses_balanced(right)):
        return -5
    if not (is_valid_expression(left) and is_valid_expression(right)):
        return -6

    left_negation = left.copy()
    right_negation = right.copy()
    left_negation.insert(0, '!')
    right_negation.insert(0, '!')
    if left_negation == right:
        return -7
    if left == right_negation:
        return -8
    return left, right


ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ+|^!()"


def is_valid_string(s, allowed_chars):
    return all(c in allowed_chars for c in s)


def has_valid_parenthesis(expression):
    valid_operators = ['+', '|', '^']
    valid_operands = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    negation = '!'

    operands = 0
    operators = 0
    parenthesis = 0
    left_parenthesis = 0
    right_parenthesis = 0
    for i, token in enumerate(expression):
        if token == '(':
            left_parenthesis += 1
            if i > 0 and expression[i-1] in valid_operands:
                return False
        elif token == ')':
            right_parenthesis += 1
            # Check if next token is an operand without an operator in between.
            if i < len(expression) - 1 and (expression[i+1] in valid_operands or expression[i+1] == negation):
                return False
        elif token in valid_operators:
            operators += 1
        elif token == negation:
            # Check if next tokens form '()'.
            if expression[i+1:i+3] == ['(', ')']:
                return False
        elif token in valid_operands:
            operands += 1

    return left_parenthesis == right_parenthesis and operands - operators == 1


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


def is_expression(element: Tuple):
    binary_operators = ['+', '|', '^']

    for token in element:
        if token in binary_operators:
            return True
    return False


def is_negation(element: Tuple):
    if has_only_conjunctions(element):
        for token in element:
            if token == '!':
                return True
    return False


def has_only_conjunctions(element: Tuple):
    binary_operators = ['|', '^']
    for token in element:
        if token in binary_operators:
            return False
    return True


def get_operands(element: Tuple):
    valid_operands = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    operands_lst = []
    for token in element:
        if token in valid_operands or token == '!':
            operands_lst.append(token)
    return operands_lst

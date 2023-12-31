from parse import KnowledgeBaseDAG, is_expression, is_negation, has_only_conjunctions, get_operands
import sys

class TextColors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'

def print_colored_text(text, color_code):
    if color_code.upper() in dir(TextColors):
        color = getattr(TextColors, color_code.upper())
        print(f"{color}{text}{TextColors.RESET}", file=sys.stdout)
    else:
        print(text)

def print_rules(rules, color_code):
    for key, value in rules.items():
        print_colored_text(f'{key}:\t{value}', color_code)

def forward_chaining(kb: KnowledgeBaseDAG, visited=None):
    if visited is None:
        visited = set()
    results = {}
    for fact in kb.facts:
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print_colored_text(f'Evalating {fact}', 'YELLOW')
        value_lst = find_fact_in_values(kb.rules, fact)
        if value_lst == "ERROR":
            if kb.reasoning:
                if kb.interactive:
                    print("(expert-system) ", end='')
                print(f"Contradiction found in the rule {fact}.")
            return "Error"
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print_colored_text(f'Value list: {value_lst} for fact {fact}', 'magenta')
        eval_results = eval_expression(kb, value_lst)
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(f'Evaluation expression result: {eval_results}')
        for key, value in eval_results.items():
            if value == "ERROR":
                if kb.reasoning:
                    if kb.interactive:
                        print("(expert-system) ", end='')
                    print(f"Contradiction found in the rule {fact}.")
                return "Error"
    return results

def process_elements(kb: KnowledgeBaseDAG, rules, elements, visited):
    stack = []
    stack_elements = []
    if kb.reasoning:
        if kb.interactive:
            print("(expert-system) ", end='')
        print(f'elements in process_elements: {elements}')
    for index, element in enumerate(elements):
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print_colored_text(f'process element: {element}, visited: {visited}', 'blue')
        if element == '!':
            operand = stack.pop()
            element_operand = stack_elements.pop()
            if kb.reasoning:
                if kb.interactive:
                    print("(expert-system) ", end='')
                print(
                    f"Applying negation (!) to '{element_operand} ({operand})'")
            negation_result = not eval_expr(kb, rules, element_operand, visited)
            stack.append(negation_result)
            stack_elements.append(element_operand)
        elif element in ('+', '|', '^'):
            right = stack.pop()
            left = stack.pop()
            right_chars = stack_elements.pop()
            left_chars = stack_elements.pop()
            if element == '+':
                result = left and right
                operation = 'AND'
            elif element == '|':
                result = left or right
                operation = 'OR'
            elif element == '^':
                result = left ^ right
                operation = 'XOR'
            if kb.reasoning:
                if kb.interactive:
                    print("(expert-system) ", end='')
                print(
                    f"Applying {operation} ({element}) to '{left_chars} ({left})' and '{right_chars} ({right})'")
            stack.append(result)
            stack_elements.append((left_chars, right_chars, element))
        else:
            eval_result = eval_expr(kb, rules, element, visited)
            if kb.reasoning:
                if kb.interactive:
                    print("(expert-system) ", end='')
                print(f'Result for element:{element}', eval_result)
            if (eval_result == True and not element in kb.facts):
                if kb.reasoning:
                    if kb.interactive:
                        print("(expert-system) ", end='')
                    print_colored_text(f'{element} is added as fact', 'yellow')
                kb.add_facts(element)
            stack.append(eval_result)
            stack_elements.append(element)
    eval_result = stack.pop()
    eval_element = stack_elements.pop()
    if kb.reasoning:
        if kb.interactive:
            print("(expert-system) ", end='')
        print(f'Evaluation result: {eval_result}, element: {eval_element}')
    key = kb.rev_rules[elements][0]
    if kb.reasoning:
        if kb.interactive:
            print("(expert-system) ", end='')
        print_colored_text(f'{key} is {eval_result} after evaluating expresion: {elements}', 'red')
    return check_eval_result(kb, key, eval_result)

def check_eval_result(kb, key, eval_result):
    if eval_result == True and key[0] not in kb.facts:
        if not is_expression(key):
            if is_negation(key):
                for i, elem in enumerate(key):
                    if i + 1 < len(key) and key[i + 1] != '!':
                        kb.add_facts(elem)
            else:
                kb.add_facts(key[0])
        elif is_expression(key):
            if has_only_conjunctions(key):
                operands_lst = get_operands(key)
                #print_colored_text(operands_lst, 'yellow')
                for i, operand in enumerate(operands_lst):
                    #print(f'curr operand: {operand}', file=sys.stderr)
                    if i + 1 < len(operands_lst) and operands_lst[i + 1] == '!':
                        pass
                    else:
                        kb.add_facts(operand)
    elif eval_result == False and is_negation(key):
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print_colored_text(f'negation in key: {key} {len(key)} when result is {eval_result}', 'red')
        for i, elem in enumerate(key):
            if i + 1 < len(key) and key[i + 1] == '!':
                kb.add_facts(elem)
    elif eval_result == False and not is_negation(key):
        pass
    elif eval_result == True and key[0] in kb.facts:
        if not is_expression(key):
            #print(kb.facts, file=sys.stderr)
            for i, elem in enumerate(key):
                if i + 1 < len(key) and key[i + 1] == '!':
                    return "ERROR"
        elif is_expression(key):
            if has_only_conjunctions(key):
                operands_lst = get_operands(key)
                #print_colored_text(operands_lst, 'yellow')
                for i, operand in enumerate(operands_lst):
                    #print(f'curr operand: {operand}', file=sys.stderr)
                    if i + 1 < len(operands_lst) and operands_lst[i + 1] == '!':
                        return "ERROR"
    else:
        return "ERROR"
    return eval_result


def find_fact_in_values(rules, fact):
    value_lst = []
    for key_tuple, value_list in rules.items():
        if fact in key_tuple:
            if key_tuple + ('!',) in rules.keys():
                return "ERROR"
        for value_tuple in value_list:
            if fact in value_tuple:
                value_lst.append(value_tuple)
    return value_lst

def find_query_in_keys(rules, query):
    for key_tuple, _ in rules.items():
        if query in key_tuple:
            if key_tuple + ('!',) in rules.keys():
                return "ERROR"
            return key_tuple
    return None

def eval_expr(kb: KnowledgeBaseDAG, rules, query, visited=None):
    if visited is None:
        visited = set()

    if query in kb.facts:
        if kb.reasoning is True:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(f"Symbol {query} is in facts list, so it is true")
        return True

    if kb.reasoning:
        if kb.interactive:
            print("(expert-system) ", end='')
        print(f"Finding {query} in rules...")
    key_tuple = find_query_in_keys(rules, query)

    if key_tuple == 'ERROR':
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(f"Contradiction found in the rule {query}.")
        return 'ERROR'

    if key_tuple in visited:
        return False
    return eval_key(kb, rules, key_tuple, visited)

def eval_key(kb, rules, key_tuple, visited): 
    if key_tuple:
        elements = rules[key_tuple]
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print_colored_text(f'elements in eval expr: {elements}, for key {key_tuple}', 'green')
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
        for element in elements:
            if kb.reasoning:
                if kb.interactive:
                    print("(expert-system) ", end='')
                print_colored_text(f'curr element in eval expr: {element}', 'green')
            visited_copy = visited.copy()
            visited_copy.add(key_tuple)

            process_elements_result = process_elements(kb, rules, element, visited_copy)
            if process_elements_result == True:
                key = kb.get_key(element, rules)
                if (len(key) >= 2 and key[1] == '!'):
                    return False
                return True
            elif process_elements_result == False:
                key = kb.get_key(element, rules)
                if not is_expression(key):
                    if key[0] in kb.facts:
                        if kb.reasoning:
                            if kb.interactive:
                                print("(expert-system) ", end='')
                            print_colored_text(f'{key} is added as A fact', 'yellow')
                        kb.add_facts(key[0])
                        return True
            elif process_elements_result == "ERROR":
                return "ERROR"
                
    visited.add(key_tuple)

    return False

def eval_expression(kb: KnowledgeBaseDAG, queries):
    results = {}
    for query in queries:
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(f"Evaluating fact {query}")
        query_result = process_elements(kb, kb.rules, query, None)
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(
                f"Result of fact {query} is {'True' if query_result else 'False'} ")
        results[query] = query_result
    return results


def eval_query(kb: KnowledgeBaseDAG, queries):
    if kb.reasoning is True:
        if kb.interactive:
            print("(expert-system) ", end='')
        print(f"Evaluating queries {list(queries)}")

    results = {}
    for query in queries:
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(f"Evaluating query {query}")
        query_result = eval_expr(kb, kb.rules, query)
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(
                f"Result of query {query} is {'True' if query_result else 'False'} ")
        results[query] = query_result
    return results

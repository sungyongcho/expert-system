from parse import KnowledgeBaseDAG, is_expression, has_only_conjunctions, get_operands
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
        print(f"{color}{text}{TextColors.RESET}", file=sys.stderr)
    else:
        print(text)

def print_rules(rules, color_code):
    for key, value in rules.items():
        print_colored_text(f'{key}:\t{value}', color_code)

def forward_chaining(kb: KnowledgeBaseDAG, visited=None):
    #print_colored_text(f'\nkb.rev_rules: {kb.rev_rules}', 'YELLOW')
    #print_colored_text(f'\nkb.rules: {kb.rules}', 'magenta')
    print_rules(kb.rev_rules, 'yellow')
    print_rules(kb.rules, 'magenta')
    if visited is None:
        visited = set()
    for fact in kb.facts:
        print('curr fact:', fact, file=sys.stderr)
        print_colored_text(f'eval for rules with fact {fact}', 'YELLOW')
        #key_lst = find_query_in_keys2(kb.rules, fact)
        #print(f'key_lst: {key_lst}')
        #eval_key2(kb, kb.rules, key_lst, visited)
        value_lst = find_fact_in_values(kb.rules, fact)
        print_colored_text(f'value_lst: {value_lst} for fact {fact}', 'magenta')
        eval_expression(kb, value_lst)

        #print_colored_text(f'eval for REV rules with fact {fact}', 'YELLOW')
        ##key_lst = find_query_in_keys2(kb.rev_rules, fact)
        #value_lst = find_fact_in_values(kb.rev_rules, fact)
        #print(f'value_lst: {value_lst}')
        #eval_key2(kb, kb.rev_rules, value_lst, visited)

        #key_tuple = find_query_in_keys(kb.rev_rules, fact)
        #eval_key(kb, kb.rev_rules, key_tuple, visited)

def process_elements(kb: KnowledgeBaseDAG, rules, elements, visited):
    stack = []
    stack_elements = []
    print(f'elements in process_elements: {elements}', file=sys.stderr)
    for index, element in enumerate(elements):
        print_colored_text(f'process element: {element}, visited: {visited}', 'blue')
        #print('process element:', element, 'visited:', visited)
        if element == '!':
            operand = stack.pop()
            element_operand = stack_elements.pop()
            if kb.reasoning:
                if kb.interactive:
                    print("(expert-system) ", end='')
                print(
                    f"Applying negation (!) to '{element_operand} ({operand})'")
            negation_result = not eval_expr(kb, rules, element_operand, visited)
            print("negation_result:", negation_result, file=sys.stderr)
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
            #stack.append(eval_expr(kb, element, visited))
            eval_result = eval_expr(kb, rules, element, visited)
            print(f'result for element:{element}', eval_result, file=sys.stderr)
            if (eval_result == True and not element in kb.facts):
                print_colored_text(f'{element} is added as fact', 'yellow')
                kb.add_facts(element)
            stack.append(eval_result)
            stack_elements.append(element)
    eval_result = stack.pop()
    eval_element = stack_elements.pop()
    print(f'op result: {eval_result}, element: {eval_element}', file=sys.stderr)
    key = kb.rev_rules[elements][0]
    print_colored_text(f'key: {key} is {eval_result} after evaluating expresion: {elements}', 'red')
    if eval_result == True and key[0] not in kb.facts:
        if not is_expression(key):
            print_colored_text(f'adding key {key} as a fact after evaluating', 'yellow')
            print(kb.facts, file=sys.stderr)
            kb.add_facts(key[0])
        elif is_expression(key):
            if has_only_conjunctions(key):
                operands_lst = get_operands(key)
                print_colored_text(operands_lst, 'yellow')
                for operand in operands_lst:
                    kb.add_facts(operand)
                print(kb.facts, file=sys.stderr)
            # else:
            #     eval_expression(kb, key)
    return eval_result
    #return stack.pop()

def find_fact_in_values(rules, fact):
    value_lst = []
    for key_tuple, value_list in rules.items():
        #print(f'curr value_tuple {value_list} for finding fact {fact}')
        for value_tuple in value_list:
            if fact in value_tuple:
                #print('fact in values:', fact)
                value_lst.append(value_tuple)
    return value_lst

def find_query_in_keys2(rules, query):
    key_lst = []
    for key_tuple, _ in rules.items():
        if query in key_tuple:
            print('query in keys:', query, file=sys.stderr)
            key_lst.append(key_tuple)
            if key_tuple + ('!',) in rules.keys():
                return "ERROR"
            if '|' in key_tuple:
                print("or in conclusion", key_tuple, file=sys.stderr)
            if '^' in key_tuple:
                print("xor in conclusion", key_tuple, file=sys.stderr)
    return key_lst

def find_query_in_keys(rules, query):
    for key_tuple, _ in rules.items():
        if query in key_tuple:
            print('query in keys:', query, file=sys.stderr)
            if key_tuple + ('!',) in rules.keys():
                return "ERROR"
            if '|' in key_tuple:
                print("or in conclusion", key_tuple, file=sys.stderr)
            if '^' in key_tuple:
                print("xor in conclusion", key_tuple, file=sys.stderr)
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
        print(f'{query} is a fact', file=sys.stderr)
        return True

    # if query in rules:
    #     elements = rules[query]
    #     return process_elements(elements, rules, facts)
    if kb.reasoning:
        if kb.interactive:
            print("(expert-system) ", end='')
        print(f"Finding {query} in rules...")
    key_tuple = find_query_in_keys(rules, query)
    #print('key_tuple:', key_tuple, ', query:', query)

    if key_tuple == 'ERROR':
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(f"Contradiction found in the rule {query}.")
        return 'ERROR'

    if key_tuple in visited:
        return False
    return eval_key(kb, rules, key_tuple, visited)
    #return False

def eval_key2(kb, rules, key_lst, visited): 
    for key_tuple in key_lst:
        if key_tuple:
            elements = rules[key_tuple]
            print_colored_text(f'\nkeys in eval expr: {key_tuple}', 'green')
            if kb.reasoning:
                if kb.interactive:
                    print("(expert-system) ", end='')
                # print(f"For query {query}, rule {elements} is found.")
            for element in key_tuple:
                print_colored_text(f'curr element in eval expr: {element}', 'green')
                #print(f'curr element in eval expr: {element}')
                visited_copy = visited.copy()
                visited_copy.add(key_tuple)

                if process_elements(kb, rules, element, visited_copy) == True:
                    print_colored_text(f'element when expr is true: {element}', 'red')
                    print_colored_text(f'visited when expr is true: {visited_copy}', 'red')
                    key = kb.get_key(element, rules)
                    print_colored_text(f'key for element when expr is true: {key}', 'red')
                    if is_expression(key):
                        print(f'key is expr', file=sys.stderr)
                        #eval_expr(kb, query, element)
                        #eval_key(kb, key, visited)
                    else:
                        if key[0] not in kb.facts:
                            print_colored_text(f'{key} is added as A fact', 'yellow')
                            kb.add_facts(key[0])

                    if (len(key_tuple) == 2 and key_tuple[1] == '!'):
                        return False
                    return True
                else:
                    key = kb.get_key(element, rules)
                    print(f'expr is false: {element} for key {key}', file=sys.stderr)
                    if is_expression(key):
                        print(f'key is expr', file=sys.stderr)
                    else:
                        if key[0] in kb.facts:
                            print(f'{key} is added as A fact Re')
                            kb.add_facts(key[0])
                    
        visited.add(key_tuple)

    return False

def eval_key_lst(kb, rules, key_lst, visited): 
    for key_tuple in key_lst:
        if key_tuple:
            elements = rules[key_tuple]
            print_colored_text(f'\nelements in eval expr: {elements}, for key {key_tuple}', 'green')
            #print(f'\nelements in eval expr: {elements}, for key {key_tuple}')
            if kb.reasoning:
                if kb.interactive:
                    print("(expert-system) ", end='')
                # print(f"For query {query}, rule {elements} is found.")
            for element in elements:
                print_colored_text(f'curr element in eval expr: {element}', 'green')
                #print(f'curr element in eval expr: {element}')
                visited_copy = visited.copy()
                visited_copy.add(key_tuple)

                if process_elements(kb, rules, element, visited_copy) == True:
                    print_colored_text(f'element when expr is true: {element}', 'red')
                    print_colored_text(f'visited when expr is true: {visited_copy}', 'red')
                    key = kb.get_key(element, rules)
                    print_colored_text(f'key for element when expr is true: {key}', 'red')
                    if is_expression(key):
                        print(f'key is expr', file=sys.stderr)
                        #eval_expr(kb, query, element)
                        #eval_key(kb, key, visited)
                    else:
                        print(f'{key} is added as A fact')
                        kb.add_facts(key[0])

                    if (len(key_tuple) == 2 and key_tuple[1] == '!'):
                        return False
                    return True
                else:
                    key = kb.get_key(element, rules)
                    print(f'expr is false: {element} for key {key}', file=sys.stderr)
                    if is_expression(key):
                        print(f'key is expr', file=sys.stderr)
                    else:
                        if key[0] in kb.facts:
                            print(f'{key} is added as A fact Re')
                            kb.add_facts(key[0])
                    
        visited.add(key_tuple)

    return False

def eval_key(kb, rules, key_tuple, visited): 
    if key_tuple:
        elements = rules[key_tuple]
        print_colored_text(f'\nelements in eval expr: {elements}, for key {key_tuple}', 'green')
        #print(f'\nelements in eval expr: {elements}, for key {key_tuple}')
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            # print(f"For query {query}, rule {elements} is found.")
        for element in elements:
            print_colored_text(f'curr element in eval expr: {element}', 'green')
            #print(f'curr element in eval expr: {element}')
            visited_copy = visited.copy()
            visited_copy.add(key_tuple)

            if process_elements(kb, rules, element, visited_copy) == True:
                print_colored_text(f'element when expr is true: {element}', 'red')
                print_colored_text(f'visited when expr is true: {visited_copy}', 'red')
                key = kb.get_key(element, rules)
                print_colored_text(f'key for element when expr is true: {key}', 'red')
                if is_expression(key):
                    print(f'key is expr', file=sys.stderr)
                    #eval_expr(kb, query, element)
                    #eval_key(kb, key, visited)
                else:
                    if key[0] not in kb.facts:
                            print_colored_text(f'{key} is added as A fact', 'yellow')
                            kb.add_facts(key[0])

                if (len(key_tuple) == 2 and key_tuple[1] == '!'):
                    return False
                return True
            else:
                key = kb.get_key(element, rules)
                print(f'expr is false: {element} for key {key}', file=sys.stderr)
                if is_expression(key):
                    print(f'key is expr', file=sys.stderr)
                else:
                    if key[0] in kb.facts:
                        print_colored_text(f'{key} is added as A fact Re', 'yellow')
                        kb.add_facts(key[0])
                
    visited.add(key_tuple)

    return False


# def tokenize_query(query):
#     return [char for char in query if char.isalnum()]

def eval_expression(kb: KnowledgeBaseDAG, queries):
    print('eval expression:', queries, file=sys.stderr)
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
        print('curr expression:', query, file=sys.stderr)
        #query_result = eval_expr(kb, kb.rules, query)
        query_result = process_elements(kb, kb.rules, query, None)
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(
                f"Result of query {query} is {'True' if query_result else 'False'} ")
        results[query] = query_result
    return results


def eval_query(kb: KnowledgeBaseDAG, queries):
    print('queries:', queries, file=sys.stderr)
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
        print('curr query:', query, file=sys.stderr)
        query_result = eval_expr(kb, kb.rules, query)
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(
                f"Result of query {query} is {'True' if query_result else 'False'} ")
        results[query] = query_result
    return results


# print(eval_query(rule, facts, "A"))

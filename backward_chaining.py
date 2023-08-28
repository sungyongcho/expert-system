

# rule = {'C': ['A', 'B', '+']}

# facts = {'A', 'B'}

# rule = {('B', 'C', '+'): ['A']}

# facts = {'A', 'B'}

# rule = {'A': ['B'],
#         'B': ['E', 'D', '+'],
#         'F': ['G', 'H', '+'],
#         'G': ['I', 'J', '+'],
#         'H': ['G'],
#         'K': ['L', 'M', '+'],
#         ('L', 'N', '+'): ['O', 'P', '+'],
#         'M': ['N'],
#         }

# facts = {'D', 'E', 'I', 'J', 'P'}
# # facts = {'D', 'E', 'I', 'J', 'O', 'P'}


# rule = {'A': ['B'],
#         'B': ['A']}

# # facts = {'B'}
# facts = {'A'}


# rule = {'A': ['B', 'C', '!', '+']}

# # facts = {}
# # facts = {'B'}
# # facts = {'C'}
# facts = {'B', 'C'}


# rule = {'A': ['B', 'C', '+'],
#         'B': ['D', 'E', '|'],
#         'C': ['B'],
#         }

# # facts = {}
# # facts = {'D'}
# # facts = {'E'}
# facts = {'D', 'E'}


# rule = {'A': ['B', 'C', '+'],
#         'B': ['D', 'E', '^'],
#         'C': ['B']
#         }

# facts = {}
# facts = {'D'}
# facts = {'E'}
# facts = {'D', 'E'}


from parse import KnowledgeBaseDAG, is_expression

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
        print(f"{color}{text}{TextColors.RESET}")
    else:
        print(text)


def eval_rules_with_facts(kb: KnowledgeBaseDAG, visited=None):
    print_colored_text(f'kb.rev_rules: {kb.rev_rules}', 'YELLOW')
    if visited is None:
        visited = set()
    for fact in kb.facts:
        print('curr fact:', fact)
        print_colored_text(f'eval for rules with fact {fact}', 'YELLOW')
        key_tuple = find_query_in_keys(kb.rules, fact)
        eval_key(kb, kb.rules, key_tuple, visited)

        print_colored_text(f'eval for REV rules with fact {fact}', 'YELLOW')
        key_tuple = find_query_in_keys(kb.rev_rules, fact)
        eval_key(kb, kb.rev_rules, key_tuple, visited)

def process_elements(kb: KnowledgeBaseDAG, rules, elements, visited):
    stack = []
    stack_elements = []
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
            print("negation_result:", negation_result)
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
            print(f'result for element:{element}', eval_result)
            if (eval_result == True):
                print(f'{element} is added as fact')
                kb.add_facts(element)
            stack.append(eval_result)
            stack_elements.append(element)
    eval_result = stack.pop()
    eval_element = stack_elements.pop()
    print(f'op result: {eval_result}, element: {eval_element}')
    return eval_result
    #return stack.pop()


def find_query_in_keys(rules, query):
    for key_tuple, _ in rules.items():
        if query in key_tuple:
            print('query in keys:', query)
            if key_tuple + ('!',) in rules.keys():
                return "ERROR"
            if '|' in key_tuple:
                print("or in conclusion", key_tuple)
            if '^' in key_tuple:
                print("xor in conclusion", key_tuple)
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

def eval_key(kb, rules, key_tuple, visited): 
    if key_tuple:
        elements = rules[key_tuple]
        print_colored_text(f'\nelements in eval expr: {elements}, for key {key_tuple}', 'green')
        #print(f'\nelements in eval expr: {elements}, for key {key_tuple}')
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(f"For query {query}, rule {elements} is found.")
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
                    print(f'key is expr')
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
                print(f'expr is false: {element} for key {key}')
                if is_expression(key):
                    print(f'key is expr')
                else:
                    if key[0] in kb.facts:
                        print(f'{key} is added as A fact Re')
                        kb.add_facts(key[0])
                
    visited.add(key_tuple)

    return False


# def tokenize_query(query):
#     return [char for char in query if char.isalnum()]


def eval_query(kb: KnowledgeBaseDAG, queries):
    print('queries:', queries)
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
        print('curr query:', query)
        query_result = eval_expr(kb, kb.rules, query)
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(
                f"Result of query {query} is {'True' if query_result else 'False'} ")
        results[query] = query_result
    return results


# print(eval_query(rule, facts, "A"))

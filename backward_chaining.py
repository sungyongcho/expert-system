

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


from parse import KnowledgeBaseDAG


def process_elements(kb: KnowledgeBaseDAG, elements, visited):
    stack = []
    stack_elements = []
    for index, element in enumerate(elements):
        if element == '!':
            operand = stack.pop()
            element_operand = stack_elements.pop()
            if kb.reasoning:
                if kb.interactive:
                    print("(expert-system) ", end='')
                print(
                    f"Applying negation (!) to '{element_operand} ({operand})'")
            negation_result = not eval_expr(kb, element_operand, visited)
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
            stack.append(eval_expr(kb, element, visited))
            stack_elements.append(element)
    return stack.pop()


def find_query_in_keys(rules, query):
    for key_tuple, _ in rules.items():
        if query in key_tuple:
            if key_tuple + ('!',) in rules.keys():
                return "ERROR"
            return key_tuple
    return None


def eval_expr(kb: KnowledgeBaseDAG, query, visited=None):
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
    key_tuple = find_query_in_keys(kb.rules, query)

    if key_tuple == 'ERROR':
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(f"Contradiction found in the rule {query}.")
        return 'ERROR'

    if key_tuple in visited:
        return False

    if key_tuple:
        elements = kb.rules[key_tuple]
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(f"For query {query}, rule {elements} is found.")
        for element in elements:
            visited_copy = visited.copy()
            visited_copy.add(key_tuple)

            if process_elements(kb, element, visited_copy) == True:
                if (len(key_tuple) == 2 and key_tuple[1] == '!'):
                    return False
                return True
    visited.add(key_tuple)

    return False


# def tokenize_query(query):
#     return [char for char in query if char.isalnum()]


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
        query_result = eval_expr(kb, query)
        if kb.reasoning:
            if kb.interactive:
                print("(expert-system) ", end='')
            print(
                f"Result of query {query} is {'True' if query_result else 'False'} ")
        results[query] = query_result
    return results


# print(eval_query(rule, facts, "A"))

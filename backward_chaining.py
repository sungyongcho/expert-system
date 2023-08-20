

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
    for index, element in enumerate(elements):
        if element == '!':
            # remove currently stored value in stack first,
            stack.pop()
            # and then run eval_expr again
            next_element = elements[index - 1]
            negation_result = not eval_expr(
                kb, next_element, visited)
            stack.append(negation_result)
        elif element == '+':
            right = stack.pop()
            left = stack.pop()
            result = left and right
            stack.append(result)
        elif element == '|':
            right = stack.pop()
            left = stack.pop()
            result = left or right
            stack.append(result)
        elif element == '^':  # Handling XOR operation
            right = stack.pop()
            left = stack.pop()
            result = left ^ right
            stack.append(result)
        else:
            stack.append(eval_expr(kb, element, visited))
    return stack.pop()


def find_query_in_keys(rules, query):
    for key_tuple, _ in rules.items():
        if query in key_tuple:
            return key_tuple
    return None


def eval_expr(kb: KnowledgeBaseDAG, query, visited=None):
    if visited is None:
        visited = set()

    if query in kb.facts:
        return True

    # if query in rules:
    #     elements = rules[query]
    #     return process_elements(elements, rules, facts)

    key_tuple = find_query_in_keys(kb.rules, query)

    if key_tuple in visited:
        return False

    if key_tuple:
        elements = kb.rules[key_tuple]
        for element in elements:
            visited_copy = visited.copy()
            visited_copy.add(key_tuple)

            if process_elements(kb, element, visited_copy) == True:
                return True
    visited.add(key_tuple)

    return False


# def tokenize_query(query):
#     return [char for char in query if char.isalnum()]


def eval_query(kb: KnowledgeBaseDAG, queries):
    results = {}
    for query in queries:
        results[query] = eval_expr(kb, query)
    return results


# print(eval_query(rule, facts, "A"))



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


def process_elements(elements, rules, facts, visited):
    stack = []
    for index, element in enumerate(elements):
        if element == '!':
            # remove currently stored value in stack first,
            stack.pop()
            # and then run eval_expr again
            next_element = elements[index - 1]
            negation_result = not eval_expr(
                rules, facts, next_element, visited)
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
            stack.append(eval_expr(rules, facts, element, visited))
    return stack.pop()


def find_query_in_keys(rules, query):
    for key_tuple, _ in rules.graph.items():
        if query in key_tuple:
            return key_tuple
    return None


def eval_expr(rules, facts, query, visited=None):
    if visited is None:
        visited = set()

    if query in facts:
        return True

    if query in visited:
        return False

    # if query in rules:
    #     elements = rules[query]
    #     return process_elements(elements, rules, facts)

    key_tuple = find_query_in_keys(rules, query)

    if key_tuple:
        elements = rules.graph[key_tuple]
        for element in elements:
            # print(element)
            if process_elements(element, rules, facts, visited) == True:
                return True

    visited.add(query)

    return False


# def tokenize_query(query):
#     return [char for char in query if char.isalnum()]


def eval_query(rules, facts, queries):
    results = {}
    for query in queries:
        results[query] = eval_expr(rules, facts, query)
    return results


# print(eval_query(rule, facts, "A"))

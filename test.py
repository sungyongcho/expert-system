

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


rule = {'A': ['B'],
        'B': ['A']}

# facts = {'B'}
facts = {'A'}


def process_elements(elements, rules, facts):
    stack = []
    for element in elements:
        if element == '+':
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
            stack.append(eval_expr(rules, facts, element))
    return stack.pop()


def find_query_in_keys(rules, query):
    for key_tuple in rules.keys():
        if query in key_tuple:
            return key_tuple
    return None


def eval_expr(rules, facts, query):
    if query in facts:
        return True

    if query in rules:
        elements = rules[query]
        return process_elements(elements, rules, facts)

    key_tuple = find_query_in_keys(rules, query)

    if key_tuple:
        elements = rules[key_tuple]
        return process_elements(elements, rules, facts)

    return False


# def tokenize_query(query):
#     return [char for char in query if char.isalnum()]


def eval_query(rules, facts, queries):
    results = {}
    for query in queries:
        results[query] = eval_expr(rules, facts, query)
    return results


print(eval_query(rule, facts, "B"))

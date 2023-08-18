import networkx as nx


def parse_input(input_str):
    rpn_dict = {"+": "and", "|": "or", "=>": "implies",
                "<=>": "iff", "!": "not", "^": "xor"}
    rpn_string = ""

    for token in input_str:
        if token in rpn_dict:
            rpn_string += f" {rpn_dict[token]} "
        else:
            rpn_string += token

    return rpn_string


def build_dag(proposition_list):
    graph = nx.DiGraph()
    for prop in proposition_list:
        tokens = prop.split()
        stack = []

        for token in tokens:
            if token in {"and", "or", "implies", "iff", "not", "xor"}:
                if token == "not":
                    operand = stack.pop()
                    graph.add_node(operand)

                else:
                    operand2 = stack.pop()
                    operand1 = stack.pop()
                    graph.add_nodes_from([operand1, operand2])

                    edge_data = {"operation": token}

                    if token in {"implies", "and", "or", "xor"}:
                        graph.add_edge(operand1, operand2, **edge_data)

                    if token == "iff":
                        graph.add_edge(operand1, operand2, operation="implies")
                        graph.add_edge(operand2, operand1, operation="implies")

            else:
                stack.append(token)

    return graph


input_str = """
C => E
A + B + C => D
A | B => C
A + !B => F
C | !G => H
V ^ W => X
A + B => Y + Z
C | D => X | V
E + F => !V
A + B <=> C
A + B <=> !C
"""

propositions_raw = input_str.strip().split("\n")
rpn_propositions = [parse_input(prop) for prop in propositions_raw]

dag = build_dag(rpn_propositions)

print("Nodes:", dag.nodes())
print("Edges:", dag.edges(data=True))

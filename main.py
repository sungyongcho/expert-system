import os
import sys
import argparse
import readline

from backward_chaining import eval_query, forward_chaining
from parse import KnowledgeBaseDAG, parse_input, parse_oneline


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


def interactive_mode(kb: KnowledgeBaseDAG):
    try:
        while True:
            command = input("(expert-system) ").strip()
            if command == "help":
                print("\nAvailable commands:\n")
                print("  help - Display this help message")
                print("  rules - Display the rules in the knowledge base")
                print("  facts - Display the facts in the knowledge base")
                print("  = - Set the facts in the knowledge base")
                print("  =+ - Add a fact to the knowledge base")
                print("  ? - Evaluate a query using the knowledge base")
                print("  reasoning - Check reasoning mode status")
                print("  reasoning on - Turn on reasoning mode")
                print("  reasoning off - Turn off reasoning mode")
                print("  exit - Exit the interactive mode\n")
            elif command == "rules":
                print("Rules in the knowledge base:")
                print(kb)
            elif command == "facts":
                print("Facts in the knowledge base:")
                print(kb.facts)
                # Implement logic to display facts here
            elif command == "reasoning":
                print(
                    f"Reasoning mode is currently {'on' if kb.reasoning else 'off'}")
            elif command == "reasoning on":
                kb.reasoning = True
                print("Reasoning mode is now on")
            elif command == "reasoning off":
                kb.reasoning = False
                print("Reasoning mode is now off")
            elif command.startswith('='):
                fact = command[1:]
                if not fact:
                    print("Invalid command. The fact should follow after '='.")
                elif command.startswith('=+'):
                    fact = command[2:]
                    kb.add_facts(fact)
                    print(f"Fact '{fact}' added to the knowledge base.")
                else:
                    confirm = input("The knowledge base is not empty.\n"
                                    f"The current facts stored is {kb.facts}\n"
                                    "Do you want to continue? (y/n) ").strip().lower()
                    if confirm != 'y':
                        print("Operation cancelled.")
                        continue
                    kb.set_facts(fact)
                    print(f"Facts in the knowledge base set to '{fact}'.")
            elif command.startswith('?'):
                query = command[1:]
                if not query:
                    print("Invalid command. The query should follow after '?'.")
                else:
                    ##########################
                    result = forward_chaining(kb)
                    print('result:', result)
                    if result != "ERROR":
                        result = kb.eval_query(query)
                    print(f"The result of the query '{query}' is {result}.")
            elif command == "exit":
                break
            else:
                print("Unknown command. Type 'help' for available commands.")
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Exiting interactive mode.")


def main():
    parser = argparse.ArgumentParser(
        description="expert-system: Process input file and/or perform queries.")
    parser.add_argument("input_filename", nargs="?",
                        help="Path to the input file")
    parser.add_argument("-i", "--interactive",
                        action="store_true", help="Enable interactive mode")
    parser.add_argument("-r", "--reasoning",
                        action="store_true", help="Enable reasoning mode")

    args = parser.parse_args()

    if args.input_filename is None and not args.interactive:
        parser.print_help()
        sys.exit(1)

    kb = KnowledgeBaseDAG()

    if args.reasoning:
        print("Reasoning enabled.\n")
        kb.reasoning = True

    if args.input_filename:
        if args.interactive:
            print("(expert-system) ", end='')
            print(
                "Interactive mode enabled--will parse the input file and move to interactive mode\n")
            kb.interactive = True
        if not os.path.exists(args.input_filename):
            print(f"Error: File '{args.input_filename}' does not exist.")
            exit()
        with open(args.input_filename, "r") as f:
            for input_line in f:
                queries = parse_oneline(kb, input_line)
                if queries != None and not isinstance(queries, str) and queries < 0:
                    print("Error in syntax:",
                          f"[{input_line.strip()}]", f"{queries}")
                    exit()
                elif queries is not None:
                    if (len(kb.rules) == 0):
                        print("Error: No rules defined")
                        exit()
                    # print(kb)
                    ##########################
                    forward_result = forward_chaining(kb)
                    # print('result:', len(forward_result))
                    if len(forward_result) != 0:
                        print(forward_result)
                    else:
                        print(eval_query(kb, queries))

            current_position = f.tell()
            end_of_file = (current_position ==
                           os.fstat(f.fileno()).st_size)

            if end_of_file and not (kb.facts_given is True and kb.query_given is True):
                print("Error: query or facts not given")
                exit()
        if args.interactive:
            interactive_mode(kb)

    elif args.interactive:
        print("Interactive mode enabled.\n")
        kb.interactive = True
        interactive_mode(kb)


if __name__ == "__main__":
    main()

    # input_lines = f.readlines()

    # rules, initial_facts, queries = parse_input(input_lines)
    # print(queries)
    # print(rules)
    # print("========================\n")

    # print(eval_query(rules, initial_facts, queries))

import sys
import argparse
import readline

from backward_chaining import eval_query
from parse import KnowledgeBaseDAG, parse_input, parse_oneline


def interactive_mode(kb):
    try:
        while True:
            command = input("(expert-system) ").strip()
            if command == "help":
                print("Available commands:")
                print("help - Display this help message")
                print("rules - Display the rules in the knowledge base")
                print("facts - Display the facts in the knowledge base")
                print("exit - Exit the interactive mode")
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
            print(
                "Interactive mode enabled--will parse the rules first and move to interactive mode\n")
        with open(args.input_filename, "r") as f:
            for input_line in f:
                queries = parse_oneline(kb, input_line)
                if queries is not None:
                    print(eval_query(kb, kb.facts, queries))
        if args.interactive:
            interactive_mode(kb)

    elif args.interactive:
        print("Interactive mode enabled.\n")
        interactive_mode(kb)


if __name__ == "__main__":
    main()

    # input_lines = f.readlines()

    # rules, initial_facts, queries = parse_input(input_lines)
    # print(queries)
    # print(rules)
    # print("========================\n")

    # print(eval_query(rules, initial_facts, queries))

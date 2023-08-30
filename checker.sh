#!/bin/bash

# define color codes
YELLOW="\033[0;38;5;220m"
GREEN="\033[0;38;5;42m"
RED="\033[0;38;5;196m"
BLUE="\033[0;38;5;21m"
PINK="\033[0;38;5;205m"
PURPLE="\033[0;38;5;93m"
ORANGE="\033[38;5;202m"
FIN="\033[0m"

script_name=$(basename "$0")
program="./main.py"
output_file="output_file.txt"
verbose="false"

print_usage() {
	echo -e "Executing checker for expert-system.\n"
	echo -e "\tusage: ./$script_name [option] [verbose]"
	echo -e "\toptions:" 
	echo -e "\t\t--help : to read the manual" 
}

print_help() {
	echo -e "\toptions:" 
	echo -e "\t\t--help  : to read the manual" 
	echo -e "\t\t--basic : basic tests" 
	echo -e "\t\t--hard  : hard tests" 
	echo -e "\t\t--error : error tests" 
	echo -e "\t\t--good  : good files tests" 
	echo -e "\t\t--correction : to test for correction" 

	echo -e "\tverbose:" 
	echo -e "\t\tusage: ./$script_name [option] --verbose" 
}

run() {
	test_input="$1$2"
	#echo " test dir: $1, test input: $2"
	#echo " $test_input"

	output=$(python3	$program $test_input 2> /dev/null)
	parse_lines=$(cat $test_input | grep 'Result')
	#echo -e "$parse_lines"

	dictionary_strings=""
	while IFS= read -r line; do
		#echo "line: $line"
		if [ -z "$line" ]; then
			echo "Result is not provided, continuing to the next iteration..."
			continue
		fi

		#echo "line: $line"

		parse_line=$(echo $line | grep -oE '[A-Z]:[[:space:]]*[A-Za-z]+')
		if [ -z "$parse_line" ]; then
			dictionary_strings=$(echo $line | grep -o 'Error')
			#echo "Result is Error" 
			continue
		fi
	
		declare -A dictionary
		dictionary_string=""
	
		while read -r pair; do
			key=$(echo "$pair" | cut -d ':' -f 1)
		    value=$(echo "$pair" | cut -d ':' -f 2 | awk '{$1=$1};1') # Remove leading spaces
		
		    # Store the key-value pair in the associative array
		    dictionary["$key"]="$value"
			if [ -z "$dictionary_string" ]; then
	    	    dictionary_string="'$key': $value"
	    	else
	    	    dictionary_string="$dictionary_string, '$key': $value"
	    	fi
		done <<< "$parse_line"
	
	   	dictionary_string="{$dictionary_string}"
		if [ -z "$dictionary_strings" ]; then
			dictionary_strings+="$dictionary_string"
	    else
			dictionary_strings+="\n$dictionary_string"
		fi
	done <<< "$parse_lines"

	dictionary_strings=$(echo -e $dictionary_strings)
	if [ "$verbose" = "true" ]; then
		echo -e "\nreal:\n\n$dictionary_strings"
		echo -e "\nmine:\n\n$output"
	fi

	if [ "$dictionary_strings" = "$output" ]; then
		echo -e "${GREEN}OK${FIN}"
	else
		echo -e "${RED}FAIL${FIN}"
	fi
}

check_options() {
	if [ $1 == "--help" ]; then
		print_help
	elif [ $1 == "--basic" ]; then
		test_dir="tests/basic/"
		test_list=$(ls $test_dir)
	elif [ $1 == "--hard" ]; then
		test_dir="tests/hard/"
		test_list=$(ls $test_dir)
	elif [ $1 == "--good" ]; then
		test_dir="tests/_examples/good_files/"
		test_list=$(ls $test_dir)
	elif [ $1 == "--error" ]; then
		test_dir="tests/error/"
		test_list=$(ls $test_dir)
	elif [ $1 == "--correction" ]; then
		test_dir="tests/_correction/"
		test_list=$(ls $test_dir)
	else
		print_usage
	fi
}

check_flag() {
	if [ $# -eq 1 ]; then
		check_options $1
	elif [ $# -eq 2 ]; then
		if [ $2 == "--verbose" ]; then
			echo "set verbose=true"
			verbose="true"
		fi
		check_options $1
	fi
}

if [ $# -eq 0 ]; then
	print_usage

elif [ $# -ge 1 ]; then
	check_flag $1 $2

	#echo "$test_list"
	i=1
	for test_file in $test_list; do
		#echo "$test_file"
		echo -ne "\n${YELLOW}TEST $i $test_file ${FIN}"
		run $test_dir $test_file
		((i++))
	done
fi

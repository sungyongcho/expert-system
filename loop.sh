#!/bin/bash

run() {
	test_input="$1$2"
	for f in $test_input; do
		#echo $f
		echo "#Result should be Error" >> $f
	done
}

test_dir="./tests/_examples/bad_files/"
test_list=$(ls $test_dir)
#echo $test_list
for test_file in $test_list; do
	run $test_dir $test_file
done

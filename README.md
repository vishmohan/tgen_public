# tgen
simple repo for a riscv testgen

flow:
tgen 
	- gen test
		- get_preamble
		- sequences.gen_sequences
				- skeleton.get_skeleton
				- generate_code_sequences
	- gen linker


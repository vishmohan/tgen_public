#! /usr/bin/env python3
import getopt
import sys
import subprocess

def getargs():
	options,remainder = getopt.getopt(sys.argv[1:],"",['file=','linker=','dis'])

	fname=""
	lname=""
	disassembly=1

	for opt,arg in options:
		if opt=='--file':
			fname = arg
		elif opt=='--linker':
			lname = arg
		elif opt=='--dis':
			disassembly = 1
		else:
			pass

	return fname,lname,disassembly

def main():
	src_file,linker_file,disassembly = getargs()
	basename = src_file.split('.')[0]
	obj_file = basename + ".o" #src_file = test.s, obj_file = test.o
	elf_file = basename + ".elf"
	dis_file = basename + ".dis"
	mflags = "rv64gcv_zba_zbb_zbc_zbs_svinval"
	bcmd = f"/proj/tools/riscv64-unknown-elf/bin/as -march={mflags} {src_file} -o {obj_file}"
	lcmd = f"/proj/tools/riscv64-unknown-elf/bin/ld -T {linker_file} {obj_file} -o {elf_file}"
	dcmd =  f"/proj/tools/bin/riscv64-unknown-elf-objdump --disassemble-all {elf_file} > {dis_file}"
	
	print("Assembling test.......")
	st,op = subprocess.getstatusoutput(bcmd)
	if st:
		print(f"Error during assembly: {op}")
		sys.exit(-1)
	print("Linking.......")
	st,op = subprocess.getstatusoutput(lcmd)
	if st:
		print(f"Error during linking: {op}")
		sys.exit(-1)

	print("Generating disassembly.......")
	st,op = subprocess.getstatusoutput(dcmd)
	if st:
		print(f"Error during disassembly: {op}")
		sys.exit(-1)

	return 0





if __name__=="__main__":
	main()

#! /usr/bin/env python3
import getopt
import sys
import subprocess

def getargs():
	options,remainder = getopt.getopt(sys.argv[1:],"",['file=','linker=','arch=','dis'])

	fname=""
	lname=""
	disassembly=1
	arch="rv64"

	for opt,arg in options:
		if opt=='--file':
			fname = arg
		elif opt=='--linker':
			lname = arg
		elif opt=='--dis':
			disassembly = 1
		elif opt=='--arch':
			arch = arg
		else:
			pass

	return fname,lname,disassembly, arch

def main():
	src_file,linker_file,disassembly, arch = getargs()
	basename = src_file.split('.')[0]
	obj_file = basename + ".o" #src_file = test.s, obj_file = test.o
	elf_file = basename + ".elf"
	dis_file = basename + ".dis"
	mflags = "rv64gcv_zba_zbb_zbc_zbs_svinval"
	mabi = "lp64"
	tgt_emu = "elf64lriscv"

	if arch=="rv32":
		mflags = "rv32gcv_zba_zbb_zbc_zbs_svinval"
		mabi = "ilp32"
		tgt_emu = "elf32lriscv"

	bcmd = f"/proj/tools/riscv64-unknown-elf/bin/as -march={mflags} -mabi={mabi} {src_file} -o {obj_file}"
	lcmd = f"/proj/tools/riscv64-unknown-elf/bin/ld -m {tgt_emu} -T {linker_file} {obj_file} -o {elf_file}"
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

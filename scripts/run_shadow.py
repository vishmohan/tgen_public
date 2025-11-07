#! /usr/bin/env python3

import sys
import subprocess
import getopt


def getargs():
	options,remainder = getopt.getopt(sys.argv[1:],'',['elf=','def=','threads='])
	myelf = ""
	defines = ""
	threads = "1"

	for opt,arg in options:
		if opt=='--elf':
			myelf = arg
		elif opt=='--def':
			defines = arg
		elif opt=='--threads':
			threads = arg
		else:
			pass

	return myelf,defines,threads


def main():
	myelf,defines, threads = getargs()
	mt = True

	if not myelf:
		print("please provide an elf file")
		sys.exit(-1)

	if threads==str(1):
		mt = False

	if not defines:
		if mt:
			defines = "/nfs/home/vmohan/riscv/tests/defines_mt.h"
		else:
			defines = "/nfs/home/vmohan/riscv/tests/defines.h"
	
	
	logfile = "shadow.log"
	shadow_bin = "/proj/work/vmohan/shadow/build-Linux/shadow"
	if mt:
		harts = int(threads)
		cores = 1
		cmd = f"{shadow_bin} --target {myelf} --maxinst 100000 --cores 1 --harts {harts} --logfile {logfile} --tracePTE --sysconfigfile {defines}"
	else:
		cmd = f"{shadow_bin} --target {myelf} --maxinst 100000 --logfile {logfile} --tracePTE --sysconfigfile {defines}"
	print(f"Running: {cmd}\n")
	st,op = subprocess.getstatusoutput(cmd)
	if not st:
		print("Done")
		sys.exit(0)
	else:
		print("Error:")
		print(op)
		sys.exit(-1)


if __name__ == "__main__":
	main()

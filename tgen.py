#! /usr/bin/env python3
import sys
import getopt
import subprocess
import gen_test
import gen_linker
import gen_opt
import os

def getargs():
	options, remainder = getopt.getopt(sys.argv[1:],'',['count=','threads=','pagingmode='])
	opt_arg = {}
	for opt,arg in options:
		if opt=='--count':
			opt_arg["count"]=int(arg)
		elif opt=='--threads':
			opt_arg["threads"]=int(arg)
		elif opt=='--pagingmode':
			opt_arg["pagingmode"]=arg

	return opt_arg

def main():
	switches = getargs()
	tod_cmd	= "date +\"%m%d%Y_%H%M%S_%N\""
	p = subprocess.getoutput(tod_cmd)
	loc = subprocess.getoutput('pwd')
	src_dir = "test_src_"+ p
	fullpath = loc + "/" + src_dir + "/"
	tcount = switches['count'] if 'count' in switches else 1
	num_threads = switches['threads'] if 'threads' in switches else 1
	pagingmode = switches['pagingmode'] if 'pagingmode' in switches else "sv57"
	lstr = ""
	lfname = "test_" + p + ".list"
	create_dir = f"mkdir {fullpath}"
	symlink_name = "latest"
	create_symlink = f"ln -s  {fullpath} {symlink_name}"
	remove_symlink = f"unlink {symlink_name}"
	st, op = subprocess.getstatusoutput(create_dir)
	if st:
		print("Error creating directory")
		sys.exit(1)
	if os.path.exists(f"{symlink_name}"):
		st1, op1 = subprocess.getstatusoutput(remove_symlink)
		if not st1:
			print(f"removed sysmlink {symlink_name}")
	st, op = subprocess.getstatusoutput(create_symlink)
	if st:
		print("Error creating symlink")
		sys.exit(1)
	for i in range(tcount):
		fname = "test_"+str(i)+"_"+p
		suffix_asm = ".s"
		suffix_linker = ".ld"
		gen_test.gen_test(fname=fname,suffix=suffix_asm,fullpath=fullpath,pagingmode=pagingmode)
		gen_linker.gen_linker(fname,suffix_linker,suffix_asm,fullpath)
		#generate opt and return list file value
		lstr += gen_opt.gen_opt(fname,suffix_asm,suffix_linker,fullpath,num_threads,pagingmode) 
	print(f"Done generating {tcount} tests")
	print(f"Writing list file: {lfname}")
	with open(fullpath+lfname,"w") as fout:
		print(lstr,file=fout)


if __name__ == "__main__":
	main()

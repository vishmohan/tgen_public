#! /usr/bin/env python3
import re
import sys

mdict = {}

def gen_prestr():
	mstr = '''
OUTPUT_ARCH( "riscv" )
ENTRY(_start)
SECTIONS
{
	'''
	return mstr

def gen_body():
	mstr = ""
	for k,v in mdict.items():
		mstr += ". = " + v + ";\n"
		mstr += k + " : " + "{ *" + f"({k})" + " }\n"
	return mstr

def gen_poststr():
	mstr = '''
	. = ALIGN(0x1000);
  .tohost : { *(.tohost) }
	. = ALIGN(0x1000);
  .data : ALIGN(0x800) { *(.data) *(.rodata*) STACK = ALIGN(16) + 0x8000; }
  .bss : { *(.bss)}
  _end = .;
	}
	'''
	return mstr

#format1: #{.mdata:0x2000} -> group1 = .mdata, group2 = 0x2000
#format2: #{.mdata:0x2000:0x2000} -> group1 = .mdata, group2 = 0x2000:0x2000 group2 contains a ':'
def gen_linker(fname,lsuffix=".ld",asmsuffix=".s"):
	matchRe = re.compile("#{(.*?):(.*)}")
	with open(fname+asmsuffix,"r") as fin:
		for line in fin:
			match = matchRe.match(line)
			if match:
				if ':' in match.group(2):
					mdict[match.group(1)] = match.group(2).split(':')[1]	#format2
				else:
					mdict[match.group(1)] = match.group(2)	#format1

	mstr = ""
	mstr += gen_prestr()
	mstr += gen_body()
	mstr += gen_poststr()

	with open(fname+lsuffix,"w") as fout:
		print(mstr,file=fout)

	

if __name__=="__main__":
	fname = sys.argv[1]
	gen_linker(fname)

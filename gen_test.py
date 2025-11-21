#! /usr/bin/env python3

import preamble
import sequences
import rv32sequences

#def gen_test(fname,suffix,fullpath):
def gen_test(**kwargs):
	mstr  = ""
	fullpath = kwargs['fullpath']
	fname = kwargs['fname']
	suffix = kwargs['suffix_asm']
	pagingmode = kwargs['pagingmode']
	arch = kwargs.get("arch","rv64") #arch = rv64 if not specified
	mstr += preamble.get_preamble(arch=arch)
	if arch=="rv64":
		tstr, nopreamble = sequences.gen_sequences(pagingmode=pagingmode) #some skeletons do not need a preamble
	else:
		tstr, nopreamble = rv32sequences.gen_sequences(pagingmode=pagingmode) #some skeletons do not need a preamble

	if nopreamble:
		mstr = tstr
	else:
		mstr += tstr
	with open(fullpath+fname+suffix,"w") as f:
		print(mstr, file=f)

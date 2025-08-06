#! /usr/bin/env python3

import preamble
import sequences

def gen_test(fname,suffix,fullpath):
	mstr  = ""
	mstr += preamble.get_preamble()
	mstr += sequences.gen_sequences()
	with open(fullpath+fname+suffix,"w") as f:
		print(mstr, file=f)

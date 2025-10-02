#! /usr/bin/env python3

import preamble
import sequences

#def gen_test(fname,suffix,fullpath):
def gen_test(**kwargs):
	mstr  = ""
	fullpath = kwargs['fullpath']
	fname = kwargs['fname']
	suffix = kwargs['suffix']
	pagingmode = kwargs['pagingmode']
	mstr += preamble.get_preamble()
	mstr += sequences.gen_sequences(pagingmode=pagingmode)
	with open(fullpath+fname+suffix,"w") as f:
		print(mstr, file=f)

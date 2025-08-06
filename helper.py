#! /usr/bin/env python3

#=================================================================
def show_aliases(mlist):
#=================================================================
	for alias in mlist:
		print(hex(alias))

#=================================================================
def extract_bits(pc,ub,lb):
#=================================================================
	'''
		extract the pc bits specified by upper bound and lower bound
	'''
	ub_mod = 63-ub
	lb_mod = 63-lb
	pc_ub_lb = pc[ub_mod:lb_mod+1]
	return pc_ub_lb

#=================================================================
def extend_pc(pc):
#=================================================================
	'''
		extend the given pc to full 64 bits as a binary string
	'''
	pc_bin = f"{pc:b}"
	mlen = len(pc_bin)
	full_pc_bin = pc_bin
	if mlen!=64:
		full_pc_bin = "0" * (64-mlen) + pc_bin
	return full_pc_bin

#=================================================================
def compute_xor(pc0,pc1,pc2):
#=================================================================
	''' 
		compute hash 
	'''
	val0 = int(pc0,2)
	val1 = int(pc1,2)
	val2 = int(pc2,2)
	return val0 ^ val1 ^ val2

#! /usr/bin/env python3

#BTB2 hashes:
#btb2 tag hash = pc[53:40]^pc[39:26]^pc[25:12]
#btb2 address hash = pc[11:4]^pc[19:12]^pc[27:20]
#BTB hashes:
#btb tag hash = 		pc[48:36] ^ pc[35:23]^pc[22:10]
#btb address hash = pc[9:5]^ pc[14:10] ^ pc[19:15]

import sys
import re
import getopt
import l2btb
import l1btb
import helper

opt_arg = {}
defines_dict = {}

#defines_dict = {
#	'RV_BTB2_ADDR_HI':,
#	'RV_BTB2_ADDR_LO':,
#	'RV_BTB2_FOLD2_INDEX_HASH': False,
#	'RV_BTB2_BTAG_SIZE':,
#}
#btb_ub_lb_tag  = [(48,36),(35,23),(22,10)]
#btb_ub_lb_addr = [(9,5),(14,10),(19,15)]
#btb2_ub_lb_tag  = [(53,40),(39,26),(25,12)]
#btb2_ub_lb_addr = [(11,4),(19,12),(27,20)]


#=================================================================
def populate_defines():
#=================================================================
	'''
	populates defines_dict according to common_defines
	'''
	matchRe = re.compile(r"`define (.*) (.*)")
	matchRe1 = re.compile(r"`define (.*)")
	with open('common_defines.vh','r') as fin:
		for line in fin:
			match = matchRe.match(line)
			if match:
				k=match.group(1)
				v=match.group(2)
				defines_dict[k] = v
			else:
				match = matchRe1.match(line)
				if match:
					k=match.group(1)
					defines_dict[k] = True

#=================================================================
def get_args():
#=================================================================
	'''
	parse arguments
	'''
	options,remainder = getopt.getopt(sys.argv[1:],'',['pc=', 'count=','l2btb','l1btb'])
	for opt,arg in options:
		if opt=='--pc':
			opt_arg['pc']=arg
		if opt=='--count':
			opt_arg['count']=int(arg)
		if opt=='--l2btb':
			opt_arg['l2btb'] = 1
		if opt=='--l1btb':
			opt_arg['l1btb'] = 1
	if opt_arg.get('pc',0)==0:
		print("please specify input pc")
		sys.exit(-1)
	if opt_arg.get('l1btb',0)==0 and opt_arg.get('l2btb',0)==0:
		print("specify l1btb or l2btb")
		sys.exit(-1)
	if opt_arg.get('count',0)==0:
		print("please specify count for aliases")
		sys.exit(-1)

#=================================================================
def main():
#=================================================================
	get_args() #populate opt_arg
	pc = int(opt_arg['pc'],16)
	populate_defines()
	fullpc = helper.extend_pc(pc)
	print(f"orig pc: {opt_arg['pc']}")
	if 'l2btb' in opt_arg and opt_arg['l2btb']==1:
		h = l2btb.l2btb(defines_dict,opt_arg['count'],fullpc)
		h.find_aliasing_pc_l2btb()
		print("L2btb aliases:")
		helper.show_aliases(h.alias_list)
		print("========================")
	#if 'l1btb' in opt_arg and opt_arg['l1btb']==1:
	#	h = l1btb.l1btb(defines_dict,opt_arg['count'],fullpc)
	#	h.find_aliasing_pc_l1btb()
	#	print("L1btb aliases:")
	#	helper.show_aliases(h.alias_list)
	#	print("========================")
#=================================================================



if __name__ == "__main__":
	main()

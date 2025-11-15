#! /usr/bin/env python3
import random
import re

#example: .code4:0x180003000
#k = .code4
#v = 0x180003000
segments = {}
segments_va = {}

def parse_skeleton(fname):
	segments.clear()
	segments_va.clear()
	matchRe = re.compile("#{(.*?):(.*)}")
	matchRe1 = re.compile("#{(.*):(.*):(.*)}")
	with open(fname,"r") as fin:
		for line in fin:
			match = matchRe.match(line)		#{segment:pa}
			match1 = matchRe1.match(line) #{segment:va:pa}
			if match:
				segments[match.group(1)] = match.group(2)
			if match1:
				segments_va[match1.group(1)] = match1.group(2)

def get_skeleton(**kwargs):
	''' returns the skeleton as a string '''
	nopreamble_skeletons = ["b5489_2.s", "b5489_3.s", "b5489_4.s", "b5489_5.s", "b5489_6.s"]
	nopreamble = 0

	#sv57 templates
	templates = ["rv64_sv57_512g.s","template_branch.s","rv64_branch_aliasing1.s"]
	templates.append("rv64_sv57_512g_1.s")
	templates.append("palladium_aliasing.s")
	templates.append("rv64_sv57_512g_2.s")
	templates.append("rv64_sv57_512g_3.s")
	templates.append("rv64_sv57_512g_4.s")
	templates.append("rv64_sv57_512g_5.s")
	templates.append("rv64_sv57_512g_6.s")
	templates.append("rv64_sv57_512g_7.s")
	templates.append("rv64_sv57_512g_svadu.s")
	templates.append("rv64_sv57_512g_svadu_vs.s")
	templates.append("rv64_sv57_512g_svadu_vu.s")
	templates.append("rv64_sv57_512g_vs.s")
	templates.append("rv64_sv57_512g_vu.s")
	templates.append("rv64_sv57_512g_1_smepmp.s")
	templates.append("rv64_sv57_512g_svadu_smepmp_vs.s")

	#sv48 templates
	templates_sv48 = ["rv64_sv48_512g_svadu_vs.s"]
	templates_sv48.append("rv64_sv48_4k_vs.s")
	templates_sv48.append("rv64_sv48_4k_vs_bare.s")
	templates_sv48.append("rv64_sv48_4k_svadu_vs.s")
	templates_sv48.append("rv64_sv48_4k.s")
	templates_sv48.append("rv64_sv48_4k_1.s")
	templates_sv48.append("rv64_sv48_vector.s")
	templates_sv48.append("rv64_sv48_vector_1.s")
	templates_sv48.append("rv64_sv48_vector_2.s")
	templates_sv48.append("b5489_2.s")
	templates_sv48.append("b5489_3.s")
	templates_sv48.append("b5489_4.s")
	templates_sv48.append("b5489_5.s")
	templates_sv48.append("b5489_6.s")

	#templates_sv48 = ["b5489_2.s","b5489_3.s","b5489_4.s","b5489_5.s","b5489_6.s"]
	#templates_sv48.append("rv64_sv48_4k.s")
	#templates_sv48.append("rv64_sv48_4k_1.s")
	#templates_sv48.append("rv64_sv48_vector.s")
	#templates_sv48.append("rv64_sv48_vector_1.s")
	#templates_sv48.append("rv64_sv48_vector_2.s")

	


	pagingmode = kwargs['pagingmode']
	if pagingmode == "sv48":
		mname = random.choice(templates_sv48)
	else:
		mname = random.choice(templates)

	#if chosen skeleton does not require preamble set flag 
	if mname in nopreamble_skeletons:
		nopreamble = 1

	mstr = ""
	parse_skeleton(mname) #populate sections and their bases in the segments dictionary
	mstr += f"##skeleton name: {mname}\n"
	with open(mname,"r") as f:
		mstr += f.read()
	return mstr, nopreamble

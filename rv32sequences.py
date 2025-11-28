#! /usr/bin/env python3

from collections import defaultdict
import skeleton
import random
import re


#example: .code4:[0x180003000, "2B"]
#k = .code4
#v = [0x180003000, "2B"]
info = defaultdict(dict)
info_va = defaultdict(dict)
ret_info = set() #contains set of all return segments .ret1 , .ret2 etc
ret_info_exclude = set() #exclusion set [calls will not be generated to these segments]
data_seg = [".mdata",".mdata1",".mdata2",".mdata3",".mdata4"] 	 #for doing loads


arith_logical_ops = {
	"add":   	("rd","rs1","rs2"),
	"addi":  	("rd","rs1","imm"), #imm[11:0]
#	"addiw": 	("rd","rs1","imm"), #imm[11:0]
#	"addw":  	("rd","rs1","rs2"),
	"and":   	("rd","rs1","rs2"),
	"andi":  	("rd","rs1","imm"), #imm[11:0]
}



bcond_list = [ "x"+str(i)   for i in range(20,31) ] #x20 thru x30
gpr_list = [ "x"+str(i)   for i in range(1,15) if i!=2 ] 	#x1 thru x14 (exclude x2)
gpr_list_zero = ["x15","x16"]
gpr_list_negative = ["x17","x18", "x19"]
gpr_values_init = {} #contains initial values of gprs

ret_list = ["ret\n", "c.jr x1\n", "jalr x0, (x1)\n", "jalr x5, (x1)\n", "jalr x1, (x1)\n"]

#*************************************
#helper functions
#*************************************
def set_label(mstr):
	return f"{mstr}:\n"

def pick_one_key(mdict):
	''' picks one random key '''
	return random.choice(list(mdict.keys()))

def pick_one(mstr="rd"):
	''' picks one register '''
	if mstr in ["rd","rs1","rs2"]:
		chosen_reg = random.choice(gpr_list)
		return chosen_reg
	if mstr=="imm":
		return random.randint(-2048, 2047)

def get_loop_count():
	''' return loop count '''
	loop_cnt_lo = 2
	loop_cnt_hi = 16
	return random.randint(loop_cnt_lo, loop_cnt_hi)

#*************************************
#setup mfc0
#*************************************
def	setup_mfc0():
	'''
		write mfc0 randomly 
		icache_flush 	bit_19
		disable_bpred bit_3
	'''
	codestr = ""
	icache_flush = random.randint(0,1)
	disable_bpred = random.randint(0,1)

	if icache_flush:
		codestr +=  "bseti x1, x0, BIT_MFC0_ICACHE_FLUSH\n"	
	else:
		codestr +=  "add x1, x0, x0\n"

	if disable_bpred:
		codestr += "bseti x1, x1, BIT_MFC0_DISABLE_BPRED\n"	
	else:
		codestr +=  "add x1, x0, x0\n"

	codestr += "csrs mfc0, x1\n"
	return codestr

#*************************************
#setup mfc1
#*************************************
def	setup_mfc1():
	'''
		write mfc1 randomly 
		icache_way_disable 	bit_19:16
		btbi_m_mode disable 6
		ras_disable   			5
		btbi_disable  			4
		npc_disable   			3
		ittage_disable 			2
		tage_disable   			1
		prefetch_disable 		0
	'''
	codestr = ""
	
	codestr +=  "add x1, x0, x0\n"
	icache_way_disable = random.randint(0,1)
	icache_all_ways = random.randint(0,1)
	if icache_way_disable:
		if not icache_all_ways:
			way = random.randint(0,3)
			codestr += "bseti x1, x1, BIT_MFC1_ICACHE_WAYDISABLE_LO\n"
			codestr += f"slli  x1, x1, {way}\n"
		else:
			codestr += 	"li x1, 0xf\n"
			codestr += f"slli  x1, x1, BIT_MFC1_ICACHE_WAYDISABLE_LO\n"
		
	btbi_disable = random.randint(0,1)
	if btbi_disable:
		codestr += "bseti x1, x1, BIT_MFC1_BTBI_DISABLE\n"
		codestr += "bseti x1, x1, BIT_MFC1_BTBI_DISABLE_M\n"

	btbi_m_mode_disable = random.randint(0,1)
	if btbi_m_mode_disable and not btbi_disable:
		codestr += "bseti x1, x1, BIT_MFC1_BTBI_DISABLE_M\n"

	ras_disable = random.randint(0,1)
	if ras_disable:
		codestr += "bseti x1, x1, BIT_MFC1_RAS_DISABLE\n"

	npc_disable = random.randint(0,1)
	if npc_disable:
		codestr += "bseti x1, x1, BIT_MFC1_NPC_DISABLE\n"

	ittage_disable = random.randint(0,1)
	if ittage_disable:
		codestr += "bseti x1, x1, BIT_MFC1_ITTAGE_DISABLE\n"

	tage_disable = random.randint(0,1)
	if tage_disable:
		codestr += "bseti x1, x1, BIT_MFC1_TAGE_DISABLE\n"

	prefetch_disable = random.randint(0,1)
	if prefetch_disable:
		codestr += "bseti x1, x1, BIT_MFC1_PREFETCH_DISABLE\n"

	codestr += "csrw mfc1, x1\n"

	return codestr
#*************************************
#setup gprs
#*************************************
def	setup_gprs():
	'''
		1.  x20 < x21 < x22 .... < x30 (unsigned comparison)
		2.  x31 is special => contains loop_counter
		3.  x15, x16 = 0
		4.  x17 < x18 < x19 negative numbers  (signed comparisons)
	'''
	codestr = ""
	val = random.randint(1,0xffffffffff)
	loop_counter = random.randint(32,1024)
	inc = random.randint(4,32)
	#x20 thru x30
	for reg in bcond_list:
		codestr += f"\tli {reg}, {hex(val)}\n" 
		gpr_values_init[reg] = val
		val = val+inc

	#x15, x16, x31
	codestr += f"\tli x31, {hex(loop_counter)}\n" 
	codestr += f"\tli x15, 0\n" 
	codestr += f"\tli x16, 0\n" 
	gpr_values_init["x31"] = loop_counter
	gpr_values_init["x15"] = 0
	gpr_values_init["x16"] = 0

	#x17, x18, x19
	x = [random.randint(-1024, -10) for i in range(3)]
	v = x.pop(x.index(min(x)))
	codestr += f"\tli x17, {v}\n" 
	gpr_values_init["x17"] = v
	v = x.pop(x.index(min(x)))
	codestr += f"\tli x18, {v}\n" 
	gpr_values_init["x18"] = v
	v = x.pop(x.index(min(x)))
	codestr += f"\tli x19, {v}\n" 
	gpr_values_init["x19"] = v

	#x1 thru x14 (excluding x2)
	for reg in gpr_list:
		val = random.randint(1,0xffffffffff)
		codestr += f"\tli {reg}, {hex(val)}\n" 
		gpr_values_init[reg] = val

	codestr += f"\tlui x2, 0x5\n" #x2 = stack pointer = 0x5000
	return codestr

#*************************************
#13. generate fence.i
#*************************************
def generate_icache_flush():
	'''
		fence.i to generate icache flushes
	'''
	codestr = "#Generating fence.i\n"
	codestr += "fence.i\n"
	return codestr

#*************************************
#12. generate compressed/uncompressed returns
#*************************************
def generate_return_sequences(retname):
	'''
	If the skeleton contains return segments this routine populates those segments
	<instr1>
	<instr2>
	<instr3>
	<instr4>
	<compressed or uncompressed return>
	Thus this function creates subroutines that can be called from any of the code segments.
	'''
	codestr = ""
	subroutine_length = random.randint(1,128)
	idx = gpr_list.index("x1")
	gpr = gpr_list.pop(idx) #pop the "x1" register. will be reserved for the return instruction
	codestr += gen_arith_logical_instructions(subroutine_length)
	if random.randint(0,1):
		ret_info_exclude.add(retname)												#add	the segment to the exclusion set
		codestr += gen_call()		 														#will generate call to a segment in ret_info
	codestr += "lw x1, (x2) #return pc from the stack\n"  #return pc from the stack
	codestr += "addi x2, x2, 8 #update stack pointer\n"   #update stack pointer
	codestr += set_label("5")
	codestr += random.choice(ret_list)
	gpr_list.insert(idx,gpr) #add back the gpr
	return codestr

#*************************************
#11. generate compressed c.beqz with x8
#branches will split fetch group
#*************************************
def gen_cbeqz_x8always_taken_forward():
	''' c.beqz always taken forward with x8 '''
	codestr = ""
	codestr += f"#Generating c.beqz x8 always taken (forward) sequence\n" 
	codestr += "xor x8, x8, x8\n"
	for i in range(random.randint(1,32)):
		codestr += f"c.beqz x8, 3f\n"
		codestr += set_label("3")
	return codestr

#*************************************
#10. generate compressed c.beqz
#*************************************
def gen_cbeqz_always_taken_forward():
	''' c.beqz always taken foward '''
	codestr = ""
	loop_length = get_loop_count() #how many instructions does the loop have?
	codestr += f"#Generating c.beqz always taken (forward) sequence with max loop_length = {loop_length}\n"
	chosen_reg = random.choice(["x10","x11","x12"]) #compressed sequence must have >= x8
	rval	= random.randint(1,32)
	idx = gpr_list.index(chosen_reg)
	gpr = gpr_list.pop(idx) #pop the chosen loop count register from the gpr list
													#we don't want the gen_arith to pick this gpr
	codestr += f"xor {chosen_reg}, {chosen_reg}, {chosen_reg}\n"
	for i in range(random.randint(1,32)):
		codestr += gen_arith_logical_instructions(random.randint(1,loop_length))
		codestr += f"c.beqz {chosen_reg}, 2f\n"
		codestr += gen_arith_logical_instructions(random.randint(1,loop_length))
		codestr += set_label("2")
	gpr_list.insert(idx,gpr) #add back the gpr
	return codestr

#*************************************
#9. generate compressed c.bnez
#*************************************
def gen_cbnez_always_taken_backward():
	''' c.bnez always taken backward '''
	codestr = ""
	loop_length = get_loop_count() #how many instructions does the loop have?
	codestr += f"#Generating c.bnez always taken (backward) sequence with max loop_length = {loop_length}\n"
	chosen_reg = random.choice(["x10","x11","x12"]) #compressed sequence must have >= x8
	rval	= random.randint(1,32)
	idx = gpr_list.index(chosen_reg)
	gpr = gpr_list.pop(idx) #pop the chosen loop count register from the gpr list
													#we don't want the gen_arith to pick this gpr
	codestr += f"li {chosen_reg}, {rval}\n"
	codestr += set_label("2")
	codestr += gen_arith_logical_instructions(random.randint(1,loop_length))
	codestr += f"addi {chosen_reg}, {chosen_reg}, -1\n"
	codestr += f"c.bnez {chosen_reg}, 2b\n"
	gpr_list.insert(idx,gpr) #add back the gpr
	return codestr

#*************************************
#8. generate loads and stores
#*************************************
def gen_loads_and_stores():
	codestr = ""
	k = random.choice(data_seg)
	#use va when specified
	if k in info_va:
		base_address = int(info_va[k]["base"],16)
	else:
		base_address = int(info[k]["base"],16)
	num = random.randint(8,16)
	codestr += f"#Generating loads/stores upto {num} count\n"
	for i in range(num):
		offset = random.randint(16, 4088)  #4k offset
		addr	 =	base_address + offset	
		choose_reg = random.choice(gpr_list)
		addr_reg = random.choice(gpr_list)
		ld_flavor = ["lb","lh","lw"]
		st_flavor = ["sb","sh","sw"]
		load_type = random.choice(ld_flavor)
		store_type = random.choice(st_flavor)
		codestr += f"li {addr_reg}, {hex(addr)}\n"
		codestr += f"{load_type} {choose_reg}, ({addr_reg})\n" #load
		codestr += f"addi {choose_reg}, {choose_reg}, 1\n" #modify
		if choose_reg == addr_reg:
			codestr += f"li {addr_reg}, {hex(addr)}\n"		#load addres again
		codestr += f"{store_type} {choose_reg}, ({addr_reg})\n" #store
	return codestr
#*************************************
#8a. generate store to load forwarding
#*************************************
def gen_stlf():
	codestr = ""
	k = random.choice(data_seg)
	#use va when specified
	if k in info_va:
		base_address = int(info_va[k]["base"],16)
	else:
		base_address = int(info[k]["base"],16)
	num = random.randint(8,16)
	codestr += f"#Generating store  to load forwarding upto {num} count\n"
	for i in range(num):
		offset = random.randint(16, 4088)  #4k offset
		addr	 =	base_address + offset	
		choose_reg = random.choice(gpr_list)
		addr_reg = random.choice(gpr_list)
		ld_flavor = ["lb","lh","lw"]
		st_flavor = ["sb","sh","sw"]
		load_type = random.choice(ld_flavor)
		store_type = random.choice(st_flavor)
		codestr += f"li {addr_reg}, {hex(addr)}\n"
		codestr += f"{store_type} {choose_reg}, ({addr_reg})\n" #store
		codestr += f"{load_type}  {choose_reg}, ({addr_reg})\n" #load
	return codestr

#*************************************
#7. generate arith/logical
#*************************************
def gen_arith_logical_instructions(num=64):
	mstr = ""
	mstr += f"#Generating arith/logical instructions num = {num}\n"
	for i in range(num):
		op = pick_one_key(arith_logical_ops)
		mstr += f"{op} "
		for e in arith_logical_ops[op]:
			item = pick_one(e)
			mstr += f"{item}, "
		mstr = mstr.rstrip() #remove trailing white space
		mstr = mstr.rstrip(',') #remove trailing comma
		mstr += "\n"
	return mstr

#*************************************
#6. generate c.jal, c.j
#*************************************
def gen_unconditional_jmp():
	''' compressed unconditional jump '''
	codestr = ""
	jump_with_link = 0
	loop_length = get_loop_count() #how many instructions to skip
	codestr += f"#Generating compressed jumps with max loop_length = {loop_length}\n"
	codestr += gen_arith_logical_instructions(random.randint(1,loop_length))
	if jump_with_link:
		codestr += "c.jal 1f\n" #this expands to jal x1, offset.
													  #cannot specify a destination here
														#only supported with rv32ic not with rv64ic
	else:
		codestr += "c.j	1f\n"
	codestr += gen_arith_logical_instructions(random.randint(1,loop_length))
	codestr += set_label("1") 
	return codestr

#*************************************
#6a. generate c.jal, c.j
#difference with 6 is after the unconditional it loops backward once
#*************************************
def gen_unconditional_jmp_backward_jcc():
	''' compressed unconditional jump with a backward jcc '''
	codestr = ""
	jump_with_link = 0
	loop_length = get_loop_count() #how many instructions to skip
	loop_length1 = random.randint(2,16) #unique loop length for the jal
	codestr += f"#Generating compressed jumps/backward jcc with max loop_length = {loop_length},loop_length1 = {loop_length1} \n"
	rs1			 = random.choice(gpr_list)
	idx 		 = gpr_list.index(rs1)
	gpr 		 = gpr_list.pop(idx) #pop the "rs1" register. 
	codestr += f"li {rs1}, 2\n" #fixed to 2 backward jcc is taken exactly once
	codestr += set_label("1") 
	codestr += f"addi {rs1}, {rs1}, -1\n"
	codestr += gen_arith_logical_instructions(random.randint(1,loop_length))
	if jump_with_link:
		codestr += "c.jal 2f\n" #this expands to jal x1, offset.
													  #cannot specify a destination here
														#only supported with rv32ic not with rv64ic
	else:
		codestr += "c.j	2f\n"
	codestr += gen_arith_logical_instructions(random.randint(1,loop_length1))
	codestr += set_label("2") 
	codestr += f"bnez {rs1}, 1b\n" #loop back exactly once
	gpr_list.insert(idx,gpr) #add back the gpr
	return codestr

#*************************************
#5. generate jal, j
#*************************************
def gen_unconditional_jmp4():
	''' uncompressed unconditional jump '''
	codestr = ""
	jump_with_link = random.randint(0,1)
	loop_length = get_loop_count() #how many instructions to skip
	codestr += f"#Generating uncompressed jumps with max loop_length = {loop_length}\n"
	codestr += gen_arith_logical_instructions(random.randint(1,loop_length))
	if jump_with_link:
		codestr += "jal x1,	1f\n"
	else:
		codestr += "j	1f\n"
	codestr += gen_arith_logical_instructions(random.randint(1,loop_length))
	codestr += set_label("1") 
	return codestr

#*************************************
#5a. generate jal, j
#*************************************
def gen_unconditional_jmp4_only():
	''' uncompressed unconditional jump '''
	codestr = ""
	jump_with_link = random.randint(0,1)
	loop_length = get_loop_count() #how many instructions to skip
	codestr += f"#Generating uncompressed jumps \n"
	if jump_with_link:
		codestr += "jal x1,	1f\n"
	else:
		codestr += "j	1f\n"
	codestr += set_label("1") 
	return codestr

#*************************************
#5b. generate jalr
#*************************************
def gen_unconditional_jmp_chain():
	''' jalr unconditional jump chain '''
	codestr = ""
	codestr += f"#Generating chain of uncompressed jumps \n"
	chosen_reg = random.choice(gpr_list)
	length = random.randint(8,20)
	for i in range(length):
		codestr += f"la {chosen_reg}, 	1f\n"
		codestr += f"jalr {chosen_reg}, ({chosen_reg})\n"
		if random.randint(0,1):
			codestr += f"li {chosen_reg}, {i}\n" #dummy instruction
		codestr += set_label("1") 
	return codestr

#*************************************
#4. generate bgt/blt
#*************************************
def gen_backward_bgt_blt():
	''' backward bgt/bgtu/blt/bltu '''
	codestr = ""
	loop_length = get_loop_count() #how many instructions does the loop have?
	codestr += f"#Generating bgt/bgtu taken sequence with max loop_length = {loop_length}\n"
	signed   = random.randint(0,1)
	choose_bgt   = random.randint(0,1)
	mstr 	= ""
	istr 	= ""
	#only positive numbers here
	if not signed:
		rs1			 = random.choice(bcond_list)
		rs2 		 = rs1
		if choose_bgt:
			instr = random.choice(["bgt","bgtu"])
		else:
			instr = random.choice(["blt","bltu"])
		#ensure rs1 and rs2 are different
		while	rs2==rs1:
			rs2			 = random.choice(bcond_list)
	else:
		rs1			 = random.choice(gpr_list_negative)
		rs2 		 = rs1
		if choose_bgt:
			instr = "bgt"
		else:
			instr = "blt"
		#ensure rs1 and rs2 are different
		while	rs2==rs1:
			rs2			 = random.choice(gpr_list_negative)

	#swap rs1, rs2 to ensure branch is taken (prevent infinite loops)
	if choose_bgt and not signed:
		if(bcond_list.index(rs1) < bcond_list.index(rs2)):
			rs1, rs2 = rs2, rs1
		mstr += f"addi {rs1}, {rs1}, -1\n"
	elif choose_bgt and signed:
		if(gpr_list_negative.index(rs1) < gpr_list_negative.index(rs2)):
			rs1, rs2 = rs2, rs1
		mstr += f"addi {rs1}, {rs1}, -1\n"
	elif not choose_bgt and signed:
		if(gpr_list_negative.index(rs1) > gpr_list_negative.index(rs2)):
			rs1, rs2 = rs2, rs1
		mstr += f"addi {rs1}, {rs1}, 1\n"
	else: #less than, positive
		if(bcond_list.index(rs1) > bcond_list.index(rs2)):
			rs1, rs2 = rs2, rs1
		mstr += f"addi {rs1}, {rs1}, 1\n"

	rs1val	= gpr_values_init[rs1]
	rs2val	= gpr_values_init[rs2]
	codestr += f"li {rs1}, {rs1val}\n"
	codestr += f"li {rs2}, {rs2val}\n"
	codestr += set_label("1") 
	codestr += gen_arith_logical_instructions(random.randint(1,loop_length))
	if random.randint(0,1):
		codestr += set_label("1") #make it a shorter loop 50% of the time
	codestr += mstr
	codestr += f"{instr} {rs1}, {rs2}, 1b\n"
	return codestr

#*************************************
#3. generate beqz always not taken
#*************************************
def gen_beqz_not_taken():
	''' beqz always not taken '''
	codestr = ""
	loop_length = get_loop_count() #how many instructions does the loop have?
	rs1			 = random.choice(bcond_list)
	codestr += f"#Generating beqz not taken sequence with max loop_length = {loop_length}\n"
	codestr += set_label("1")
	codestr += gen_arith_logical_instructions(random.randint(1,loop_length))
	instr = "beqz"
	codestr += f"{instr} {rs1}, 1b\n"
	return codestr

#*************************************
#2. generate beqz always taken
#*************************************
def gen_beqz_always_taken_forward():
	''' beqz always taken forward '''
	codestr = ""
	loop_length = get_loop_count() #how many instructions does the loop have?
	codestr += f"#Generating beqz always taken (forward) sequence with max loop_length = {loop_length}\n"
	chosen_reg = random.choice(gpr_list)
	if random.randint(0,1):
		codestr += f"xor {chosen_reg}, {chosen_reg}, {chosen_reg}\n"
		codestr += f"beqz {chosen_reg}, 1f\n"
	else:
		codestr += f"beqz x0, 1f\n" #use x0 50% of the time
	codestr += gen_arith_logical_instructions(random.randint(1,loop_length))
	codestr += set_label("1")
	codestr += gen_arith_logical_instructions(random.randint(1,loop_length))
	return codestr

#*************************************
#2a. generate beqz only
#branches will split fetch group
#*************************************
def gen_beqz_chain_always_taken_forward():
	''' beqz always taken forward '''
	codestr = ""
	length = random.randint(8,20)
	codestr += f"#Generating beqz always taken (forward) chain length = {length}\n"
	chosen_reg = random.choice(gpr_list)
	for i in range(length):
		if random.randint(0,1):
			codestr += f"xor {chosen_reg}, {chosen_reg}, {chosen_reg}\n"
			codestr += f"beqz {chosen_reg}, 1f\n"
		else:
			codestr += f"beqz x0, 1f\n" #use x0 50% of the time
		codestr += set_label("1")
	return codestr

#*************************************
#1. generate bnez always taken
#*************************************
def gen_bnez_always_taken_backward():
	''' bnez always taken backward '''
	codestr = ""
	loop_length = get_loop_count() #how many instructions does the loop have?
	codestr += f"#Generating bnez always taken (backward) sequence with max loop_length = {loop_length}\n"
	chosen_reg = random.choice(gpr_list)
	rval	= random.randint(1,64)
	idx = gpr_list.index(chosen_reg)
	gpr = gpr_list.pop(idx) #pop the chosen loop count register from the gpr list
													#we don't want the gen_arith to pick this gpr
	codestr += f"li {chosen_reg}, {rval}\n"
	codestr += set_label("1")
	codestr += gen_arith_logical_instructions(random.randint(1,loop_length))
	codestr += f"addi {chosen_reg}, {chosen_reg}, -1\n"
	codestr += f"bnez {chosen_reg}, 1b\n"
	gpr_list.insert(idx,gpr) #add back the gpr
	return codestr

def start_test():
	'''
		jump to code1 segment via mret
	'''
	codestr = ""
	k = ".code1"
	if k in info_va:
		address = int(info_va[k]["base"],16)
	else:
		address = int(info[k]["base"],16)

	codestr += f"li x1, {hex(address)}\n"
	codestr += "csrw mepc, x1\n"
	return codestr

def jump_to_code_segment(k):
	codestr = ""
	#use va when specified
	if k in info_va:
		address = int(info_va[k]["base"],16)
	else:
		address = int(info[k]["base"],16)
	codestr += set_label("1") #need this label at the end of a code segment
														#eg: beqz x1, 1f (and if no local label for 1 was created)
	src = random.choice(["x1","x5"])
	dst = random.choice(["x0","x1","x5"])
	codestr += f"li {src}, {hex(address)}\n"
	codestr += f"jalr {dst}, ({src})\n"
	return codestr

def gen_call():
	'''
	 do a call to a return segment
	'''
	codestr = ""
	codestr += f"#Generating call/return sequence\n"
	#make sure we have return segments in the skeleton
	if ret_info and ret_info!=ret_info_exclude:
		#choose which return segment to call
		k = random.choice(list(ret_info))
		while k in ret_info_exclude:
			k = random.choice(list(ret_info))
			
		#use va when specified
		if k in info_va:
			address = int(info_va[k]["base"],16)
		else:
			address = int(info[k]["base"],16)
		codestr += set_label("1") 
		src = random.choice(["x1","x5"])
		dst = "x1"
		codestr += f"addi x2, x2, -8  #stack pointer\n" #stack pointer
		codestr += f"la {src}, 4f 	  #return address\n" #return address
		codestr += f"sw {src}, (x2)   #update stack pointer with return address\n" #update stack pointer with return address
		codestr += f"li {src}, {hex(address)}\n"
		codestr += f"jalr {dst}, ({src}) #call \n" #call
		codestr += set_label("4") 
		
	return codestr

def generate_code_sequences(this_segment,final_code_segment):
	codestr = ""
	sequence_dict = {
		"gen_backward_bgt_blt": 					  gen_backward_bgt_blt,
		#"gen_arith_logical_instructions":   gen_arith_logical_instructions,
		"gen_beqz_not_taken":								gen_beqz_not_taken,
		"gen_unconditional_jmp": 						gen_unconditional_jmp,
		"gen_unconditional_jmp4": 					gen_unconditional_jmp4,
		"gen_unconditional_jmp_chain":			gen_unconditional_jmp_chain,
		"gen_unconditional_jmp4_only":			gen_unconditional_jmp4_only,
		"gen_unconditional_jmp_backward_jcc": gen_unconditional_jmp_backward_jcc,
		"gen_beqz_always_taken_forward": 		gen_beqz_always_taken_forward,
		"gen_bnez_always_taken_backward": 	gen_bnez_always_taken_backward,
		"gen_cbnez_always_taken_backward": 	gen_cbnez_always_taken_backward,
		"gen_cbeqz_always_taken_forward":		gen_cbeqz_always_taken_forward,
		"gen_cbeqz_x8always_taken_forward": 	 gen_cbeqz_x8always_taken_forward,
		"gen_beqz_chain_always_taken_forward": gen_beqz_chain_always_taken_forward,
		"gen_loads_and_stores"						: gen_loads_and_stores,
		"gen_stlf"												:	gen_stlf,
		"gen_call"												: gen_call,
		"generate_icache_flush"						: generate_icache_flush,
	}
	num_seq = random.randint(1,len(sequence_dict)) 
	codestr+= f"1:\n"			#add this label at the beginning of the first sequence
												#this gives other sequences an option to not create a local label
												#so they can jump to ealier offsets
												#example:
												#generating seq1:
												#1:
												#<seq1_code>
												#<seq1_code>
												#<seq1_code>
												#generating seq2: (this sequence may or may not create a label)
												#<seq2_code>
												#<seq2_code>
												#<seq2_code> = beq 1b (this will jump to seq1 and then repeat)
	for i in range(num_seq):
		mkey = random.choice(list(sequence_dict.keys()))
		codestr+= f"##generating sequence {i}:\n"
		codestr += sequence_dict[mkey]() #call function
	final = (this_segment == final_code_segment)
	if final:
		codestr += set_label("1") #final sequence must have this label(just like the initial sequence)
		codestr += "finish_test\n"
	else:
		next_segment = this_segment + 1
		if random.uniform(0,1) < 0.3: #30% of the time visit older code segments
			addr_reg = random.choice(gpr_list)
			choose_reg = addr_reg
			while choose_reg==addr_reg:
				choose_reg = random.choice(gpr_list)
			codestr += f"li {addr_reg}, 0x2000\n" 
			codestr += f"lbu {choose_reg}, ({addr_reg})\n" #load [if non-zero visit older]
			codestr += f"beqz {choose_reg}, 3f\n"				  #cannot be 1f because jump_to_code_segment unconditionally puts a 1:
			codestr += f"sb x0, ({addr_reg})\n" 					#store [clear counter]
			codestr += jump_to_code_segment(".code"+str(1))
			codestr += set_label("3") 
		codestr += jump_to_code_segment(".code"+str(next_segment))
	return codestr

def gen_sequences(**kwargs):
	mstr, nopreamble = skeleton.get_skeleton(**kwargs) 
	info.clear()
	info_va.clear()
	ret_info.clear()
	ret_info_exclude.clear()

	for k,v in skeleton.segments.items():
		#instr_type = ["2B","4B","mixed"]
		instr_type = ["4B"]
		info[k]["base"] = v 
		info[k]["type"] = random.choice(instr_type) 
		if "ret" in k:
			ret_info.add(k)

	for k,v in skeleton.segments_va.items():
		#instr_type = ["2B","4B","mixed"]
		instr_type = ["4B"]
		info_va[k]["base"] = v #the virtual address  
		info_va[k]["type"] = random.choice(instr_type) 
		if "ret" in k:
			ret_info.add(k)

	#print(f"retinfo: {ret_info}")

	pattern = r"(code\d+_begin:\n)"
	pattern_setup = r"(test_setup:\n)"
	pattern_return = r"(ret\d+_begin:\n)"

	#generate_setup_code
	tstr = setup_gprs()
	if random.randint(0,1):
		tstr += setup_mfc0()
	if random.randint(0,1):
		tstr += setup_mfc1()
	tstr += start_test()
	mstr = re.sub(pattern_setup, r'\1'+tstr  ,mstr)

	#populate_return_segments
	matches = re.findall(pattern_return,mstr)
	final_return_segment = len(matches)
	for i in range(len(matches)):
		tpattern = "ret"+str(i+1)+"_begin:\n"
		tcode = generate_return_sequences(".ret"+str(i+1))
		mstr = re.sub(tpattern,tpattern+tcode,mstr)

	#generate_code_sequences
	matches = re.findall(pattern,mstr)
	final_code_segment = len(matches)
	for i in range(len(matches)):
		tpattern = "code"+str(i+1)+"_begin:\n"
		this_segment = i+1
		tcode = generate_code_sequences(this_segment,final_code_segment)
		mstr = re.sub(tpattern,tpattern+tcode,mstr)



	return mstr, nopreamble







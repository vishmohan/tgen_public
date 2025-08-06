#! /usr/bin/env python3

import helper

class l1btb:
	def __init__(self,mdict,count,fullpc):
		self.full_pc = fullpc
		self.howmany = count
		self.alias_list = []
		self.defines_dict = mdict

	#=================================================================
	def fix_address_hash_l1btb(self,new_pc,address_hash_old,address_hash_new):
	#=================================================================
		'''
			after the tag fixup sometimes index may not match.
			this routine fixes the address hash by manipulating lower bits 
			example [11:5]. These bits are chosen because these are not used
			for the tag has computation. Any change made to these bits
			will not affect the tag hash already computed
		'''
		ub	= int(self.defines_dict['RV_BTB_ADDR_HI'])
		lb  = int(self.defines_dict['RV_BTB_ADDR_LO'])
	
		diff = address_hash_old ^ address_hash_new #bit vector to indicate how many bits are different
		index = helper.extract_bits(new_pc,ub,lb)
		pos = 0
		index_list = list(index)
		mlen = len(index_list)
	
		#flip the bits that are a 1 in the bit vector
		while diff!=0:
			if diff&1 :
				mbit = index_list[mlen-1-pos]
				#flip bit
				newval = "0"
				if mbit=="0":
					newval="1"
				index_list[mlen-1-pos] = newval
			pos+=1
			diff=diff>>1
	
			index = ''.join(index_list)	
			
	
		modified_pc_part1 = helper.extract_bits(new_pc,63,(ub+1))
		modified_pc_part2 = index
		modified_pc_part3 = helper.extract_bits(new_pc,lb-1,0)
	
		return modified_pc_part1 + modified_pc_part2 + modified_pc_part3

	#=================================================================
	def compute_index_components_l1btb(self,orig_pc):
	#=================================================================
		'''
			returns the individual parts of pc used to compute address hash
		'''
		ub	= int(self.defines_dict['RV_BTB_ADDR_HI'])
		lb  = int(self.defines_dict['RV_BTB_ADDR_LO'])
		part1 = helper.extract_bits(orig_pc,ub,lb)
		btb_array_width = ub - lb
		btb_index2_lo = ub + 1
		btb_index2_hi = btb_index2_lo + btb_array_width 
		part2 = "0"*len(part1)
		btb_fold2_index = True if 'RV_BTB_FOLD2_INDEX_HASH' in self.defines_dict else False
		if not btb_fold2_index:
			part2 = helper.extract_bits(orig_pc,btb_index2_hi,btb_index2_lo)
		btb_index3_lo = btb_index2_hi + 1
		btb_index3_hi = btb_index3_lo + btb_array_width 
		part3 = helper.extract_bits(orig_pc,btb_index3_hi,btb_index3_lo)
		return part1,part2,part3

	#=================================================================
	def compute_addr_hash_l1btb(self,orig_pc):
	#=================================================================
		'''
			computes address hash (index) for l1btb 
		'''
		addr_hash = 0
		part1,part2,part3 = self.compute_index_components_l1btb(orig_pc)
		addr_hash = helper.compute_xor(part1,part2,part3) 
		return addr_hash

	#=================================================================
	def compute_tag_components_l1btb(self,orig_pc):
	#=================================================================
		'''
			returns the individual parts of pc used to compute tag hash
		'''
		btb_addr_hi	=  int(self.defines_dict['RV_BTB_ADDR_HI'])
		btb_addr_lo  = int(self.defines_dict['RV_BTB_ADDR_LO'])
		btb_tag_size = int(self.defines_dict['RV_BTB_BTAG_SIZE']) 
		ub = btb_addr_hi + 3*btb_tag_size
		lb = btb_addr_hi + 2*btb_tag_size + 1

		btb_btag_fold = True if 'RV_BTB_BTAG_FOLD' in self.defines_dict else False
		part1 = helper.extract_bits(orig_pc,ub,lb)
		if 	btb_btag_fold:
			part1 = "0" * len(part1)

		ub = btb_addr_hi + 2*btb_tag_size
		lb = btb_addr_hi + btb_tag_size + 1
		part2 = helper.extract_bits(orig_pc,ub,lb)

		ub = btb_addr_hi + btb_tag_size
		lb = btb_addr_hi + 1
		part3 = helper.extract_bits(orig_pc,ub,lb)
		return part1,part2,part3

	#=================================================================
	def compute_tag_hash_l1btb(self,orig_pc):
	#=================================================================
		'''
			computes tag hash for l1btb 
		'''
		tag_hash = 0
		part1,part2,part3 = self.compute_tag_components_l1btb(orig_pc)
		tag_hash = helper.compute_xor(part1,part2,part3) 
		return tag_hash

	#=================================================================
	def construct_new_pc_tag_l1btb(self,orig_pc,part1,part2,part3):
	#=================================================================
		'''
			construct new aliased pc with the provided  info
		'''
		btb_addr_hi	= int(self.defines_dict['RV_BTB_ADDR_HI'])
		btb_addr_lo  = int(self.defines_dict['RV_BTB_ADDR_LO'])
		btb_tag_size = int(self.defines_dict['RV_BTB_BTAG_SIZE'])
		ub = btb_addr_hi + 3*btb_tag_size
		pc_hi = helper.extract_bits(orig_pc,63,ub+1) #these bits uninvolved in tag computation
		lb = btb_addr_hi + 1
		pc_lo = helper.extract_bits(orig_pc,lb-1,0) 	#these bits uninvolved in tag computation
	
		pc1   = helper.extract_bits(helper.extend_pc(part1), btb_tag_size-1 ,0)
		pc2   = helper.extract_bits(helper.extend_pc(part2), btb_tag_size-1 ,0)
		pc3   = helper.extract_bits(helper.extend_pc(part3), btb_tag_size-1 ,0)
		pc_alias = pc_hi + f"{pc1}" + f"{pc2}" + f"{pc3}" + pc_lo
		return pc_alias

	#=================================================================
	def find_aliasing_pc_l1btb_tag(self,orig_pc,temp):
	#=================================================================
		'''
			find aliasing tags
		'''
		tag_hash = self.compute_tag_hash_l1btb(orig_pc)
		part1,part2,part3 = self.compute_tag_components_l1btb(orig_pc)
		temp_xor = int(part2,2) ^ int(part3,2)
		part2 = temp ^ temp_xor
		part3 = temp
		new_pc = self.construct_new_pc_tag_l1btb(orig_pc,int(part1,2),part2,part3)
		new_pc_alias = int(new_pc,2)
		return new_pc, new_pc_alias

	#=================================================================
	def find_aliasing_pc_l1btb(self):
	#=================================================================
		fullpc = self.full_pc
		for i in range(self.howmany):
			new_pc, new_pc_alias = self.find_aliasing_pc_l1btb_tag(fullpc,2*i)
			address_hash_old = self.compute_addr_hash_l1btb(fullpc)
			address_hash_new = self.compute_addr_hash_l1btb(new_pc)
			tag_hash_old = self.compute_tag_hash_l1btb(fullpc)

			#did the address hash change due to tag changes?
			if address_hash_old != address_hash_new:
				new_pc = self.fix_address_hash_l1btb(new_pc,address_hash_old,address_hash_new)
				new_pc_alias = int(new_pc,2) 
				address_hash_new = self.compute_addr_hash_l1btb(new_pc)
	
			self.alias_list.append(new_pc_alias)
			tag_hash_new = self.compute_tag_hash_l1btb(new_pc)
			assert(address_hash_old==address_hash_new) #make sure the index hash matches for new_pc and orig_pc
			assert(tag_hash_old==tag_hash_new) 				 #make sure the tag hash matches for new_pc and orig_pc

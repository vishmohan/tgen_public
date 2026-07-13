#! /usr/bin/env python3


MAGIC_MASK  = 0x4D035C09A360
MAGIC_MASK1 = 0x47fcdff701c0
PC_01 = 0x4D035C09A360
PC_02 = 0x47FCDFF701C0
PC_03 = 0x422B1E4DAE20
PC_04 = 0x42E28564F4A0
PC_05 = 0x470C5BB3B380
PC_06 = 0x464CE3B19900
PC_07 = 0x45D40F090620
PC_08 = 0x44CE370BFD40
PC_09 = 0x446A5F09D7C0
PC_10 = 0x40ED6B9E83A0
PC_11 = 0x4011839C24A0
PC_12 = 0x4B6AA26A2060
PC_13 = 0x4BAEC66846E0
PC_14 = 0x4A6BE2C619A0
PC_15 = 0x4B3EC22CC3C0
PC_16 = 0x4EF7CF780EE0

#several branch pcs that have the same btb_tag_hash and same btb_addr_hash
#these branch pcs can have different btb2 hashes (both tag and addr)

#btb has 4 ways and 8 banks => same btb_addr_hash, btb_tag_hash
#32 pcs to fill it up -> one of them will be overwritten
#overwritten branch is accessed again.
#btb will not report any valid branch, btb2 sill has it
#flush_f3
#btb2 wants to update the branch info into btb - btb2_mp_vld
#num_valids_f2/num_valids_f3 => flush_f3

#4B/2B branch -> 
#800125e8:	a801                	j	800125f8 --> btb2_mp_boffset = 0
#800125f6:	eb95                	bnez	a5,8001262a --> btb2_mp_boffset = 1

#btb2_mp_boffset ==> 1 if pc is on a 2b boundary but not on a 4b boundary

#python interpreter quick function
#hashf = lambda h: print(  hex( ((h>>5)&0x1f) ^ ((h>>10)&0x1f) ^ ((h>>15)&0x1f)) )
#thashf = lambda h: print(  hex( ((h>>36)&0x1fff) ^ ((h>>23)&0x1fff) ^ ((h>>10)&0x1fff)) )

#hashf_btb2 = lambda h: print(  hex( ((h>>5)&0x7f) ^ ((h>>12)&0x7f) ^ ((h>>19)&0x7f)) )
#thashf_btb2 = lambda h: print(  hex( ((h>>40)&0x3fff) ^ ((h>>26)&0x3fff) ^ ((h>>12)&0x3fff)) )

#==================================================
#alp5100: btb hashes are computed as follows
#btb_tag_hash = { (pc[48:36] ^ pc[35:23] ^ pc[22:10]) };
#btb_addr_hash = pc[9:5] ^ pc[14:10] ^ pc[19:15];
#==================================================
def generate_aliasing_pcs(base_pc, count=8):
    aliased_pcs = []
    
    for delta in range(1, count + 1):
        # Isolate the 13-bit delta mask
        mask = delta & 0x1FFF
        
        # Shift mask to align with pc[48:36] and pc[35:23]
        xor_mask = (mask << 36) | (mask << 23)
        
        # Apply the mask to the base PC
        aliased_pc = base_pc ^ xor_mask
        #aliased_pc = aliased_pc & MAGIC_MASK1 #use this to create common btb/btb2 aliases
        aliased_pcs.append(hex(aliased_pc))
        
    return aliased_pcs

#==================================================
#alp5100: btb2 hashes are computed as follows
#assign btb2_tag_hash = { (pc[53:40] ^ pc[39:26] ^ pc[25:12]) };
#alp5100:
#assign btb2_addr_hash[11:5] = pc[11:5] ^ pc[18:12] ^ pc[25:19];
#==================================================
def generate_btb2_aliasing_pcs(base_pc, count=8):
    aliased_pcs = []
    
    for delta in range(1, count + 1):
        # Isolate a unique 14-bit mask
        mask = delta & 0x3FFF
        
        # Shift mask to align perfectly with pc[53:40] and pc[39:26]
        xor_mask = (mask << 40) | (mask << 26)
        
        # Apply mask to create the collision
        aliased_pc = base_pc ^ xor_mask
        aliased_pcs.append(hex(aliased_pc))
        
    return aliased_pcs


base = 0x80012600
print(f"Base PC: {hex(base)}")
print("Aliased PCs:")
num = 1
for pc in generate_aliasing_pcs(base):
    print(f"Aliased btb pc {num}: {pc}")
    num += 1

#num = 1
#for pc in generate_btb2_aliasing_pcs(base):
#    print(f"Aliased btb2 pc {num}: hex({pc})")
#    num += 1


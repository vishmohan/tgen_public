mstr = '''
.equ pma, 0x7c0
.equ mtinst, 0x34a
.equ mtval2, 0x34b
.equ mfc0, 0x7f9
.equ mfc1, 0x7fa
.equ menvcfg, 0x30a
.equ mseccfg, 0x747

.equ pmpcfg0,   0x3a0
.equ pmpcfg2,   0x3a2

.equ pmpaddr0,  0x3b0
.equ pmpaddr1,  0x3b1
.equ pmpaddr2,  0x3b2
.equ pmpaddr3,  0x3b3
.equ pmpaddr4,  0x3b4
.equ pmpaddr5,  0x3b5
.equ pmpaddr6,  0x3b6
.equ pmpaddr7,  0x3b7
.equ pmpaddr8,  0x3b8
.equ pmpaddr9,  0x3b9
.equ pmpaddr10, 0x3ba
.equ pmpaddr11, 0x3bb
.equ pmpaddr12, 0x3bc
.equ pmpaddr13, 0x3bd
.equ pmpaddr14, 0x3be
.equ pmpaddr15, 0x3bf


.equ SV57_PAGING_MODE, 	0xA
.equ SV48_PAGING_MODE, 	0x9
.equ SV39_PAGING_MODE, 	0x8

.equ SATP_PPN, 	 				 0x140000 #4K aligned satp.ppn
.equ SATP_ASID,  			   0xffff
.equ VSATP_ASID, 				 0xfffe
.equ VSATP_PPN,  				 0x140008 #4K aligned vsatp.ppn
.equ SATP_MODE,  				 SV57_PAGING_MODE
.equ VSATP_MODE, 				 SV57_PAGING_MODE


.equ SATP_PPN_SV48, 	 	 0x140001 #4K aligned satp.ppn
.equ VSATP_PPN_SV48,  	 0x140009 #4K aligned vsatp.ppn
.equ VSATP_PPN1, 				 0x240000 #4K aligned vsatp.ppn

.equ HGATP_PPN, 	 			 0x140010 #16K aligned satp.ppn
.equ HGATP_PPN1, 				 0x340010
.equ HGATP_VMID,   			 1
.equ HGATP_MODE,   			 SV57_PAGING_MODE

.equ BIT_MISA_HEXT,			 	7
.equ BIT_MSTATUS_VS_LO,   9
.equ BIT_MSTATUS_VS_HI,  10
.equ BIT_MSTATUS_MPP_LO, 11
.equ BIT_MSTATUS_MPP_HI, 12
.equ BIT_MSTATUS_MPRV, 	 17
.equ BIT_MSTATUS_SUM, 	 18
.equ BIT_MSTATUS_MXR, 	 19
.equ BIT_MSTATUS_MPV, 	 39

.equ BIT_HSTATUS_SPV,		 	7
.equ BIT_HSTATUS_SPVP,	 	8
.equ BIT_HSTATUS_HU,	 	 	9

.equ BIT_SSTATUS_SPP,	 		8


.equ	BIT_MFC0_ICACHE_FLUSH, 19
.equ	BIT_MFC0_DISABLE_BPRED, 3

.equ	BIT_MFC1_ICACHE_WAYDISABLE_HI, 19
.equ	BIT_MFC1_ICACHE_WAYDISABLE_LO, 16
.equ  BIT_MFC1_BTBI_DISABLE_M, 				6
.equ  BIT_MFC1_RAS_DISABLE, 					5
.equ  BIT_MFC1_BTBI_DISABLE, 					4	
.equ  BIT_MFC1_NPC_DISABLE, 					3	
.equ  BIT_MFC1_ITTAGE_DISABLE, 				2	
.equ  BIT_MFC1_TAGE_DISABLE, 					1	
.equ  BIT_MFC1_PREFETCH_DISABLE, 		  0


.equ	BIT_MENVCFG_ADUE,  61
.equ	BIT_MENVCFG_PBMTE, 62

.equ    BIT_MML,        	0
.equ    BIT_MMWP, 				1
.equ    BIT_RLB,  				2

.equ ECALL_SMODE, 9

.equ	ILLEGAL_INSTRUCTION, 2
.equ	VIRTUAL_INSTRUCTION, 0x16

#=================================
#set ADUE
#clobbers x22
#=================================
.macro set_menvcfg_adue
	bseti	x22, x0, BIT_MENVCFG_ADUE
	csrs	menvcfg, x22
.endm

#=================================
#set PBMTE
#clobbers x22
#=================================
.macro set_menvcfg_pbmte
	bseti	x22, x0, BIT_MENVCFG_PBMTE
	csrs	menvcfg, x22
.endm

#=================================
#set ADUE
#clobbers x22
#=================================
.macro set_henvcfg_adue
	bseti	x22, x0, BIT_MENVCFG_ADUE
	csrs	henvcfg, x22
.endm

#=================================
#set PBMTE
#clobbers x22
#=================================
.macro set_henvcfg_pbmte
	bseti	x22, x0, BIT_MENVCFG_PBMTE
	csrs	henvcfg, x22
.endm


#==========================
#set mseccfg.mml
#==========================
.macro set_mseccfg_mml
  csrr  x22, mseccfg
  bseti   x22, x22, BIT_MML
  csrw    mseccfg, x22
.endm

#==========================
#clear mseccfg.mml
#==========================
.macro clear_mseccfg_mml
  csrr  x22, mseccfg
  bclri   x22, x22, BIT_MML
  csrw    mseccfg, x22
.endm

#==========================
#set mseccfg.rlb
#==========================
.macro set_mseccfg_rlb
  csrr  x22, mseccfg
  bseti   x22, x22, BIT_RLB
  csrw    mseccfg, x22
.endm

#==========================
#clear mseccfg.rlb
#==========================
.macro clear_mseccfg_rlb
  csrr  x22, mseccfg
  bclri   x22, x22, BIT_RLB
  csrw    mseccfg, x22
.endm


#=================================
#create leaf pte entry
#permissions = {v,r,w,x,u,g,a,d}
#               lsb           msb
#=================================
.macro make_leaf_pte_entry ppn permissions n pbmt
	.dword (\\n<<63|\pbmt<<61|\ppn<<10|\permissions)
.endm

#=================================
#create non-leaf pte entry
#permissions = {v,0,0,0,u,g,0,0}  
#              lsb  		  msb
#=================================
.macro make_nonleaf_pte_entry ppn permissions 
	.dword (\ppn<<10|\permissions)
.endm


#=================================
#update satp with specified value
#clobbers x22
#=================================
.macro write_satp ppn,asid,mode
	li x22, (\\mode <<60) | (\\asid<<44) | (\\ppn)
	csrw satp, x22
.endm

#=================================
#update vsatp with specified value
#clobbers x22
#=================================
.macro write_vsatp ppn,asid,mode
	li x22, (\\mode <<60) | (\\asid<<44) | (\\ppn)
	csrw vsatp, x22
.endm

#=================================
#update hgatp with specified value
#clobbers x22
#=================================
.macro write_hgatp ppn,vmid,mode
	li x22, (\\mode <<60) | (\\vmid<<44) | (\\ppn)
	csrw hgatp, x22
.endm


#=================================
#initialize specified pmp
#clobbers x22, x23, x24
#mode = 3 => NAPOT
#mode = 1 => TOR
#size in powers of 2
#=================================
.macro init_pmp num,base,size,mode,lock,permissions
	#for pmpbase
	li		x22, \\base 
	li 		x23, 1
	slli  x23, x23, \\size
	srli	x22, x22, 2 #base>>2
	srli	x23, x23, 3 #size>>3
	add	  x22, x22, x23
	addi  x22, x22, -1
	csrw	pmpaddr\\num, x22

	#for pmpcfg
	li		x22, \\lock
	slli  x22, x22, 7
	li 		x23, \\mode
	slli  x23, x23, 3
	or 		x22, x22, x23
	ori		x22, x22, \\permissions

	#which bits to update in pmpcfg0/2
	li		x23, \\num
	li		x24, 8
	remu	x23, x23, x24 #eg: if pmp9 then bits 15:8 => byte1
	slli	x23, x23, 3 #bit offset => eg: x23=8 for pmp9

	.if \\num > 7
		csrr	x24, pmpcfg2
	  sll 	x22, x22, x23	
		or		x22, x22, x24
		csrw	pmpcfg2, x22
	.else
		csrr	x24, pmpcfg0
	  sll 	x22, x22, x23	
		or		x22, x22, x24
		csrw	pmpcfg0, x22
	.endif
	
.endm

#=================================
#prepare entry to vs mode
#=================================
.macro prepare_for_vs_mode 

	#write sstatus.SPP for supervisor
	csrr x22, 		sstatus
	bseti x22, 		x22, BIT_SSTATUS_SPP
	csrw sstatus, x22

	#write hstatus.SPV
	csrr	x22, hstatus
	bseti x22, x22, BIT_HSTATUS_SPV
	csrw	hstatus, x22

.endm



.macro initialize_registers
	li x0,  0
	li x1,  0
	li x2,  0
	li x3,  0
	li x4,  0
	li x5,  0
	li x6,  0
	li x7,  0
	li x8,  0
	li x9,  0
	li x10, 0
	li x11, 0
	li x12, 0
	li x13, 0
	li x14, 0
	li x15, 0
	li x16, 0
	li x17, 0
	li x18, 0
	li x19, 0
	li x20, 0
	li x21, 0
	li x22, 0
	li x23, 0
	li x24, 0
	li x25, 0
	li x26, 0
	li x27, 0
	li x28, 0
	li x29, 0
	li x30, 0
	li x31, 0
.endm


.macro finish_test
	csrr	x5, sscratch
	c.jalr x5
.endm

'''

def get_preamble(**kwargs):
	return mstr


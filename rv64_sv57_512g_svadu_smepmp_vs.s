.global _start

#{.text.init:0x00000000}
.section .text.init
_start:
    initialize_registers
    bseti x1, x0, 31
	li	x1, 1
	slli x1, x1, 31
	ret				# expands to jalr  x0, (x1)
	

#{.text:0x80000000}
.section .text

test_begin:
	li		x13, 0xc0010000
	#setup mstatus to jump to virtual supervisor mode
	bseti	x1, x0, BIT_MSTATUS_MPP_LO
	bseti	x2, x1, BIT_MSTATUS_MPP_HI
	csrc	mstatus, x2
	bseti x1, x1, BIT_MSTATUS_MPV
	csrs	mstatus, x1 #mstatus.MPP = 2'b01

	#update mepc with pc = 0x200000
	bseti 	x2, x0, 21
	csrw	mepc, x2

	#update vsscratch with return pc
	la		x2, _pass
	csrw	vsscratch, x2

	#set up mtvec
	la   x2, _hndlr
	csrw mtvec, x2

	#set rlb 
	set_mseccfg_rlb 

	#init_pmp num,base,size,mode,lock,permissions
	init_pmp 3,  0x80000000, 12, 3, 1, 0x4 	 #2G 		--> 4k L=1 X=1
	init_pmp 2,  0xc0000000, 12, 3, 1, 0x3 	 #3G 		--> 4k M mode locked r/w region mail box addr


	set_mseccfg_mml

	csrr x22, mseccfg

	init_pmp 15, 0x2000,			12,  3, 0, 0x6    #0x2000 --> shared r/w region M/S mode
	init_pmp 14, 0x140000000, 30,  3, 0, 0x3    #5G     --> S mode R/W pagetables

	init_pmp 10, 0x200000,    12,  3, 0, 0x4    #0x200000 4k S mode execute only
	init_pmp 11, 0x201000,    12,  3, 1, 0x4    #0x201000 4k M mode execute only
	init_pmp 12, 0x202000,    12,  3, 0, 0x5    #0x202000 4k S mode read/execute only
	init_pmp 13, 0x203000,    12,  3, 1, 0x4    #0x203000 4k M mode execute only
	init_pmp  9, 0x204000,    12,  3, 0, 0x7    #0x204000 4k S mode read/write/execute only
	init_pmp  8, 0x205000,    12,  3, 1, 0x4    #0x205000 4k M mode execute only
	init_pmp  7, 0x206000,    12,  3, 0, 0x4    #0x206000 4k S mode execute only
	init_pmp  6, 0x207000,    12,  3, 1, 0x4    #0x207000 4k M mode execute only
	init_pmp  5, 0x208000,    12,  3, 0, 0x4    #0x208000 4k S mode execute only

	init_pmp  4,  0x400000,    21,  3, 1, 0x2    #0x400000 2M M/S/U mode execute only
	init_pmp  0,  0x80000000, 12, 3, 1, 0x6 	  #2G 		--> 4k execute S/U , read/execute M mode
	init_pmp  1,  0xc0000000, 30, 3, 0, 0x6 	  #3G 		--> 1G r/w region mail box addr M/S/U mode

	#initialize pma
	li		x22, 0x5555555559 									 #region1 is nonspec
	csrw	pma, x22

	#update satp
	write_satp	SATP_PPN, SATP_ASID, SV57_PAGING_MODE

	#update vsatp
	write_vsatp	VSATP_PPN, VSATP_ASID, SV57_PAGING_MODE

	#update hgatp
	write_hgatp	HGATP_PPN, HGATP_VMID, SV57_PAGING_MODE

#register initialization goes here
test_setup:


	set_menvcfg_adue #menvcfg[adue]=1
	set_menvcfg_pbmte #menvcfg[pbmte] = 1

	set_henvcfg_adue #henvcfg[adue]=1
	set_henvcfg_pbmte #henvcfg[pbmte] = 1

	mret #goto 0x200000
	j _fail

_pass:
    li      t0, 0xd0580000
    addi    t1, x0, 0xff
    sb      t1, 0(t0)
    fence.i
    beq     x0, x0, _pass
_fail:
    li      t0, 0xd0580000
    addi    t1, x0, 0xff
    sb      t1, 0(t0)
    fence.i
    beq     x0, x0, _fail
.align 4
_hndlr:
	csrr x1, mcause
	csrr x1, mtval
	lui  x2, 1 
	add  x1, x1, x2
	csrw mepc, x1 #try the next 4kpage
	mret

#{.code1:0x200000}
.section .code1 , "aw"
code1_begin:

#{.code2:0x201000}
.section .code2 , "aw"
code2_begin:


#{.code3:0x202000}
.section .code3 , "aw"
code3_begin:


#{.code4:0x203000}
.section .code4 , "aw"
code4_begin:



#{.code5:0x204000}
.section .code5 , "aw"
code5_begin:


#{.code6:0x205000}
.section .code6 , "aw"
code6_begin:

#{.code7:0x206000}
.section .code7 , "aw"
code7_begin:

#{.code8:0x207000}
.section .code8 , "aw"
code8_begin:

#{.code9:0x208000}
.section .code9 , "aw"
code9_begin:


#{.code10:0x400000}
.section .code10 , "aw"
code10_begin:

#{.mdata:0x2000}
#{.mdata:0x2000:0x2000}
.section .mdata , "aw"
mdata_begin:
.set dat, 1
.rept 4096
	.hword dat
	.set 	dat, dat+1
.endr	





#hs page tables

#{.ptl5:0x140000000}
.section .ptl5, "aw"
	make_nonleaf_pte_entry 0x140001 0x1

#{.ptl4:0x140001000}
.section .ptl4, "aw"
	make_nonleaf_pte_entry 0x140002 0x1

#{.ptl3:0x140002000}
.section .ptl3, "aw"
	make_nonleaf_pte_entry 0x140003 0x1
	make_nonleaf_pte_entry 0x140003 0x1
	make_leaf_pte_entry (2<<30)>>12 0xcf 0 0
	make_leaf_pte_entry (3<<30)>>12 0xcf 0 0
	make_nonleaf_pte_entry 0x140003 0x1

#{.ptl2:0x140003000}
.section .ptl2, "aw"
	make_nonleaf_pte_entry 0x140004 0x1
	make_nonleaf_pte_entry 0x140005 0x1
	make_nonleaf_pte_entry 0x140006 0x1
	make_nonleaf_pte_entry 0x140007 0x1

#{.ptl1:0x140004000}
.section .ptl1, "aw"
	.set ppn, 1<<35|1<<21 
	.set idx, 0
	.rept 512
		.set ppn_mod, ppn|idx<<12
		make_leaf_pte_entry ppn_mod>>12 0x0f 0 0
		.set idx, idx+1
	.endr

#{.ptl1_1:0x140005000}
.section .ptl1_1, "aw"
	.set ppn, 2<<21 
	.set idx, 0
	.rept 512
		.set ppn_mod, ppn|idx<<12
		make_leaf_pte_entry ppn_mod>>12 0x0f 0 0
		.set idx, idx+1
	.endr

#{.ptl1_2:0x140006000}
.section .ptl1_2, "aw"
	.set ppn, 1<<35|3<<21 
	.set idx, 0
	.rept 512
		.set ppn_mod, ppn|idx<<12
		make_leaf_pte_entry ppn_mod>>12 0x0f 0 0
		.set idx, idx+1
	.endr

#{.ptl1_3:0x140007000}
.section .ptl1_3, "aw"
	.set ppn, 4<<21 
	.set idx, 0
	.rept 512
		.set ppn_mod, ppn|idx<<12
		make_leaf_pte_entry ppn_mod>>12 0x0f 0 0
		.set idx, idx+1
	.endr



#vs page tables

#{.vptl5:0x140008000}
.section .vptl5, "aw"
	make_nonleaf_pte_entry 0x140009 0x1

#{.vptl4:0x140009000}
.section .vptl4, "aw"
	make_nonleaf_pte_entry 0x14000A 0x1

#{.vptl3:0x14000A000}
.section .vptl3, "aw"
	make_nonleaf_pte_entry 0x14000B 0x1
	make_nonleaf_pte_entry 0x14000B 0x1
	make_leaf_pte_entry (2<<30)>>12 0xcf 0 0
	make_leaf_pte_entry (3<<30)>>12 0xcf 0 0
	make_nonleaf_pte_entry 0x14000B 0x1

#{.vptl2:0x14000B000}
.section .vptl2, "aw"
	make_nonleaf_pte_entry 0x14000C 0x1
	make_nonleaf_pte_entry 0x14000D 0x1
	make_nonleaf_pte_entry 0x14000E 0x1
	make_nonleaf_pte_entry 0x14000F 0x1

#{.vptl1:0x14000C000}
.section .vptl1, "aw"
	.set ppn, 0 
	.set idx, 0
	.rept 512
		.set ppn_mod, idx<<12
			make_leaf_pte_entry idx 0x0f 0 0
		.set idx, idx+1
	.endr

#{.vptl1_1:0x14000D000}
.section .vptl1_1, "aw"
	.set ppn, 1<<21 
	.set idx, 0
	.rept 512
		.set ppn_mod, ppn|idx<<12
		make_leaf_pte_entry ppn_mod>>12 0x0f 0 0
		.set idx, idx+1
	.endr

#{.vptl1_2:0x14000E000}
.section .vptl1_2, "aw"
	.set ppn, 2<<21 
	.set idx, 0
	.rept 512
		.set ppn_mod, ppn|idx<<12
		make_leaf_pte_entry ppn_mod>>12 0x0f 0 0
		.set idx, idx+1
	.endr

#{.vptl1_3:0x14000F000}
.section .vptl1_3, "aw"
	.set ppn, 3<<21 
	.set idx, 0
	.rept 512
		.set ppn_mod, ppn|idx<<12
		make_leaf_pte_entry ppn_mod>>12 0x0f 0 0
		.set idx, idx+1
	.endr


#gstage page tables

#{.hptl5:0x140010000}
.section .hptl5, "aw"
	.rept 512
		make_nonleaf_pte_entry 0x140020 0x01 
	.endr

#{.hptl4:0x140020000}
.section .hptl4, "aw"
	.rept 512
		make_nonleaf_pte_entry 0x140021 0x01 
	.endr

#{.hptl3:0x140021000}
.section .hptl3, "aw"
	.set ppn, 0
	.set idx, 0
	.rept 512
		make_leaf_pte_entry (ppn<<30)>>12 0x1f 0 0
		.set idx, idx+1
		.set ppn, ppn+1
	.endr

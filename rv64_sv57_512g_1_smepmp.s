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
	#setup mstatus to jump to supervisor mode
	bseti	x1, x0, BIT_MSTATUS_MPP_LO
	bseti	x2, x1, BIT_MSTATUS_MPP_HI
	csrc	mstatus, x2
	csrs	mstatus, x1 #mstatus.MPP = 2'b01

	#update mepc with pc = 0x200000
	bseti 	x2, x0, 21
	csrw	mepc, x2

	#update sscratch with return pc
	la		x2, _pass
	csrw	sscratch, x2

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
	init_pmp 14, 0x140000000, 13,  3, 0, 0x3    #5G     --> S mode R/W pagetables

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
	li		x22, 0x5555555555
	csrw	pma, x22

	#update satp
	write_satp	SATP_PPN, SATP_ASID, SV57_PAGING_MODE


	#load from 0x2000 - pmp15 ok
	lui x22, 0x2
	ld  x23, (x22)

#register initialization goes here
test_setup:

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

#{.ptl5:0x140000000}
.section .ptl5, "aw"
	make_nonleaf_pte_entry 0x140001 0x21


#{.ptl4:0x140001000}
.section .ptl4, "aw"
	.set ppn3, 0
	.rept 10
		make_leaf_pte_entry (ppn3<<39)>>12 0xcf 0 0
		.set ppn3, ppn3+1
	.endr

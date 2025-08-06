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

	#initialize pmp0
	li		x22, 0
	li		x23, 64<<30
	srli	x22, x22, 2 #base>>2
	srli	x23, x23, 3 #size>>3
	add	    x22, x22, x23
	addi    x22, x22, -1
	csrw	pmpaddr0, x22
	li		x22, 0x1f
	csrw	pmpcfg0, x22

	#initialize pma
	li		x22, 0x5555555559 #region1 is nonspec
	csrw	pma, x22

	#update satp
	write_satp	SATP_PPN, SATP_ASID, SV57_PAGING_MODE

#register initialization goes here
test_setup:


	set_menvcfg_adue #menvcfg[adue]=1
	set_menvcfg_pbmte #menvcfg[pbmte] = 1

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

#{.code1:0x100000000:0x800200000}
.section .code1 , "aw"
code1_begin:
#{.code2:0x100200000:0x400000}
.section .code2 , "aw"
code2_begin:
#{.code3:0x100400000:0x800600000}
.section .code3 , "aw"
code3_begin:
#{.code4:0x100600000:0x800000}
.section .code4 , "aw"
code4_begin:


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






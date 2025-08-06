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
	li		x22, 0x5555555555
	csrw	pma, x22

	#update satp
	write_satp	SATP_PPN, SATP_ASID, SV57_PAGING_MODE

#register initialization goes here
test_setup:

	mret 
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

#{.code1:0x200000}
.section .code1 , "aw"
code1_begin:

#{.code2:0x7821e3c0}
.section .code2 , "aw"
code2_begin:


#{.code3:0x7021c380}
.section .code3 , "aw"
code3_begin:

#{.code4:0x6821a340}
.section .code4 , "aw"
code4_begin:

#{.code5:0x60218300}
.section .code5 , "aw"
code5_begin:

#{.code6:0x582162c0}
.section .code6 , "aw"
code6_begin:

#{.code7:0x50214280}
.section .code7 , "aw"
code7_begin:

#{.code8:0x48212240}
.section .code8 , "aw"
code8_begin:


#{.ret1:0x40210200}
.section .ret1 , "aw"
ret1_begin:

#{.ret2:0x3820e1c0}
.section .ret2 , "aw"
ret2_begin:

#{.ret3:0x3020c180}
.section .ret3 , "aw"
ret3_begin:

#{.ret4:0x2820a140}
.section .ret4 , "aw"
ret4_begin:


#{.ret5:0x20208100}
.section .ret5 , "aw"
ret5_begin:

#{.ret6:0x182060c0}
.section .ret6 , "aw"
ret6_begin:

#{.ret7:0xe0238700}
.section .ret7 , "aw"
ret7_begin:

#{.ret8:0x8202000}
.section .ret8 , "aw"
ret8_begin:

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

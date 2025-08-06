#==========================================================
#BTB2 hashes:
#btb2 tag hash = pc[53:40]^pc[39:26]^pc[25:12]
#btb2 address hash = pc[11:4]^pc[19:12]^pc[27:20]
#BTB hashes:
#btb tag hash = 		pc[48:36] ^ pc[35:23]^pc[22:10]
#btb address hash = pc[9:5]^ pc[14:10] ^ pc[19:15]
#============================================================
.global _start

#{.text.init:0x00000000}
.section .text.init
_start:
    initialize_registers
    bseti x1, x0, 30	#we return from pc_a segment here
		ret				# expands to jalr  x0, (x1)
	

#{.text:0x40000000}
.section .text

test_begin:
	li		x13, 0xc0010000
	#setup mstatus to jump to supervisor mode
	bseti	x1, x0, BIT_MSTATUS_MPP_LO
	bseti	x2, x1, BIT_MSTATUS_MPP_HI
	csrc	mstatus, x2
	csrs	mstatus, x1 #mstatus.MPP = 2'b01

	#update mepc 
	li			x1,	0x8c000
	csrw	mepc, x1			

	#no delegation
	csrw medeleg, x0

	#update sscratch with return pc
	la		x2, _pass
	csrw	sscratch, x2

	#update mtvec
	la    x2, _handler
	csrw mtvec, x2

	#initialize pmp0
	li		x22, 0
	li		x23, 256<<30
	srli	x22, x22, 2 #base>>2
	srli	x23, x23, 3 #size>>3
	add	  x22, x22, x23
	addi  x22, x22, -1
	csrw	pmpaddr0, x22
	li		x22, 0x1f
	csrw	pmpcfg0, x22

	#initialize pma
	li		x22, 0x5555555555
	csrw	pma, x22

	#update satp
	#write_satp	SATP_PPN, SATP_ASID, SV57_PAGING_MODE
	li x15, 8 #counter for pc_x
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
.align 4
_handler:
		csrr		x1, mcause
		csrr		x1, mepc
		csrr		x1, mtval
		csrr		x1, mtval2
		csrr		x1, mtinst
		csrr	  x1, sscratch
		ret


#{.code1:0x8c000}
.section .code1 , "aw"
code1_begin:

#{.code2:0x118000000}
.section .code2 , "aw"
code2_begin:

#{.code3:0x119000800}
.section .code3 , "aw"
code3_begin:

#{.code4:0x11a001000}
.section .code4 , "aw"
code4_begin:

#{.code5:0x11a801400}
.section .code5 , "aw"
code5_begin:

#{.code6:0x11b001800}
.section .code6 , "aw"
code6_begin:


#{.mdata:0x2000}
.section .mdata , "aw"
mdata_begin:
.set dat, 1
.rept 4096
	.hword dat
	.set 	dat, dat+1
.endr	











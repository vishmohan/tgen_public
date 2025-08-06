.equ PC_X, (1<<35)

.global _start

#{.text.init:0x00000000}
.section .text.init
_start:
    initialize_registers
    bseti x1, x0, 30
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
	li			x1,	PC_X
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
	write_satp	SATP_PPN, SATP_ASID, SV57_PAGING_MODE
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
		csrr	  x1, sscratch
		ret
		mret

#{.code1:0x800000000}
#{.code1:0x800000000:0x800000000}
.section .code1 , "aw"
code1_begin:

#{.code2:0x1800000000}
#{.code2:0x2000800000000:0x1800000000}
.section .code2 , "aw"
code2_begin:

#{.code3:0x2800000000}
#{.code3:0x40000800000000:0x2800000000}
.section .code3 , "aw"
code3_begin:
	


#{.mdata:0x2000}
.section .mdata , "aw"
mdata_begin:
.set dat, 1
.rept 4096
	.hword dat
	.set 	dat, dat+1
.endr	




#{.ptl5:0x140000000}
.section .ptl5, "aw"
		make_nonleaf_pte_entry 0x140001 0x21  			#for pc_x, pc_y, pc_z
		.dword 0
		#make_leaf_pte_entry (0x60<<30)>>12 0xcf 0 0 #for pc_z 256t unsupported?
		make_nonleaf_pte_entry 0x140005 0x21  			#for pc_z
		.rept 61
			.dword 0
		.endr
		make_nonleaf_pte_entry 0x140003 0x21  			#for pc_a

#{.ptl4:0x140001000}
.section .ptl4, "aw"
		make_nonleaf_pte_entry 0x140002 0x21
		.dword 0
		#make_nonleaf_pte_entry 0x140002 0x21
		

#{.ptl3:0x140002000}
.section .ptl3, "aw"
	.set ppn2, 0
	.rept 512
		.if ppn2==288
			make_leaf_pte_entry (0x60<<30)>>12 0xcf 0 0
		.else
			make_leaf_pte_entry (ppn2<<30)>>12 0xcf 0 0
		.endif
		.set ppn2, ppn2+1
	.endr

#{.ptl4_1:0x140003000}
.section .ptl4_1, "aw"
		make_nonleaf_pte_entry 0x140004 0x21 #pc_a

#{.ptl3_1:0x140004000}
.section .ptl3_1, "aw"
	.rept 512
		make_leaf_pte_entry (0xA0<<30)>>12 0xcf 0 0 #pc_a 
	.endr

#{.ptl4_2:0x140005000}
.section .ptl4_2, "aw"
		make_nonleaf_pte_entry 0x140006 0x21 #pc_z

#{.ptl3_2:0x140006000}
.section .ptl3_2, "aw"
	.rept 512
		make_leaf_pte_entry (0x60<<30)>>12 0xcf 0 0 #pc_x 
	.endr







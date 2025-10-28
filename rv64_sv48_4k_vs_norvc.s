.option norvc

.equ	guest_code_begin, 		0x200000
.equ	supervisor_code_begin, 0x800000000

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
	bseti	x1, x1, BIT_MSTATUS_MPV 
	csrs	mstatus, x1 #mstatus.MPP = 2'b01 , MPV=1

	#update mepc 
	li			x1,	supervisor_code_begin
	csrw	mepc, x1			

	write_vsatp	VSATP_PPN1, VSATP_ASID, SV48_PAGING_MODE
	write_hgatp	HGATP_PPN1, HGATP_VMID, SV48_PAGING_MODE

	#no delegation
	csrw medeleg, x0

	#update vsscratch with return pc
	la		x2, _pass
	csrw	vsscratch, x2

	#update mtvec
	la    x2, _handler
	csrw mtvec, x2

	#update stvec
	la    x2, _handler_s
	csrw stvec, x2

	#update vstvec
	la    x2, _handler_vs
	csrw vstvec, x2

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
	#write_satp	SATP_PPN, SATP_ASID, SV48_PAGING_MODE

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
.align 4
_handler_s:
_handler_vs:
		csrr		x1, scause
		csrr		x1, sepc
		csrr		x1, stval
		csrr		x1, htinst
		csrr		x1, htval
		csrr	  x1, sscratch
		ret



#{.code0:0x800000000:0x800000000}
#.section .code0 , "aw"
#	li	x31, 8
#	1:
#	.rept 8
#		addi x1, x31, 1
#		slli	x1, x1, 1
#	.endr
#		addi x31, x31, -1
#		bnez x31,1b
#
#	prepare_for_vs_mode
#	li	x12, guest_code_begin
#	csrw sepc, x12 #set up guest pc
#	write_vsatp	VSATP_PPN1, VSATP_ASID, SV48_PAGING_MODE
#	write_hgatp	HGATP_PPN1, HGATP_VMID, SV48_PAGING_MODE
#	sret

#{.code1:0x200000:0x200000}
.section .code1 , "aw"
guest_code_begin:
code1_begin:

#{.code2:0x402000:0x8202000}
.section .code2 , "aw"
code2_begin:

#{.code3:0x204000:0x204000}
.section .code3 , "aw"
code3_begin:
	



#{.mdata:0x2000}
.section .mdata , "aw"
mdata_begin:
.set dat, 1
.rept 512
	.dword dat
	.set 	dat, dat+1
.endr	




#Not used in this test
#{.ptl5:0x140000000}
.section .ptl5, "aw"
		make_nonleaf_pte_entry 0x140001 0x21  			

#{.ptl4:0x140001000}
.section .ptl4, "aw"
		make_nonleaf_pte_entry 0x140002 0x21

#{.ptl3:0x140002000}
.section .ptl3, "aw"
	.set ppn2, 0
	.rept 512
			make_leaf_pte_entry (ppn2<<30)>>12 0xcf 0 0
		.set ppn2, ppn2+1
	.endr

#vsatp.mode = sv48
#{.vptl4: 0x240000000}
.section .vptl4, "aw"
		.rept 512
		 make_nonleaf_pte_entry 0x240001 0x21
		.endr

#{.vptl3: 0x240001000}
.section .vptl3, "aw"
		make_nonleaf_pte_entry 0x240002 0x21  			
		.set idx, 1
		.rept 511
			make_leaf_pte_entry (idx<<30)>>12 0xcf 0 0
		  .set idx, idx+1
		.endr

#{.vptl2: 0x240002000}
.section .vptl2, "aw"
			make_nonleaf_pte_entry 0x240003 0x21  			
			make_nonleaf_pte_entry 0x240004 0x21  			
				.set ppn, 2
			.rept 510
				make_leaf_pte_entry (ppn<<21)>>12 0xcf 0 0 #va = 0x400000 -> gpa = 0x400000
				.set ppn, ppn+1
			.endr

#{.vptl1: 0x240003000}
.section .vptl1, "aw"
			.set idx, 0
			.rept 512
				make_leaf_pte_entry (idx<<12)>>12 0xcf 0 0
				.set idx, idx+1
			.endr

#{.vptl1_1: 0x240004000}
.section .vptl1_1, "aw"
			.set ppn, 1
			.set idx, 0
			.rept 512
				make_leaf_pte_entry (ppn<<21|idx<<12)>>12 0xcf 0 0
				.set idx, idx+1
			.endr


#hgatp.mode = sv48
#{.hptl4: 0x340010000}
.section .hptl4, "aw"
	make_nonleaf_pte_entry 0x340002 0x21


#{.hptl3: 0x340002000}
.section .hptl3, "aw"
	make_nonleaf_pte_entry 0x340003 0x21
	.set ppn,1
	.rept 511
		make_leaf_pte_entry (ppn<<30)>>12 0xdf 0 0
		.set ppn, ppn+1
	.endr


#{.hptl2: 0x340003000}
.section .hptl2, "aw"
	.set idx, 65
	make_nonleaf_pte_entry 0x340004 0x21
	make_nonleaf_pte_entry 0x340005 0x21
	make_leaf_pte_entry (idx<<21)>>12 0xdf 0 0 #gpa = 0x400000 -> spa=0x8200000


#{.hptl1: 0x340004000}
.section .hptl1, "aw"
	.set ppn, 0
	.rept 512
		make_leaf_pte_entry (ppn<<12)>>12 0xdf 0 0
		.set ppn, ppn+1
	.endr

#{.hptl1_1: 0x340005000}
.section .hptl1_1, "aw"
	.set ppn, 1
	.set idx, 0
	.rept 512
		make_leaf_pte_entry (ppn<<21|idx<<12)>>12 0xdf 0 0
		.set idx, idx+1
	.endr

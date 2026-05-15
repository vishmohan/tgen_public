.equ	guest_code_begin, 		 0x200000
.equ	supervisor_code_begin, 0x800000000


.equ t0_code, 0x4D035C09A360
.equ t1_code, 0x47FCDFF701C0
.equ t2_code, 0x422B1E4DAE20
.equ t3_code, 0x42E28564F4A0

.equ PC_01, 0x4D035C09A360
.equ PC_02, 0x47FCDFF701C0
.equ PC_03, 0x422B1E4DAE20
.equ PC_04, 0x42E28564F4A0
.equ PC_05, 0x470C5BB3B380
.equ PC_06, 0x464CE3B19900
.equ PC_07, 0x45D40F090620
.equ PC_08, 0x44CE370BFD40
.equ PC_09, 0x446A5F09D7C0
.equ PC_10, 0x40ED6B9E83A0
.equ PC_11, 0x4011839C24A0
.equ PC_12, 0x4B6AA26A2060
.equ PC_13, 0x4BAEC66846E0
.equ PC_14, 0x4A6BE2C619A0
.equ PC_15, 0x4B3EC22CC3C0
.equ PC_16, 0x4EF7CF780EE0



#=====================================
#macro for the vector sequence
#=====================================
.macro do_vector_sequence_b5489 num
	lui		x12, 3
	lui		x1,  2
	.rept \num 
		li		x14, 2
		j			1f
		2:
		.rept 15
			nop
		.endr
		3:
		.rept 15
			nop
		.endr
	1:
	.rept 2
		vadd.vi		v0, v0, 1
		vse8.v		v0, (x1)
		vle8.v		v1, (x1)
		vadd.vi		v1, v1, 1
		vse8.v		v1, (x12)
		vle8.v		v0, (x12)
	.endr
		addi x14, x14, -1
		bgtz x14, 2b
		beqz x14, 3b
	.endr
.endm
#=====================================

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
	set_menvcfg_pbmte

	li		x13, 0xc0010000

	#setup mstatus to jump to supervisor mode
	bseti	x1, x0, BIT_MSTATUS_MPP_LO
	bseti	x2, x1, BIT_MSTATUS_MPP_HI
	bseti x2, x2, BIT_MSTATUS_VS_LO  #bit9  vector status
	bseti x2, x2, BIT_MSTATUS_VS_HI  #bit10 vector status
	csrc	mstatus, x2	#clear MPP and VS vector registers OFF
	#bseti	x1, x1, BIT_MSTATUS_MPV 
	bseti	x1, x1, BIT_MSTATUS_VS_LO	 #vector registers in init status
	csrs	mstatus, x1 #mstatus.MPP = 2'b01 , VS=2'b01

	#configure vector parameters
	vsetvli	x22, x30, e8, m1, ta, ma  #x30 = (AVL) 256


	#update mepc 
	li			x1,	supervisor_code_begin
	csrw	mepc, x1		#meaningless - tgen will setup correct value(code1)	

	write_vsatp	VSATP_PPN1, VSATP_ASID, SV48_PAGING_MODE
	write_satp	VSATP_PPN1, VSATP_ASID, SV48_PAGING_MODE
	#write_hgatp	HGATP_PPN1, HGATP_VMID, SV48_PAGING_MODE

	#medeleg[9] = 1 ecall 
	#ecall handler uncacheable via pbmt
	csrw medeleg, x0
	li   x2, 1
	slli x2, x2, ECALL_SMODE
	csrrs x1, medeleg, x2

	#update sscratch with return pc
	la		x2, _pass
	csrw	sscratch, x2

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
	init_pmp 0, 0, 39, 3, 0, 7

	#initialize pma
	li		x22, 0x5555555555
	csrw	pma, x22

	#update satp
	#write_satp	SATP_PPN, SATP_ASID, SV48_PAGING_MODE

#register initialization goes here
test_setup:
	csrr x1, mhartid
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
		csrr    x1, sepc
		addi    x1, x1, 4
		csrw    sepc, x1
		sret
		csrr	  x1, sscratch
		ret



#{.code1:0x4D035C09A360:0x35C09A360}
.section .code1 , "aw"
guest_code_begin:
	li		x12, 1
	beq   x1, x12, continue_test_t1
	li		x12, 2
	beq   x1, x12, continue_test_t2
	li		x12, 3
	beq   x1, x12, continue_test_t3
	j			continue_test_t0 #default is t0 (if x1 is corrupted)	

continue_test_t3:
	li		x12, t3_code
	jalr x12, (x12) 
	
continue_test_t1:
	do_vector_sequence_b5489 32
	li	x1, t1_code
	ret #jump to code2

continue_test_t2:
	do_vector_sequence_b5489 32
	li x1, 0x2001200000
	ret #jump to code3

continue_test_t0:
	#do_vector_sequence_b5489 32
code1_begin:


#{.code2:0x47FCDFF701C0:0x7CDFF701C0}
.section .code2 , "aw"
code2_begin:

#{.code3:0x422B1E4DAE20:0x2B1E4DAE20}
.section .code3 , "aw"
code3_begin:

#{.code4:0x42E28564F4A0:0x628564F4A0}
.section .code4 , "aw"
code4_begin:

#{.code5:0x470C5BB3B380:0xC5BB3B380}
.section .code5 , "aw"
code5_begin:

#{.code6:0x464CE3B19900:0x4CE3B19900}
.section .code6 , "aw"
code6_begin:

#{.code7:0x45D40F090620:0x540F090620}
.section .code7 , "aw"
code7_begin:

#{.code8:0x44CE370BFD40:0x4E370BFD40}
.section .code8 , "aw"
code8_begin:


#{.code9:0x446A5F09D7C0:0x6A5F09D7C0}
.section .code9 , "aw"
	.rept 8
		ecall
	.endr
	do_vector_sequence_b5489 4 
code9_begin:


	finish_test

#covers 0x2000-0x3fff
#{.mdata:0x2000}
.section .mdata , "aw"
mdata_begin:
.set dat, 1
.rept 1024
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
		.set idx, 0
		.rept 512
		 .if (idx==0x9a) || (idx==0x8f) || (idx==0x84)
			make_leaf_pte_entry 0 0xcf 0 0
		 .elseif (idx==0x85) || (idx==0x8E) || (idx==0x8c)
			make_leaf_pte_entry 0 0xcf 0 0
		 .elseif (idx==0x8B) || (idx==0x89) || (idx==0x88)
			make_leaf_pte_entry 0 0xcf 0 0
		 .else
		 	make_nonleaf_pte_entry 0x240001 0x21
		 .endif
		  .set idx, idx+1
		.endr

#{.vptl3: 0x240001000}
.section .vptl3, "aw"
		make_nonleaf_pte_entry 0x240002 0x21  			
		.set idx, 1
		.rept 511
			.if idx==1
				make_leaf_pte_entry (idx<<30)>>12 0xcf 0 0 
			.elseif idx==64 || idx==0x80 || idx==0xc0
				make_leaf_pte_entry 0 0xcf 0 0
			.elseif idx==0x100 || idx==0x140 || idx==0x180 || idx==0x1c0
				make_leaf_pte_entry 0 0xcf 0 0
			.else
				make_leaf_pte_entry (idx<<30)>>12 0xcf 0 0
			.endif
		  .set idx, idx+1
		.endr

#make_leaf_pte_entry (idx<<30)>>12 0xcf 0 1 #pbmt = 1 
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




#Not used########

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

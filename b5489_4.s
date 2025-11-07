#define STDOUT 0xd0580000

.equ pma, 0x7c0
.equ menvcfg, 0x30a

.equ SV57_PAGING_MODE, 	0xA
.equ SV48_PAGING_MODE, 	0x9
.equ SV39_PAGING_MODE, 	0x8

.equ SATP_PPN, 	0x140000 #4K aligned satp.ppn sv48
.equ SATP_ASID, 0xffff
.equ SATP_MODE, SV57_PAGING_MODE

.equ BIT_MSTATUS_VS_LO,  9
.equ BIT_MSTATUS_VS_HI,  10
.equ BIT_MSTATUS_MPP_LO, 11
.equ BIT_MSTATUS_MPP_HI, 12
.equ BIT_MSTATUS_MPRV, 	 17
.equ BIT_MSTATUS_SUM, 	 18
.equ BIT_MSTATUS_MXR, 	 19

.equ 	REGION1, 					 35
.equ	BIT_MENVCFG_PBMTE, 62

.equ ECALL_SMODE, 9

.option norvc

#=================================
#set PBMTE
#clobbers x22
#=================================
.macro set_menvcfg_pbmte
	bseti	x22, x0, BIT_MENVCFG_PBMTE
	csrs	menvcfg, x22
.endm


#=================================
#create leaf pte entry
#permissions = {v,r,w,x,u,g,a,d}
#               lsb           msb
#=================================
.macro make_leaf_pte_entry ppn permissions n pbmt
	.dword (\n<<63|\pbmt<<61|\ppn<<10|\permissions)
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
	li x22, (\mode <<60) | (\asid<<44) | (\ppn)
	csrw satp, x22
.endm


.macro setup_threads tid 

	#program handler 
	bseti x2, x0, 33
	bseti x2, x2, 22
	csrw	stvec, x2 #mtvec = 0x200400000

	#medeleg[9] = 1 ecall -> so that 0x200400000 pbmt is applied via paging
	#li   x2, 1
	#slli x2, x2, ECALL_SMODE
	#csrrs x1, medeleg, x2

	#setup mstatus to jump to supervisor mode
	bseti	x1, x0, BIT_MSTATUS_MPP_LO
	bseti	x2, x1, BIT_MSTATUS_MPP_HI
	bseti x2, x2, BIT_MSTATUS_VS_LO  #bit9  vector status
	bseti x2, x2, BIT_MSTATUS_VS_HI  #bit10 vector status
	csrc	mstatus, x2
	bseti	x1, x1, BIT_MSTATUS_VS_LO	 #vector registers in init status
	csrs	mstatus, x1 #mstatus.MPP = 2'b01, mstatus[10:9]=2'b01 -> vector registers in initial state

	#configure vector parameters
	vsetvli	x22, x30, e8, m1, ta, ma  #x30 = (AVL) 256 

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

##########include "defines.h"

.global _start

#{.text.init:0x00000000}
.section .text.init
_start:
    initialize_registers
		set_menvcfg_pbmte
		start_test:
    	bseti x1, x0, 31
			li	x1, 1
			slli x1, x1, 31
			ret				# expands to jalr  x0, (x1)
	

#{.text:0x80000000}
.section .text

test_begin:
	li		x13, 0xc001aced
	li		x30, 256  #x30 used for AVL - Do not touch x30 elsewhere!

	#update sscratch with return pc
	la		x2, _pass
	csrw	sscratch, x2



	#M mode handler is UC
	li		x2, 1
	slli	x2, x2, REGION1
	csrw	mtvec, x2


	li		x2, 1
	csrr  x1, mhartid
	beqz  x1, 		continue_test_t0
	beq   x1, x2, continue_test_t1
	li		x2, 2
	beq   x1, x2, continue_test_t2

	#all other threads finish test
	csrr	x1, sscratch
	ret

#t0 and t1 have different fetch pcs
#t0 = 0x280000000
#t1 = 0x200000000
#t2 = 0x2C0000000
continue_test_t2:

	setup_threads 2

	#update mepc with pc = 0x2C0000000
	bseti 	x2, x0, 33
	bseti 	x2, x2, 31
	bseti 	x2, x2, 30
	csrw	mepc, x2

	j	continue_test_common


continue_test_t1:

	setup_threads 1

	#update mepc with pc = 0x200000000
	bseti 	x2, x0, 33
	csrw	mepc, x2

	j	continue_test_common

	
continue_test_t0:

	setup_threads 0

	#update mepc with pc = 0x280000000
	bseti 	x2, x0, 33
	bseti 	x2, x2, 31
	csrw	mepc, x2

continue_test_common:

	#initialize pmp0
	li		x22, 0
	li		x23, 16<<30
	srli	x22, x22, 2 #base>>2
	srli	x23, x23, 3 #size>>3
	add	    x22, x22, x23
	addi    x22, x22, -1
	csrw	pmpaddr0, x22
	li		x22, 0x1f
	csrw	pmpcfg0, x22

	#initialize pma
	li		x22, 0x5555555551 #region1 = uc
	csrw	pma, x22

	#update satp
	write_satp	SATP_PPN, SATP_ASID, SV48_PAGING_MODE

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


#{.mmodehndlr:0x800000000}
.section .mmodehndlr , "aw"
mmodehndlr_begin:
	lui		x12, 3
	lui		x15, 4
.rept 64 
	li		x31, 0x2
	.rept 15
		addi		x3, x3, 1
		and			x3, x12, x15
	.endr
	.rept 4
		li				x3, 1
		divu			x12, x12, x3
		divu			x3,  x12, x12
	.endr
.endr

	csrr x22, mepc
	addi x22, x22, 4
	csrw mepc, x22
	mret




#{.code1:0x280000000}
.section .code1 , "aw"
code1t0_begin:
.rept 128
	lui		x12, 1
	lui		x15, 2
	li		x31, 2
	vadd.vi		v0, v0, 1
	j			1f #jumptocacheline3
	.rept 11
		vadd.vi		v1, v1, 2
	.endr #endof cacheline1
	2:
	.rept 16
		vse8.v		v1, (x12) #cacheline2
	.endr
1:
		.rept 4
			vse8.v		v0, (x15)
			vle8.v		v1, (x15)
			vse8.v		v1, (x12)
		.endr
		vle8.v		v0, (x12)
		vse8.v		v1, (x12)
		addi x31, x31, -1
		bnez x31,	2b						#jumptocacheline2
.endr

	csrr	x1,	sscratch				#get return_pc
	ret					 							#jump and finish_test

#{.code1t1:0x200000000}
.section .code1t1 , "aw"
code1t1_begin:
	li		x31, 2
	li		x13, 0x1
	lui		x12, 2

	#j			1f
#.rept 64
	#.rept 15 
	#	nop
	#.endr
1:
	.rept 4
		ecall
	.endr

#.endr

	#addi	x31, x31, -1
	#bnez	x31, 1b

	csrr	x1,	sscratch		#get return_pc
	ret					 					#jump and finish_test

#{.code1t2:0x2c0000000}
.section .code1t2 , "aw"
code1t2_begin:

.rept 128
	lui		x12, 1
	lui		x15, 2
	li		x31, 2
	vadd.vi		v0, v0, 1
	j			1f #jumptocacheline3
	.rept 11
		vadd.vi		v1, v1, 2
	.endr #endof cacheline1
	2:
	.rept 16
		vse8.v		v1, (x12) #cacheline2
	.endr
1:
		.rept 4
			vse8.v		v0, (x15)
			vle8.v		v1, (x15)
			vse8.v		v1, (x12)
		.endr
		vle8.v		v0, (x12)
		vse8.v		v1, (x12)
		addi x31, x31, -1
		bnez x31,	2b						#jumptocacheline2
.endr

	csrr	x1,	sscratch				#get return_pc
	ret					 							#jump and finish_test


#handler code in S mode
#{.codecommon:0x200400000}
.section .codecommon , "aw"
code_common_begin:
	lui		x12, 3
	lui		x15, 4
.rept 64 
	li		x31, 0x2
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
		vse8.v		v0, (x15)
		vle8.v		v1, (x15)
		vadd.vi		v1, v1, 1
		vse8.v		v1, (x12)
		vle8.v		v0, (x12)
	.endr
	addi x31, x31, -1
	bgtz x31, 2b
	beqz x31, 3b
.endr
	csrr x22, sepc
	addi x22, x22, 4
	csrw sepc, x22
	sret

#{.mdata: 0x1000}
#{.mdata:0x1000:0x1000}
.section .mdata, "aw"
	.fill 4096, 1, 0

#pml4
#{.ptl5:0x140000000}
.section .ptl5, "aw"
	make_nonleaf_pte_entry 0x140001 0x31


#pdpt
#{.ptl4:0x140001000}
.section .ptl4, "aw"
	.set ppn3, 0
	.rept 512
		.if ppn3==8
			make_leaf_pte_entry (ppn3<<30)>>12 0xcf 0 0 #pbmt = 0
		.else
			make_leaf_pte_entry (ppn3<<30)>>12 0xcf 0 0
		.endif
		.set ppn3, ppn3+1
	.endr

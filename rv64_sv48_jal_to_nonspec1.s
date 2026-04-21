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

.equ BIT_MFC1_ICACHE_WAYDISABLE_LO, 16
.equ mfc0, 0x7f9
.equ mfc1, 0x7fa


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
	beqz  x1, 		continue_test_t1 #swap t0, t1 entry points
	beq   x1, x2, continue_test_t0 #swap t0, t1 entry points
	li		x2, 2
	beq   x1, x2, continue_test_t2
	li		x2, 3
	beq   x1, x2, continue_test_t3

	#all other threads finish test
	csrr	x1, sscratch
	ret

#t0 and t1 have different fetch pcs
#t0 = 0x280000000
#t1 = 0x200000000
#t2 = 0x2C0000000
#t3 = 0x800000000
continue_test_t3:
	setup_threads 3

	#update mepc with pc = 0x800000000
	bseti t0, zero, 35
	csrw mepc, t0

	#initialize pma
	li		x22, 0x5555555551 #region1 = uc
	csrw	pma, x22

  ecall #t3 jumps to the handler in M mode	

	#finish test
	csrr	x1, sscratch
	ret

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

	#enable way2 icache - other ways disabled
	#li		x1, 0xb
	#slli	x1, x1, BIT_MFC1_ICACHE_WAYDISABLE_LO
	#csrw mfc1, x1


	#update satp for threads t0-t2, t3 will be bare
	write_satp	SATP_PPN, SATP_ASID, SV48_PAGING_MODE

skip_satp_init:
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
	#j			1f
	2:
	.rept 15
		#nop
		vadd.vi		v0, v0, 1
	.endr
	3:
	.rept 15
		#nop
		vadd.vi		v0, v0, 1
	.endr
1:
	.rept 2
		vadd.vi		v0, v0, 1
		#vse8.v		v0, (x15)
		#vle8.v		v1, (x15)
		vadd.vi		v1, v1, 1
		#vse8.v		v1, (x12)
		#vle8.v		v0, (x12)
	.endr
	#addi x31, x31, -1
	#bgtz x31, 2b
	#beqz x31, 3b
.endr

	csrr x22, mepc
	addi x22, x22, 4
	csrw mepc, x22
	mret




#{.code1:0x280000000}
.section .code1 , "aw"
code1t0_begin:
	lui		x12, 1
	lui		x15, 2
	li		t4, 0x8   #outer loop counter
	li		t6, 0x8		#inner loop counter 
	2:
		.rept 128
			jal		t0,	1f #jump to nonspec region
		  add   t0, t0, zero	
			vadd.vi		v1, v1, 1
		  add   t0, t0, zero	
			nop
			vadd.vi		v0, v0, 1
		  add   t0, t0, zero	
			nop
			vadd.vi		v1, v1, 1
			jal		t0,	1f #jump to nonspec region
		.endr

	1:
		vadd.vi		v0, v0, 1
		vse8.v		v0, (x15)
		vle8.v		v1, (x15)
		vadd.vi		v1, v1, 1
		vse8.v		v1, (x12)
		vle8.v		v0, (x12)
		addi			t6, t6, -1 #decrement inner loop counter
		beqz			t6, t0_repeat_loop	
		jalr 			t1, (t0) #go to next pc

t0_repeat_loop:
		addi 			t4, t4, -1 #decrement outer loop counter
		beqz			t4, t0_terminate
		li				t6, 0x8    #reinitialize inner loop counter
		jal				t1, 2b

t0_terminate:
	csrr	x1,	sscratch				#get return_pc
	ret					 							#jump and finish_test

#{.code1t1:0x200000000}
.section .code1t1 , "aw"
code1t1_begin:
	li		t6, 4
	li		a3, 0x1
	lui		x12, 2
2:
	j			1f
3:
	.rept 256
		nop
	.endr
		j	1f
	.rept 256 #this block will never be executed
		nop
	.endr
1:
	.rept 256 
		mul t1, t0, zero
	.endr

	addi	t6, t6, -1
	beqz	t6, t1_terminate
	.rept 256
		divu	a3, a3, a3
	.endr
	jal 	zero, 3b

t1_terminate:
	csrr	x1,	sscratch		#get return_pc
	ret					 					#jump and finish_test


#{.code1t2:0x2c0000000}
.section .code1t2 , "aw"
code1t2_begin:
	lui		x12, 1
	lui		x15, 2
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
		#ecall
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
#{.ptl4:0x140000000}
.section .ptl4, "aw"
	make_nonleaf_pte_entry 0x140001 0x31


#pdpt
#{.ptl3:0x140001000}
.section .ptl3, "aw"
	.set ppn3, 0
	.rept 512
		.if ppn3==8
			#make_leaf_pte_entry (ppn3<<30)>>12 0xcf 0 1 #for T1 nonspec pbmt
			make_nonleaf_pte_entry 0x140004 0x1					#for T1 nonleaf entry
		.elseif ppn3==0xa
			make_nonleaf_pte_entry 0x140002 0x1					#for T0 nonleaf entry
		.elseif ppn3==0xb
			make_leaf_pte_entry (ppn3<<30)>>12 0xcf 0 0 #for T2 
		.else
			make_leaf_pte_entry (ppn3<<30)>>12 0xcf 0 0 #for other accesses
		.endif
		.set ppn3, ppn3+1
	.endr

#pde t0
#{.ptl2:0x140002000}
.section .ptl2, "aw"
	.set idx, 0
	.rept 512
		 make_nonleaf_pte_entry 0x140003 0x1					#for T0 nonleaf entry
		.set idx, idx+1
	.endr

#pte t0
#{.ptl1:0x140003000}
.section .ptl1, "aw"
	.set ppn3, 0x280000
	.set idx, 0
	.rept 512
		 .set ppn, (ppn3|idx)
		 .if idx%2==0
		 		make_leaf_pte_entry ppn  0xcf 0 0
		 .else
		 		make_leaf_pte_entry ppn  0xcf 0 2  #for T0 nonspec pbmt (destination)
		 .endif
		.set idx, idx+1
	.endr

#pde t1
#{.ptl2_1:0x140004000}
.section .ptl2_1, "aw"
	.set idx, 0
	.set ppn3, 0x200400
	.rept 512
		 .if idx==2
				make_leaf_pte_entry ppn3 0xcf 0 2					 #for address 0x200400000
		 .else
		 		make_nonleaf_pte_entry 0x140005 0x1					#for T1 nonleaf entry
		 .endif
		.set idx, idx+1
	.endr

#pte t1
#{.ptl1_1:0x140005000}
.section .ptl1_1, "aw"
	.set ppn3, 0x200000
	.set idx, 0
	.rept 512
		 .set ppn, (ppn3|idx)
		 .if idx%2==1
		 		make_leaf_pte_entry ppn  0xcf 0 0
		 .else
		 		make_leaf_pte_entry ppn  0xcf 0 2  #for T1 nonspec pbmt (destination)
		 .endif
		.set idx, idx+1
	.endr




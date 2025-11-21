.equ	BIT_MFC0_ICACHE_FLUSH, 19
.equ	BIT_MFC0_DISABLE_BPRED, 3

.equ	BIT_MFC1_ICACHE_WAYDISABLE_HI, 19
.equ	BIT_MFC1_ICACHE_WAYDISABLE_LO, 16
.equ  BIT_MFC1_BTBI_DISABLE_M, 				6
.equ  BIT_MFC1_RAS_DISABLE, 					5
.equ  BIT_MFC1_BTBI_DISABLE, 					4	
.equ  BIT_MFC1_NPC_DISABLE, 					3	
.equ  BIT_MFC1_ITTAGE_DISABLE, 				2	
.equ  BIT_MFC1_TAGE_DISABLE, 					1	
.equ  BIT_MFC1_PREFETCH_DISABLE, 		  0


.equ mfc0, 0x7f9
.equ mfc1, 0x7fa


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

.macro finish_test
	csrr	x5, mscratch
	c.jalr x5
.endm


.globl _start

#{.text.init:0x00000000}
.section .text.init
_start:
    initialize_registers
		start_test:
			#update sscratch with return pc
			la		x2, _pass
			csrw	mscratch, x2
    	bseti x1, x0, 31
			li	x1, 1
			slli x1, x1, 31
			ret				# expands to jalr  x0, (x1)
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



#{.code1:0x80000000}
.section .code1, "aw"
test_setup:



code1_begin:
 










#{.mdata: 0x1000}
#{.mdata:0x1000:0x1000}
.section .mdata, "aw"
	.fill 4096, 1, 0
#{.mdata1:0x2000:0x2000}
.section .mdata1, "aw"
	.fill 4096, 1, 0
#{.mdata2:0x3000:0x3000}
.section .mdata2, "aw"
	.fill 4096, 1, 0
#{.mdata3:0x4000:0x4000}
.section .mdata3, "aw"
	.fill 4096, 1, 0
#{.mdata4:0x5000:0x5000}
.section .mdata4, "aw"
	.fill 4096, 1, 0

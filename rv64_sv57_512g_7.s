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
	li		x23, 512<<30
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

#{.code1:0x4800000000}
#{.code1:0xffff004800000000:0x4800000000}
.section .code1 , "aw"
code1_begin:

#{.code2:0x4801000810}
#{.code2:0xffff004801000810:0x4801000810}
.section .code2 , "aw"
code2_begin:


#{.code3:0x4802001020}
#{.code3:0xffff004802001020:0x4802001020}
.section .code3 , "aw"
code3_begin:

#{.code4:0x4803001830}
#{.code4:0xffff004803001830:0x4803001830}
.section .code4 , "aw"
code4_begin:

#{.code5:0x4804002100}
#{.code5:0xffff004804002100:0x4804002100}
.section .code5 , "aw"
code5_begin:

#{.code6:0x4805002930}
#{.code6:0xffff004805002930:0x4805002930}
.section .code6 , "aw"
code6_begin:

#{.code7:0x4806003150}
#{.code7:0xffff004806003150:0x4806003150}
.section .code7 , "aw"
code7_begin:

#{.code8:0x4807003940}
#{.code8:0xffff004807003940:0x4807003940}
.section .code8 , "aw"
code8_begin:


#{.ret1:0xc1230260}
#{.ret1:0xffff0000c1230260:0xc1230260}
.section .ret1 , "aw"
ret1_begin:

#{.ret2:0x92024a0}
#{.ret2:0xffff0000092024a0:0x92024a0}
.section .ret2 , "aw"
ret2_begin:

#{.ret3:0xc9232220}
#{.ret3:0xffff0000c9232220:0xc9232220}
.section .ret3 , "aw"
ret3_begin:

#{.ret4:0x19206410}
#{.ret4:0xffff000019206410:0x19206410}
.section .ret4 , "aw"
ret4_begin:


#{.ret5:0x21208550}
#{.ret5:0xffff000021208550:0x21208550}
.section .ret5 , "aw"
ret5_begin:

#{.ret6:0x2920a5a0}
#{.ret6:0xffff00002920a5a0:0x2920a5a0}
.section .ret6 , "aw"
ret6_begin:

#{.ret7:0x3120c500}
#{.ret7:0xffff00003120c500:0x3120c500}
.section .ret7 , "aw"
ret7_begin:

#{.ret8:0x3920e520}
#{.ret8:0xffff00003920e520:0x3920e520}
.section .ret8 , "aw"
ret8_begin:

#{.ret9:0x6b807860}
.section .ret9 , "aw"
ret9_begin:

#{.ret10:0x74808380}
.section .ret10 , "aw"
ret10_begin:

#{.ret11:0x75808bc0}
.section .ret11 , "aw"
ret11_begin:

#{.ret12:0x76809300}
.section .ret12 , "aw"
ret12_begin:

#{.ret13:0x77809b40}
.section .ret13 , "aw"
ret13_begin:

#{.ret14:0x7080a280}
.section .ret14 , "aw"
ret14_begin:

#{.ret15:0x7180aac0}
.section .ret15 , "aw"
ret15_begin:

#{.ret16:0x7280b200}
.section .ret16 , "aw"
ret16_begin:

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
	.rept 512
		make_nonleaf_pte_entry 0x140001 0x21
	.endr


#{.ptl4:0x140001000}
.section .ptl4, "aw"
	.set ppn3, 0
	.rept 512
		make_leaf_pte_entry (ppn3<<39)>>12 0xcf 0 0
		.set ppn3, ppn3+1
	.endr

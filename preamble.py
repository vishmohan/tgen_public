mstr = '''
.equ pma, 0x7c0
.equ mtinst, 0x34a
.equ mtval2, 0x34b
.equ mfc0, 0x7f9
.equ menvcfg, 0x30a

.equ SV57_PAGING_MODE, 	0xA
.equ SV48_PAGING_MODE, 	0x9
.equ SV39_PAGING_MODE, 	0x8

.equ SATP_PPN, 	 0x140000 #4K aligned satp.ppn
.equ SATP_ASID,  0xffff
.equ VSATP_ASID, 0xfffe
.equ VSATP_PPN,  0x140008 #4K aligned vsatp.ppn
.equ SATP_MODE,  SV57_PAGING_MODE
.equ VSATP_MODE, SV57_PAGING_MODE

.equ HGATP_PPN, 	 0x140010 #16K aligned satp.ppn
.equ HGATP_VMID,   1
.equ HGATP_MODE,   SV57_PAGING_MODE

.equ BIT_MSTATUS_MPP_LO, 11
.equ BIT_MSTATUS_MPP_HI, 12
.equ BIT_MSTATUS_MPRV, 	 17
.equ BIT_MSTATUS_SUM, 	 18
.equ BIT_MSTATUS_MXR, 	 19
.equ BIT_MSTATUS_MPV, 	 39

.equ	BIT_MFC0_ICACHE_FLUSH, 19
.equ	BIT_MFC0_DISABLE_BPRED, 3

.equ	BIT_MENVCFG_ADUE,  61
.equ	BIT_MENVCFG_PBMTE, 62

#=================================
#set ADUE
#clobbers x22
#=================================
.macro set_menvcfg_adue
	bseti	x22, x0, BIT_MENVCFG_ADUE
	csrs	menvcfg, x22
.endm

#=================================
#set PBMTE
#clobbers x22
#=================================
.macro set_menvcfg_pbmte
	bseti	x22, x0, BIT_MENVCFG_PBMTE
	csrs	menvcfg, x22
.endm

#=================================
#set ADUE
#clobbers x22
#=================================
.macro set_henvcfg_adue
	bseti	x22, x0, BIT_MENVCFG_ADUE
	csrs	henvcfg, x22
.endm

#=================================
#set PBMTE
#clobbers x22
#=================================
.macro set_henvcfg_pbmte
	bseti	x22, x0, BIT_MENVCFG_PBMTE
	csrs	henvcfg, x22
.endm

#=================================
#create leaf pte entry
#permissions = {v,r,w,x,u,g,a,d}
#               lsb           msb
#=================================
.macro make_leaf_pte_entry ppn permissions n pbmt
	.dword (\\n<<63|\pbmt<<61|\ppn<<10|\permissions)
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
	li x22, (\\mode <<60) | (\\asid<<44) | (\\ppn)
	csrw satp, x22
.endm

#=================================
#update vsatp with specified value
#clobbers x22
#=================================
.macro write_vsatp ppn,asid,mode
	li x22, (\\mode <<60) | (\\asid<<44) | (\\ppn)
	csrw vsatp, x22
.endm

#=================================
#update hgatp with specified value
#clobbers x22
#=================================
.macro write_hgatp ppn,vmid,mode
	li x22, (\\mode <<60) | (\\vmid<<44) | (\\ppn)
	csrw hgatp, x22
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


.macro finish_test
	csrr	x5, sscratch
	c.jalr x5
.endm

'''

def get_preamble():
	return mstr


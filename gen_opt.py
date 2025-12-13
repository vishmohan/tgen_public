#! /usr/bin/env python3
import random

#def	gen_opt(fname,suffix_asm,suffix_linker,fullpath,num_threads,pagingmode):
def	gen_opt(**kwargs):
	''' 
	generate the opt file 
	returns a string that is used to create the list file
	'''

	fname = kwargs['fname']
	suffix_asm = kwargs['suffix_asm']
	suffix_linker = kwargs['suffix_linker']
	fullpath = kwargs['fullpath']
	num_threads = kwargs['num_threads']
	pagingmode = kwargs['pagingmode']
	arch = kwargs['arch']

	src = fname + suffix_asm
	lsrc = fname + suffix_linker
	optname = fname + ".opt"
	optname_st = fname + "_st.opt"
	optname_mt = fname + "_mt.opt"
	optname_tblite = fname + "_tblite.opt"
	optname_gatesim = fname + "_gatesim.opt"
	optname_uvm = fname + "_uvm.opt"

	mt_num_threads = num_threads if num_threads > 1 else 4
	paging_mode_str = ""
	if pagingmode== "sv57":
		paging_mode_str = "RV64_VA_SIZE=57,"

	#myconfig_st = random.choice(["rv64_release_qh","rv64_alp5100","rv64_alp5200"]) #for ST
	#myconfig_st = random.choice(["rv64_release_qh"]) #for ST
	myconfig_st = random.choice(["rv64_alp5100"]) #for ST



	config_str = f'{paging_mode_str}RV_BUILD_SVADU=True'#,RV_BTB2_ENABLE=1'
	config_str_mt = f'{paging_mode_str}NUM_THREADS={mt_num_threads},RV_BUILD_SMRNMI=False'
	way_predictor = random.choice(["True","False"])
	ifu_prefetch = random.choice(["True","False"])
	#config_str_mt += f',RV_WAY_PREDICTOR_ENABLE={way_predictor},RV_IFU_PREFETCH_ENABLE={ifu_prefetch}' 

	#injector specific options
	#disable btb hit
	disable_btb_hit = random.randint(0,1)
	#dec_avail_inj parameters
	dec_avail_inj_en = random.randint(0,1)
	dec_avail_inj_min_delay = random.randint(8,20)
	dec_avail_inj_max_delay = random.randint(22,50)
	#itlb_invalidate_inj 
	itlb_invalidate_inj_en = random.randint(0,1)
	#parity injector
	parity_inj_en = random.randint(0,1)

	#axi response delay
	long_delay = random.uniform(0,1)
	if long_delay > 0.1 and long_delay < 0.3:
		axi4_min_response_delay = random.randint(10,20)
		axi4_max_response_delay = random.randint(21,80)
	elif long_delay > 0.3 and long_delay < 0.9:
		axi4_min_response_delay = random.randint(10,15)
		axi4_max_response_delay = random.randint(16,18)
	else:
		axi4_min_response_delay = random.randint(150,200)
		axi4_max_response_delay = random.randint(300,400)

	myconfig_mt = "rv64_alp1200"
	mt_ooo = False
	if mt_ooo:
		myconfig_mt = "rv64_qh_perf_mt"
		config_str_mt = f'{paging_mode_str}NUM_THREADS={mt_num_threads},RV64_PA_SIZE=39,RV_BUILD_SMRNMI=False'
	

	#btb ovrd params
	rv_btb2_enable = 1 
	rv_btb2_tag_size = random.choice([10,14])
	rv_btb2_array_depth = random.choice([128,256,512])
	rv_inst_fetch_width = 16 
	rv_btb_size = random.choice([32, 48, 64, 128, 256, 512])

	#tage ovrd params
	tage_enable = random.choice([0,1])
	tage_ram_enable = random.choice([0,1])
	tage_entries = random.choice([16,32,512, 1024])
	tage_cache_entries = 32 #[32,64]
	tage_cache_way = 1 #[1...8]

	tage_history_size_dict = { 1: 2, 2: 4, 3: 16, 4: 64, 5: 128, 6: 256, 7: 512, 8: 1024, 9: 2048, 10:4096, 11:4096, 12:4096, 13:4096, 14:4096, 15:4096 }
	tage_tables = random.choice([4,5,6])
	tage_history_size = tage_history_size_dict[tage_tables]

	#ras ovrd
	ras_enable = 1
	ras_depth =  random.choice([64,128])

	btb_ovrd_str = f',RV_BTB2_ENABLE={rv_btb2_enable},RV_BTB_SIZE={rv_btb_size},RV_INST_FETCH_WIDTH={rv_inst_fetch_width},RV_BTB2_ARRAY_DEPTH={rv_btb2_array_depth},RV_BTB2_BTAG_SIZE={rv_btb2_tag_size}'
	tage_ovrd_str = f',TAGE_ENABLE={tage_enable},TAGE_RAM_ENABLE={tage_ram_enable},TAGE_ENTRIES={tage_entries},TAGE_TABLES={tage_tables},TAGE_HISTORY_SIZE={tage_history_size},TAGE_CACHE_ENTRIES={tage_cache_entries},TAGE_CACHE_WAY={tage_cache_way}'
	ras_ovrd_str = f',RAS_ENABLE={ras_enable},RAS_DEPTH={ras_depth}'

	enable_overrides = False

	if enable_overrides:
		btb_ovrd = random.randint(0,1)
		if btb_ovrd:
			config_str += btb_ovrd_str

		tage_ovrd = random.randint(0,1)
		if tage_ovrd:
			config_str += tage_ovrd_str

		ras_ovrd = random.randint(0,1)
		if ras_ovrd:
			config_str += ras_ovrd_str

	if arch=="rv32":
		mstr_arch = "rv32"
		mstr_flags = "rv32gcv_zba_zbb_zbc_zbs_svinval"
		mstr_cfg_shasta = "rv32_alp120"
		mstr_cfg_ovrd = "MAILBOX_ADDR=0xd0580000,RV_COMPILE_SFX_MEM=True"
		mstr_turlock = "turlock_aia"
		mstr_gate_ovrd = "GATE_SIM=1,SIGNAL_GATE=1,GATE_SIM_WRAPPER=1,SF_GATE_SIM=1,MAILBOX_ADDR=0xd0580000"
	else:
		mstr_arch = 		"rv64"
		mstr_flags = 		"rv64gcv_zba_zbb_zbc_zbs_svinval"
		if num_threads > 1:
			mstr_cfg_shasta = "rv64_alp1200"
			mstr_turlock = 	"turlock_mt"
		else:
			mstr_cfg_shasta = "rv64_alp5100"
			mstr_turlock = 	"turlock_aia"
		mstr_cfg_ovrd = "MAILBOX_ADDR=0x8d0580000,RV_COMPILE_SFX_MEM=True"
		mstr_gate_ovrd = "GATE_SIM=1,SIGNAL_GATE=1,SF_GATE_SIM=1,MAILBOX_ADDR=0x8d0580000"

	mstr_rv_uvm = f'''
-arch {mstr_arch}
-march {mstr_flags}
-config_shasta {mstr_cfg_shasta}
-config_ovr {mstr_cfg_ovrd}
-config_turlock {mstr_turlock}
-bench_dec_num_threads {num_threads}
-gate_sim=0
-harts={num_threads}
-maxinstr=50000
-bench_dec_mrac_cache_en 0
-shadow_skip=1
-stepfile_skip=1
-stake_skip=1
-tblite_trc_en=1
-test {src}
-timeout=500000
-ld_file {lsrc}
	'''	

	mstr_rv_tblite_addon = f'''
-tb_lite=1
-tb_lite_vip=1
-console_check "TEST PASSED"
	'''	

	mstr_rv_tblite = mstr_rv_uvm + mstr_rv_tblite_addon

	#for gatesim tests after adding eot_checks
	addon = '-console_check "TEST PASSED"'

	mstr_rv_gate = f'''
-arch {mstr_arch}
-march {mstr_flags}
-config_shasta {mstr_cfg_shasta}
-config_ovr {mstr_gate_ovrd}
-config_turlock {mstr_turlock}
-bench_dec_num_threads {num_threads}
-gate_sim=1
-harts={num_threads}
-maxinstr=100000
-bench_dec_mrac_cache_en=0
-shadow_skip=1
-stepfile_skip=1
-stake_skip=1
-tb_lite=1
-tb_lite_vip=1
-tblite_trc_en=1
-test {src}
-timeout=500000
-ld_file {lsrc}
-console_check "TEST PASSED"
	'''

	mstr = f'''
		-test {src}
		-arch rv64
		-march rv64gcv_zbs
		-config {myconfig_st}
		-config_shasta {myconfig_st}
		-config_turlock turlock_aia
		-config_ovr_shasta "{config_str}"
		-maxinstr 550000
		-ld_file {lsrc}
		-shadow_tracePTE 1
		-tracePTE  1 
		-bench_mmu_checker_disable  1
		-bench_ifu_BigTage_collision_inj_en 1
		-bench_ifu_BigTage_collision_inj_min_delay 100
		-bench_ifu_BigTage_collision_inj_max_delay 500
		-bench_ifu_dec_avail_inj_en 			 {dec_avail_inj_en}
		-bench_ifu_dec_avail_inj_min_delay {dec_avail_inj_min_delay}
		-bench_ifu_dec_avail_inj_max_delay {dec_avail_inj_max_delay}
		-bench_axi4_min_response_delay 		 {axi4_min_response_delay}
		-bench_axi4_max_response_delay     {axi4_max_response_delay}
		-bench_ifu_disable_btb_hit {disable_btb_hit}
		-bench_ifu_itlb_invalidate_inj_en {itlb_invalidate_inj_en}
		-bench_ifu_icache_parity_inj_en {parity_inj_en}
		-msg_level debug
		-timeout	500000
		-stake_skip 1
		'''
	mstr_mt = f'''
		-test {src}
		-arch rv64
		-march rv64gcv_zbs
		-config {myconfig_mt}
		-config_ovr_shasta "{config_str_mt}"
		-config_turlock turlock_mt
		-bench_dec_num_threads {mt_num_threads}
		-bench_mmu_checker_disable  1
		-harts {mt_num_threads}
		-maxinstr 550000
		-ld_file {lsrc}
		-shadow_tracePTE 1
		-tracePTE 1 
		-msg_level debug
		-bench_ifu_fetch_delay 40
		-bench_core_fe_timeout 250000
		-bench_core_be_timeout 250000
		-bench_core_ldst_op_timeout 1500000
		-bench_ifu_dec_avail_inj_en 			 {dec_avail_inj_en}
		-bench_ifu_dec_avail_inj_min_delay {dec_avail_inj_min_delay}
		-bench_ifu_dec_avail_inj_max_delay {dec_avail_inj_max_delay}
		-bench_axi4_min_response_delay 		 {axi4_min_response_delay}
		-bench_axi4_max_response_delay     {axi4_max_response_delay}
		-bench_ifu_itlb_invalidate_inj_en {itlb_invalidate_inj_en}
		-bench_ifu_icache_parity_inj_en {parity_inj_en}
		-timeout	8000000
		-stepfile_skip 0 
		-stake_skip 1
		'''
		#-bench_dec_mrac_cache_en    0
		#-bench_dec_mrac							0x55555555
	#generate opt file
	with open(fullpath+optname,"w") as f:
		if num_threads==1:
			if arch=='rv64':
				print(mstr,file=f)
			else:
				print(mstr_rv_uvm,file=f)
		else:
			print(mstr_mt,file=f)

	#now generate ST version of optfile unconditionally
	#useful when a MT test needs to be tried as ST
	with open(fullpath+optname_st,"w") as f:
			print(mstr,file=f)

	#now generate MT version of optfile unconditionally
	#useful when a ST test needs to be tried as MT
	with open(fullpath+optname_mt,"w") as f:
			print(mstr_mt,file=f)


	#for rv32/rv64 generate tblite and gatesim opfiles
	with open(fullpath+optname_tblite,"w") as f:
		print(mstr_rv_tblite,file=f)
	with open(fullpath+optname_gatesim,"w") as f:
		print(mstr_rv_gate,file=f)
	with open(fullpath+optname_uvm,"w") as f:
		print(mstr_rv_uvm,file=f)
		print(addon,file=f)

	mstr1 = f"-opt {optname}\n"
	return mstr1

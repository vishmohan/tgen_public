#! /usr/bin/env python3
import random

def	gen_opt(fname,suffix_asm,suffix_linker,fullpath,num_threads=1):
	''' 
	generate the opt file 
	returns a string that is used to create the list file
	'''

	src = fname + suffix_asm
	lsrc = fname + suffix_linker
	optname = fname + ".opt"
	optname_st = fname + "_st.opt"
	optname_mt = fname + "_mt.opt"
	mt_num_threads = num_threads if num_threads > 1 else 4

	myconfig_st = random.choice(["rv64_release_qh"]) #for ST

	config_str = 'RV64_VA_SIZE=57,RV_BUILD_SVADU=True'#,RV_BTB2_ENABLE=1'
	config_str_mt = f'RV64_VA_SIZE=57,RV_BTB2_ENABLE=1,AXI_ASYNC_OUTPUTS=False,NUM_THREADS={mt_num_threads},RV64_PA_SIZE=39,RV_BUILD_SVADU=True'
	way_predictor = random.choice(["True","False"])
	ifu_prefetch = random.choice(["True","False"])
	config_str_mt += f',RV_BUILD_AFFINITY_REGISTER=False,RV_WAY_PREDICTOR_ENABLE={way_predictor},RV_IFU_PREFETCH_ENABLE={ifu_prefetch}' 
	
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

	

	mstr = f'''
		-test {src}
		-arch rv64
		-march rv64gcv_zbs
		-config {myconfig_st}
		-config_ovr_shasta "{config_str}"
		-maxinstr 550000
		-ld_file {lsrc}
		-shadow_tracePTE 1
		-tracePTE  1 
		-msg_level debug
		-timeout	250000
		-stake_skip 1
		'''
	mstr_mt = f'''
		-test {src}
		-arch rv64
		-march rv64gcv_zbs
		-config rv64_alp1200_mt
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
		-bench_core_ldst_op_timeout 150000
		-timeout	500000
		-stepfile_skip 0 
		-stake_skip 1
		'''
		#-bench_dec_mrac_cache_en    0
		#-bench_dec_mrac							0x55555555
	#generate opt file
	with open(fullpath+optname,"w") as f:
		if num_threads==1:
			print(mstr,file=f)
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

	mstr1 = f"-opt {optname}\n"
	return mstr1

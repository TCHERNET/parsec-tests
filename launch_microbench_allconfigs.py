#!/usr/bin/env python3

#This is a job launch script

import os
import sys
import argparse
from uuid import UUID

from gem5art.artifact.artifact import Artifact
from gem5art.run import gem5Run
from gem5art import tasks



experiments_repo = Artifact.registerArtifact(
    command = 'git clone https://github.com/darchr/gem5art-experiments.git',
    typ = 'git repo',
    name = 'gem5-experiments',
    path =  './',
    cwd = '../',
    documentation = 'main experiments repo to run experiments in gem5art'
)

gem5_repo = Artifact.registerArtifact(
    command = '''git clone https://github.com/darchr/gem5 
    cd gem5''',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = 'git repo with gem5 cloned on Nov 22 from DarchR (patch shd be applied to support mem vector port)'
)

m5_binary = Artifact.registerArtifact(
    command = 'make -f Makefile.x86',
    typ = 'binary',
    name = 'm5',
    path =  'gem5/util/m5/m5',
    cwd = 'gem5/util/m5',
    inputs = [gem5_repo,],
    documentation = 'm5 utility'
)

gem5_binary = Artifact.registerArtifact(
    command = 'scons build/X86/gem5.opt',
    typ = 'binary',
    name = 'gem5',
    cwd = 'gem5/',
    path =  'gem5/build/X86/gem5.opt',
    inputs = [gem5_repo,],
    documentation = 'default gem5 x86'
)


if __name__ == "__main__":

    full_list =['CCa','CCe','CCh', 'CCh_st', 'CCl','CCm','CF1','CRd','CRf','CRm',
    'CS1','CS3','DP1d','DP1f','DPcvt','DPT','DPTd','ED1','EF','EI','EM1','EM5',
    'MD','MC','MCS','M_Dyn','MI','MIM','MIM2','MIP','ML2','ML2_BW_ld','ML2_BW_ldst',
    'ML2_BW_st','ML2_st','MM','MM_st','STc','STL2','STL2b']
    controlbenchmarks = ['CCa','CCe','CCh', 'CCh_st','CCl','CCm','CF1','CRd','CRf','CRm',
    'CS1','CS3']
    memorybenchmarks = ['MD','MC','MCS','M_Dyn','MI','MIM','MIM2','MIP','ML2','ML2_BW_ld','ML2_BW_ldst',
    'ML2_BW_st','ML2_st','MM','MM_st','STc','STL2','STL2b']
    main_memorybenchmarks = ['MM','MM_st','STc','STL2','STL2b']
    cpu_types = ['Simple','DefaultO3'] 
    mem_latency = ['Inf','SingleCycle','Slow'] #['Slow', 'Inf' 'SingleCycle']

    
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', choices = ['config_base','config_controlbenchmarks','config_memorybenchmarks']
                                               ,default='config_base',help = "experiment you want to run")
    parser.add_argument('--bm_list',choices =[full_list,controlbenchmarks,memorybenchmarks,main_memorybenchmarks]
                                            ,default=full_list, help = "benchmark suite to run the experiment")
    parser.add_argument('--cpu', choices = ['Simple','O3'], default='Simple',help="cpu choice for controlbenchmark experiments.")
    parser.add_argument('--cache_type', type = str, choices = ['L1_cache','L2_cache'],
                                            default='L1_cache',help = "cache type for memory experiment")
    args  = parser.parse_args()

    config = args.config
    bm_list =  args.bm_list
    
    cpu_bp= args.cpu
    Simple_bp=('Simple_Local', 'Simple_BiMode', 'Simple_Tournament', 'Simple_LTAGE')
    DefaultO3_bp=('DefaultO3_Local' ,'DefaultO3_BiMode', 'DefaultO3_Tournament','DefaultO3_LTAGE')
    
    cache_type = args.cache_type #'L2_cache'
    #L1Cache_sizes.
    L1D = ['4kB','32kB','64kB']
    #L2Cache_sizes.
    L2C = ['512kB','1MB']

    #Architecture to run with.
    arch='X86' #'ARM'
    if arch =='X86':
        bma='bench.X86'
    elif arch =='ARM':
        bma='bench.ARM'

    path = 'microbench'
    
    if config == 'config_base':
      for mem in mem_latency:
        for bm in bm_list:
            for cpu in cpu_types:
                    run = gem5Run.createSERun(
                        'gem5/build/X86/gem5.opt',
                        'configs-microbench-tests/run_allbenchmarks.py',
                        'results/{}/run_allbenchmarks/{}/{}/{}'.format(arch,mem,bm,cpu),
                        gem5_binary, gem5_repo, experiments_repo,
                        cpu, mem, os.path.join(path,bm,bma))
                    #run_gem5_instance.apply_async((run,))
                    run.run() 
    elif config == 'config_controlbenchmarks':
        for mem in mem_latency:
            for bm in bm_list:
                if cpu_bp == 'Simple':
                    for config_cpu in Simple_bp:
                        run = gem5Run.createSERun(
                                'gem5/build/X86/gem5.opt',
                                'configs-microbench-tests/run_controlbenchmarks.py',
                                'results/{}/run_controlbenchmarks/{}/{}/{}/{}'.format(arch,mem,bm,cpu_bp,config_cpu), 
                                gem5_binary, gem5_repo, experiments_repo,
                                config_cpu, mem, os.path.join(path,bm,bma))
                        #run_gem5_instance.apply_async((run,)) 
                        run.run()  
                elif cpu_bp == 'O3':
                    for config_cpu in  DefaultO3_bp:
                        run = gem5Run.createSERun(
                                'gem5/build/X86/gem5.opt',
                                'configs-microbench-tests/run_controlbenchmarks.py',
                                'results/{}/run_controlbenchmarks.py/{}/{}/{}/{}'.format(arch,mem,bm,cpu_bp,config_cpu), 
                                gem5_binary, gem5_repo, experiments_repo,
                                config_cpu, mem, os.path.join(path,bm,bma))
                        #run_gem5_instance.apply_async((run,))
                        run.run()
    elif config =='config_memorybenchmarks':
        for mem in mem_latency:
            for bm  in bm_list:
                for cpu in cpu_types:
                        if cache_type =='L1_cache':
                            for size in L1D:
                                run = gem5Run.createSERun(
                                'gem5/build/X86/gem5.opt',
                                'configs-microbench-tests/run_memorybenchmarks.py',
                                'results/{}/run_memorybenchmarks/{}/{}/{}/L1_cache/{}'.format(arch,mem,bm,cpu,size), 
                                gem5_binary, gem5_repo, experiments_repo,
                                cpu, mem, size,'1MB', os.path.join(path,bm,bma))
                                #run_gem5_instance.apply_async((run,))
                                run.run()
                        if cache_type =='L2_cache':
                            for size in L2C:
                                run = gem5Run.createSERun(
                                'gem5/build/X86/gem5.opt',
                                'configs-microbench-tests/run_memorybenchmarks.py',
                                'results/{}/run_memorybenchmarks/{}/{}/{}/L2_cache/{}'.format(arch,mem,bm,cpu,size), 
                                gem5_binary, gem5_repo, experiments_repo,
                                cpu, mem,'32kB',size, os.path.join(path,bm,bma))
                                #run_gem5_instance.apply_async((run,))
                                run.run()



    



    


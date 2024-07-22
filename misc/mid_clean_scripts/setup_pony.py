#!/usr/bin/env python
# ian.heywood@physics.ox.ac.uk

import glob
import numpy
import os
import sys

def write_slurm(runfile,logfile,jobname,time,ncpu,mem,syscall):
    f = open(runfile,'w')
    f.writelines(['#!/bin/bash\n',
        '#file: '+runfile+':\n',
        '#SBATCH --job-name='+jobname+'\n',
        '#SBATCH --time='+time+'\n',
        '#SBATCH --partition=Main\n'
        '#SBATCH --ntasks=1\n',
        '#SBATCH --nodes=1\n',
        '#SBATCH --cpus-per-task='+str(ncpu)+'\n',
        '#SBATCH --mem='+mem+'\n',
        '#SBATCH --output='+logfile+'\n',
        'SECONDS=0\n',
        syscall+'\n',
        'echo "****ELAPSED "$SECONDS" '+jobname+'"\n'])
    f.close()


#ptgs = sorted(glob.glob('COSMOS*/MID/images/'))

ptgs = sorted(glob.glob('J1000+0233/out*0769-1152*/'))

i = 0

for ptg in ptgs:
    os.chdir(ptg)
    jobname = 'pony'+str(i).zfill(4)
    os.system('cp ../../pony.py .')
    runfile = 'slurm_pony_'+jobname+'.sh'
    logfile = 'slurm_pony_'+jobname+'.log'
    syscall = 'singularity exec /users/ianh/containers/oxkat-0.42.sif python3 pony.py --threshold 4.8 img'
    write_slurm(runfile,logfile,jobname,'04:00:00',16,'115GB',syscall)
    os.system('sbatch '+runfile)
    os.chdir('../../')
    i+=1

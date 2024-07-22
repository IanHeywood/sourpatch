#!/usr/bin/env python
# ian.heywood@physics.ox.ac.uk

import glob
import numpy
import os
import sys
import shutil

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


container = '/users/ianh/containers/oxkat-0.41.sif'

chunks = sorted(glob.glob('*/out*'))

cwd = os.getcwd()

for chunk in chunks:
    os.chdir(chunk)
    if not os.path.isdir('SCRIPTS'): os.mkdir('SCRIPTS')
    if not os.path.isdir('LOGS'): os.mkdir('LOGS')
    jobname = chunk.split('.mms_')[-1].replace('CL','PS')
    shutil.copyfile('../../get_psfs_taper_seq.py','get_psfs_taper_seq.py')
    syscall = 'singularity exec '+container+' '
    syscall += 'python3 get_psfs_taper_seq.py'
    runfile = 'SCRIPTS/slurm_psfs_'+jobname+'.sh'
    logfile = 'LOGS/slurm_psfs_'+jobname+'.log'
    write_slurm(runfile,logfile,jobname,'12:00:00',8,'64GB',syscall)
    print('sbatch '+runfile)
    os.system('sbatch '+runfile)
    os.chdir(cwd)


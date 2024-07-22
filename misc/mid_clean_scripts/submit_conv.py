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

if not os.path.isdir('SCRIPTS'): os.mkdir('SCRIPTS')
if not os.path.isdir('LOGS'): os.mkdir('LOGS')

opdirs = sorted(glob.glob('*/out*'))
prefixes = []
for opdir in opdirs:
    prefix = opdir.split('_MID_')[-1].split('.mms')[0]
    if prefix not in prefixes: prefixes.append(prefix)


for prefix in prefixes:
    print(prefix)
    workdir = 'conv_'+prefix
    if not os.path.isdir(workdir): os.mkdir(workdir)
    os.chdir(workdir)
    folders = sorted(glob.glob('../*/out*'+prefix+'*'))
    for folder in folders:
        print(f'    {folder}')
        os.system('ln -s '+folder+' .')
        os.system('cp ../convolve_channels.py .')
        os.system('cp ../beam_template.fits .')
        ch0 = prefix.split('-')[0]
        jobname = 'CONV'+ch0
        runfile = 'slurm_conv_'+prefix+'.sh'
        logfile = 'slurm_conv_'+prefix+'.log'
        syscall = 'singularity exec /users/ianh/containers/oxkat-0.41.sif python3 convolve_channels.py '+prefix
        write_slurm(runfile,logfile,jobname,'05:00:00',32,'230GB',syscall)
    print('sbatch '+runfile)
    os.system('sbatch '+runfile)
    os.chdir('../')

#     ch0 = prefix.split('-')[0]
#     jobname = 'CONV'+ch0
#     runfile = 'SCRIPTS/slurm_conv_'+prefix+'.sh'
#     logfile = 'LOGS/slurm_conv_'+prefix+'.log'
#     syscall = 'singularity exec /users/ianh/containers/oxkat-0.41.sif python3 convolve_channels.py /*'+prefix+'/out*'
#     write_slurm(runfile,logfile,jobname,'05:00:00',32,'230GB',syscall)
#     print('sbatch '+runfile)


#!/usr/bin/env python
# ian.heywood@physics.ox.ac.uk


import numpy
import os
import glob


def write_casa(cubename,fitsname,casafile):
    f = open(casafile,'w')
    f.writelines(['import os\n',
        'ia.imageconcat("'+cubename+'",infiles="*fits",relax=True,reorder=True)\n',
        'exportfits(imagename="'+cubename+'",fitsimage="'+fitsname+'")\n',
        'os.system("rm -rf '+cubename+'")\n'])
    f.close()


def write_slurm(container,runfile,logfile,jobname,time,cpus,mem,syscall):
    f = open(runfile,'w')
    f.writelines(['#!/bin/bash\n',
        '#file: '+runfile+':\n',
        '#SBATCH --job-name='+jobname+'\n',
        '#SBATCH --time='+time+'\n',
        '#SBATCH --partition=Main\n'
        '#SBATCH --ntasks=1\n',
        '#SBATCH --nodes=1\n',
        '#SBATCH --cpus-per-task='+str(cpus)+'\n',
        '#SBATCH --mem='+mem+'\n',
        '#SBATCH --output='+logfile+'\n',
        'SECONDS=0\n',
        syscall+'\n',
        'echo "****ELAPSED "$SECONDS" '+jobname+'"\n'])
    f.close()


container = '/users/ianh/containers/oxkat-0.41.sif'
rootdir = os.getcwd()
chans = 384
fitslist = sorted(glob.glob(rootdir+'/images/*image.fits'))

ptgs = sorted(glob.glob('*/out*/pony.*/filtered'))

j = 0


for ptg in ptgs:
    os.chdir(ptg)
    fitslist = sorted(glob.glob('*filtered.fits'))
    nfits = len(fitslist)
    start_chan = fitslist[0].split('-image')[0].split('-')[-1]
    end_chan = fitslist[-1].split('-image')[0].split('-')[-1]
    cubename = (fitslist[0].split('_40asec')[0]+'_40asec_'+start_chan+'-'+end_chan+'.image.cube.im').split('/')[-1]
    fitsname = (fitslist[0].split('_40asec')[0]+'_40asec_'+start_chan+'-'+end_chan+'.image.cube.fits').split('/')[-1]
    casafile = 'casa_make_cube_'+str(j)+'.py'
    slurmfile = 'slurm_make_cube_'+str(j)+'.sh'
    logfile = 'slurm_make_cube_'+str(j)+'.log'
    syscall = 'singularity exec '+container+' casa -c '+casafile+' --nologger --log2term --nogui'
    write_casa(cubename,fitsname,'casa_make_cube_'+str(j)+'.py')
    write_slurm(container,
        slurmfile,
        logfile,
        'MASK_'+str(j).zfill(3),
        '03:00:00',
        8,
        '60GB',
        syscall)
#        os.system('sbatch '+slurmfile)
    os.chdir(rootdir)
    j+=1

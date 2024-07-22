#!/usr/bin/env python
# ian.heywood@physics.ox.ac.uk


import glob
import os
import sys
import generators as gen


myms = glob.glob('*.mms')
if len(myms) == 0:
    print('No MMS found, please check')
    sys.exit()
else:
    myms = myms[0].rstrip('/')


if 'LOW' in myms:
    band = 'LOW'
    low_chans = [0]
    high_chans = [1818]
    n_chans = [1818]
elif 'MID' in myms:
    band = 'MID'
    low_chans = [0,2200,4400,6600]
    high_chans = [2200,4400,6600,8805]
    n_chans = [2200,2200,2200,2205]
elif 'HIGH' in myms:
    band = 'HIGH'
    low_chans = [0]
    high_chans = [1531]
    n_chans = [1531]


CWD = os.getcwd()+'/'
container = '/users/ianh/containers/oxkat-0.42.sif'
cube_dir = CWD+'CUBE/'
scripts_dir = CWD+'SCRIPTS/'
logs_dir = CWD+'LOGS/'


for mydir in [cube_dir,scripts_dir,logs_dir]:
    if not os.path.isdir(mydir): os.mkdir(mydir)


submit_file = 'submit_make_cube_jobs.sh'
kill_file = 'kill_make_cube_jobs.sh'
master_job_list = []


print('----------------------------+---------------------------------------')
print('Found                       : %s' % myms)
print('Sub-band                    : %s' % band)
print('Channel groups              : %s' % low_chans)
print('                            : %s' % high_chans)
print('----------------------------+---------------------------------------')


f = open(submit_file,'w')
f.write('#!/usr/bin/env bash\n')


for i in range(0,len(low_chans)):

    image_name = cube_dir+'/img_'+myms+'_cube'+str(i)+'_r0p5'
    
    tempdir = 'temp_'+str(i).zfill(3)
    if not os.path.isdir(tempdir): os.mkdir(tempdir)
    
    cube_name = 'CUBE'+str(i)
    cube_runfile = scripts_dir+'slurm_'+cube_name+'.sh'
    cube_logfile = cube_runfile.replace('.sh','.log').replace(scripts_dir,logs_dir)
    cube_syscall = gen.image_cube(container,myms,image_name,low_chans[i],high_chans[i],n_chans[i],tempdir)
    gen.write_slurm(cube_runfile,cube_logfile,cube_name,'24:00:00',32,'230GB',cube_syscall)
    run_command = cube_name+"=`sbatch "+cube_runfile+" | awk '{print $4}'`\n"
    f.write(run_command)
    master_job_list.append(cube_name)

    pbcor_name = 'PBCOR'+str(i)
    pbcor_runfile = scripts_dir+'slurm_'+pbcor_name+'.sh'
    pbcor_logfile = pbcor_runfile.replace('.sh','.log').replace(scripts_dir,logs_dir)
    pbcor_syscall = 'singularity exec '+container+' python3 aux/pbcor_parallel.py cube'+str(i)
    gen.write_slurm(pbcor_runfile,pbcor_logfile,pbcor_name,'04:00:00',16,'115GB',pbcor_syscall)
    run_command = pbcor_name+"=`sbatch -d afterok:$"+cube_name+" "+cube_runfile+" | awk '{print $4}'`\n"
    f.write(run_command)
    master_job_list.append(pbcor_name)

f.write('\n# --------------------------------------------------\n')
f.write('# Kill commands\n')
for job_id in master_job_list:
    if job_id == master_job_list[0]:
        kill = 'echo "scancel $'+job_id+' #'+job_id+'" > '+kill_file+'\n'
    else:
        kill = 'echo "scancel $'+job_id+' #'+job_id+'" >> '+kill_file+'\n'
    f.write(kill)
f.close()
print('Submit jobs                 : source %s' %submit_file)
print('----------------------------+---------------------------------------\n')


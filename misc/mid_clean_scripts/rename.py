import numpy
import glob
import os

nopes = ['LOGS',
    'MID_r0p0_beams',
    'MID_r0p0_clean_mosaic',
    'MID_r0p0_dirty_mosaic',
    'MID_40asec_beams',
    'MID_40asec_clean_mosaic',
    'SCRIPTS',
    'taper']

cwd = os.getcwd()
sets = []
scan = os.scandir(cwd)
for ii in scan:
    if ii.is_dir() and ii.name not in nopes: sets.append(ii.name)
scan.close()

#COSMOS_1/output_1617809470_sdp_l0_COSMOS_1_MID_0001-0384.mms_CL_07_00/img_1617809470_sdp_l0_COSMOS_1_MID_0001-0384.mms_40asec-0383-image.pbcor.fits
#suffixes = ['psf.fits','model.fits','dirty.fits','residual.fits','image.conv.fits']


suffixes = ['psf.fits','residual.fits','model.fits','dirty.fits','residual.fits','image.conv.fits','image.conv.pbcor.fits','image.conv.wt.fits']

# DO NOT USE on 0001
# 0000 ---> 0001, then 0001 --> 0002, etc. until only the final file remains
# use temporary destination folder and cp 

print(sets)

for ss in sets:
    print(ss)
#    ch0 = int(ss.split('_')[-1].split('-')[0])
#    ch1 = int(ss.split('_')[-1].split('-')[1])
#    chans = numpy.arange(ch0,ch1+1)
#    print(ss,chans)
    subsets = sorted(glob.glob(ss+'/output_*'))
    for subset in subsets:
        ch0 = int(subset.split('MID_')[-1].split('-')[0])
        subset_chans = []
        tempdir = subset+'/sequence'
        if not os.path.isdir(tempdir): os.mkdir(tempdir)
        fitslist = sorted(glob.glob(subset+'/*image.fits'))
        for fitsfile in fitslist:
            fitschan = int(fitsfile.split('40asec-')[-1].split('-')[0])
            subset_chans.append(fitschan)
        subset_chans = numpy.array(subset_chans)+ch0
        for i in range(0,len(fitslist)):
            newimgname = fitslist[i].split('40asec')[0]+'40asec-'+str(subset_chans[i]).zfill(4)+'-image.fits'
            newimgname = tempdir+'/'+newimgname.split('/')[-1]
            if not os.path.isfile(newimgname):
                syscall = 'mv '+fitslist[i]+' '+newimgname
                print(syscall)
                os.system(syscall)
#            os.rename(fitslist[i],newimgname)
            for suffix in suffixes:
                ff = fitslist[i].replace('image.fits',suffix)
                if os.path.isfile(ff):
                    newname = ff.split('40asec')[0]+'40asec-'+str(subset_chans[i]).zfill(4)+'-'+suffix
                    newname = tempdir+'/'+newname.split('/')[-1]
                    if not os.path.isfile(newname):
                        syscall = 'mv '+ff+' '+newname
                        print(syscall)
                        os.system(syscall)
#                    os.rename(ff,newname)
                # else:
                #     syscall = 'mv '
                #     print(i,subset_chans[i],ff)

        print('')


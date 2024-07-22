import os

runfiles = ['COSMOS_1/SCRIPTS/slurm_image_cube_1617809470_sdp_l0_COSMOS_1_MID_0001-0384.mms.sh',
	'COSMOS_2/SCRIPTS/slurm_image_cube_1619963656_sdp_l2.full_COSMOS_2_MID_0001-0384.mms.sh',
	'COSMOS_3/SCRIPTS/slurm_image_cube_1622376680_sdp_l2.full_COSMOS_3_MID_0001-0384.mms.sh',
	'COSMOS_4/SCRIPTS/slurm_image_cube_1621083675_sdp_l2.full_COSMOS_4_MID_0001-0384.mms.sh',
	'J0958+0201/SCRIPTS/slurm_image_cube_1586274966_sdp_l2.full_J0958+0201_MID_0001-0384.mms.sh',
	'J0958+0222/SCRIPTS/slurm_image_cube_1586188138_sdp_l2.full_J0958+0222_MID_0001-0384.mms.sh',
	'J0959+0151/SCRIPTS/slurm_image_cube_1586705155_sdp_l2.full_J0959+0151_MID_0001-0384.mms.sh',
	'J0959+0212/SCRIPTS/slurm_image_cube_1585413022_sdp_l2.full_J0959+0212_MID_0001-0384.mms.sh',
	'J0959+0233/SCRIPTS/slurm_image_cube_1586016787_sdp_l2.full_J0959+0233_MID_0001-0384.mms.sh',
	'J1000+0151/SCRIPTS/slurm_image_cube_1585671638_sdp_l2.full_J1000+0151_MID_0001-0384.mms.sh',
	'J1000+0212/SCRIPTS/slurm_image_cube_1587911796_sdp_l2_J1000+0212_MID_0001-0384.mms.sh',
	'J1000+0233/SCRIPTS/slurm_image_cube_1585844155_sdp_l2.full_J1000+0233_MID_0001-0384.mms.sh',
	'J1001+0151/SCRIPTS/slurm_image_cube_1586791316_sdp_l2.full_J1001+0151_MID_0001-0384.mms.sh',
	'J1001+0212/SCRIPTS/slurm_image_cube_1585498873_sdp_l2.full_J1001+0212_MID_0001-0384.mms.sh',
	'J1001+0233/SCRIPTS/slurm_image_cube_1585928757_sdp_l2.full_J1001+0233_MID_0001-0384.mms.sh']

for rr in runfiles:
	wd = rr.split('/')[0]
	slurm = '/'.join(rr.split('/')[1:])
	print(wd,slurm)
	os.chdir(wd)
	os.system('sbatch '+slurm)
	os.chdir('../')

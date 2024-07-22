import subprocess


target = 'J1001+0233'
opms = '1585928757_sdp_l2.full.ms'

rdb_link = 'https://archive-gw-1.kat.ac.za/1585928757/1585928757_sdp_l0.full.rdb?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJpc3MiOiJrYXQtYXJjaGl2ZS5rYXQuYWMuemEiLCJhdWQiOiJhcmNoaXZlLWd3LTEua2F0LmFjLnphIiwiaWF0IjoxNjc2NDU5OTQ1LCJwcmVmaXgiOlsiMTU4NTkyODc1NyJdLCJleHAiOjE2NzcwNjQ3NDUsInN1YiI6Imlhbi5oZXl3b29kQGdtYWlsLmNvbSIsInNjb3BlcyI6WyJyZWFkIl19.ZJlXMBbXR8jIHsyjJFkA49fQL16S6ZV_vcI-DpJ-f_HBf32EQWKsxJBUo1_CGLRNPpod2HfzQo4IhvAoVFWq6Q'

syscall = 'mvftoms.py -v -f --applycal all --flags cam,data_lost,ingest_rfi '
syscall += '--target '+target+' '
syscall += '-o '+opms+' '
syscall += rdb_link+' '
syscall = syscall.split()

success = False

i = 0
while not success:
    print('Run %s ' % str(i))
    result = subprocess.run(syscall, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.stdout.split()[-6] != 'socket.timeout:':
        success = True
    i += 1

print('Final restart count %s' % str(i))
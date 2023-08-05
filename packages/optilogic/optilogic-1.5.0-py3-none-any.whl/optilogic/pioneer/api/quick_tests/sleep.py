import sys
import time
import random
from optilogic import pioneer

pioneer.Job.print_add_record_calls = True

stime = time.time()
print('start time', stime)
sys.stderr.write('stderr is now True\n')

rsecs = random.randint(300,600)
print(f'\n\nforecast runtime {rsecs} seconds')
pioneer.Job.add_record(key='eta', message=f'{rsecs} seconds')
for sec in range(rsecs):
    etime = time.time() - stime
    if sec % 5 == 0:
        print(f'elapsed time {etime}')
    if sec % 15 == 0:
        pioneer.Job.add_record(key=f'key_{sec}_etime', message=f'value {etime}')
    time.sleep(1)

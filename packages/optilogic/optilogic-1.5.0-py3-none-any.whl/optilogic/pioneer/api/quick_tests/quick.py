import sys
from optilogic import pioneer

pioneer.Job.print_add_record_calls = True

print('going to be quick')
sys.stderr.write('stderr is now True\n')
pioneer.Job.add_record(key='quick', message='done done')
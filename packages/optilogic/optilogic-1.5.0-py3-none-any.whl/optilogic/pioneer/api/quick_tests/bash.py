'''
execute a bash command

Usage:
  bash.py <cmd>
  bash.py (-h | --help)

Examples:
  bash.py 'ls -al'
  bash.py bash.py 'ls -al | grep quick'

Options:
  -h, --help
'''

from os import system
from docopt import docopt

if __name__ == '__main__':
    args = docopt(__doc__)
    print(args)
    system(args['<cmd>'])
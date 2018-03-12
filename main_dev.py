import sys
import os
       
if not os.path.exists('./logs'):
    os.makedirs('./logs')
         
import config as cfg
from timeline_dev import run_timeline


def main(method):
    methods = ['timeline', 'reply', 'stat']
    method = method.strip('--')

    if method not in methods:
        print('ERROR: Invalid method. Please include a valid method.')
        sys.exit(1)
    elif method == 'timeline':
        run_timeline(cfg.AUTH)
    

if __name__ == '__main__':
    # Outfile Handling #
    if not os.path.exists('./rawdata/original'):
        os.makedirs('./rawdata/original')
    if not os.path.exists('./rawdata/reply'):
        os.makedirs('./rawdata/reply')
    
    method = sys.argv[1]
    main(method)

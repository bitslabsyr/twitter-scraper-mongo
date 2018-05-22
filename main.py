import sys
import os
       
if not os.path.exists('./logs'):
    os.makedirs('./logs')
   
from timeline import run_timeline


if __name__ == '__main__':
    
    if len(sys.argv) <> 2:
        print('Example: python main.py [INPUT FILE e.g. input.txt]')
        sys.exit(1)
    
    input_filename = sys.argv[1].strip()
    run_timeline(input_filename)

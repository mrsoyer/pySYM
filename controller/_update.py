import os
import subprocess
import sys

def run(request,SYM):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r' 'requirements.txt'])

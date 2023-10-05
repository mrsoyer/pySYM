import os
import subprocess
import sys

def run(request):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r' 'requirements.txt'])

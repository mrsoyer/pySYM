import sys
import subprocess
import os

# implement pip as a subprocess:
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r' 'requirements.txt'])
os.system('''echo 'alias sym="python3 $HOME/pySYM/cli.py"' >> ~/.bash_profile''')
os.system('''echo 'alias sym="python3 $HOME/pySYM/cli.py"' >> ~/.zshrc''')




import sys
import subprocess
import os

def setup_django(manage_folder='.'):
    try:
        l=''
        if manage_folder!='.':
            l += 'cd '+  manage_folder+';'
        l+='python manage.py check'
        print(l)
        subprocess.check_call(l,shell=True)
        exit(0)
    except Exception:
        exit(-1)


if __name__=='__main__':
    if len(sys.argv)>1:
        setup_django(sys.argv[1])
    else:
        setup_django()

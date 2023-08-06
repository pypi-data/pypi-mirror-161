#!/usr/bin/python3
#************************************************************************
# Copyright 2021 O7 Conseils inc (Philippe Gosselin)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#************************************************************************

import os 
import signal 
import subprocess


#*************************************************
# 
#*************************************************
def get_process_children(pid):

    p = subprocess.Popen('ps --no-headers -o pid --ppid %d' % pid, shell = True,
              stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout, stderr = p.communicate()
    return [int(p) for p in stdout.split()]



#*************************************************
# Run a process with a timeout
#*************************************************
def run(args, cwd = None, shell = False, timeout = None, env = None):

    # Ref: https://docs.python.org/3/library/subprocess.html
    proc = subprocess.Popen(args, cwd=cwd, shell=shell, env=env, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    
    try: 
        stdout, stderr = proc.communicate(timeout=timeout)

    except FileNotFoundError:
        print(f"ERROR: not able to found execution file: {args}")
        return -8, '', ''

    except subprocess.TimeoutExpired:
        # print (f"Need to kill PID {proc.pid}, os.name {os.name} sys.platform {sys.platform}")
        
        if os.name == 'nt':
            subprocess.run(f"taskkill /F /T /PID {proc.pid} > taskkill.log" , shell=True)
        else:
            proc.kill()
            proc.communicate()

        return -9, '', ''

    return proc.returncode, stdout, stderr


if __name__ == '__main__':

    print('Sleeping for 4 sesonds')
    test = run('sleep 4', shell = True, timeout = 3)
    print(test)
    print('Sleeping for 2 sesonds')
    test = run('sleep 2', shell = True)
    print(test)
    
#!/usr/bin/python3

# Copyright 2020 The SODA Authors.
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

import sys, os, shutil, subprocess
from subprocess import CalledProcessError
import traceback as tb
from helper import *

sim_source_path = ''
sim_etc_dir = '/etc/dolphin'
sim_var_dir = '/var/lib/dolphin'
conf_file = os.path.join(sim_etc_dir, 'dolphin.conf')
proj_name = 'SIM'

def _activate():
    path_to_activate = os.getcwd() + '/' + proj_name + '/bin/activate'
    print(path_to_activate)
    command = '. ' +  path_to_activate    
    os.system(command) 

# Initialize the settings first
def init():
    #_activate()
    pass
    
def create_sim_db():
    try:
        db_path = os.path.join(sim_source_path, 'installer', 'create_db.py')
        subprocess.check_call(['python3', db_path, '--config-file', conf_file])
    except CalledProcessError as cpe:
        logger.error("Got CPE error [%s]:[%s]" % (cpe, tb.print_exc()))
        return
    logger.info('db created ')
        
def start_api():
    api_path = os.path.join(sim_source_path, 'dolphin', 'cmd', 'api.py')
    command = 'python3 ' + api_path + ' --config-file ' + conf_file  + ' &'
    os.system(command)
    #subprocess.call(['python3', api_path, '--config-file', conf_file], shell=True)
    logger.info("process_started")
    
    
def install_sim():
    python_setup_comm = ['build', 'install'] 
    req_logs = os.path.join(sim_log_dir, 'requirements.log')
    command='pip3 install -r requirements.txt >' + req_logs+ ' 2>&1'
    logger.info("Executing [%s]", command)
    os.system(command)
    
    setup_file=os.path.join(sim_source_path, 'setup.py')
    for command in python_setup_comm:
        try:
            command = 'python3 ' + setup_file + ' ' + command + ' >>' + logfile
            logger.info("Executing [%s]", command)
            os.system(command)
        except CalledProcessError as cpe:
            logger.error("Got CPE error [%s]:[%s]" % (cpe, tb.print_exc()))
            return

def main():
    global sim_source_path
    cwd = os.getcwd()
    logger.info("Current dir is %s" % (cwd))
    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    sim_source_path = os.path.join(this_file_dir, "../" )

    logger.info("sims [%s]" % (sim_source_path))
    os.chdir(sim_source_path)
    logger.info(os.getcwd())

    # create required directories
    create_dir(sim_etc_dir)
    create_dir(sim_var_dir)

    # Copy required files
    # Copy api-paste.ini
    ini_file_src = os.path.join(sim_source_path, 'etc', 'dolphin', 'api-paste.ini')
    ini_file_dest = os.path.join(sim_etc_dir, 'api-paste.ini')
    copy_files(ini_file_src, ini_file_dest)

    # Copy the conf file
    conf_file_src = os.path.join(sim_source_path, 'etc', 'dolphin', 'dolphin.conf')
    copy_files(conf_file_src, conf_file)

    # install
    install_sim()

    # create db
    create_sim_db()

    # start
    start_api()
if __name__ == "__main__":
    main()

import subprocess
import unittest
import os
import glob
# from johnsnowlabs.utils.venv_utils import *
import sys


def process_was_succ(result: subprocess.CompletedProcess) -> bool:
    if result.stderr:
        return False
    return True


def log_process(result: subprocess.CompletedProcess):
    print("______________STDOUT:")
    print(result.stdout.decode())
    print("______________STDERR:")
    print(result.stderr.decode())


class VenvWrapper:
    venv_path: str
    py_exec_path: str

    def __init__(self, venv_path, create_if_missing=True, auto_install_pip=True):
        self.venv_path = venv_path
        self.py_exec_path = self.glob_py_exec_from_venv(venv_path, False)
        if not self.py_exec_path:
            # Create a venv for testing if not exist
            if create_if_missing:
                self.create_venv(venv_path)
            self.py_exec_path = self.glob_py_exec_from_venv(venv_path, True)
            if auto_install_pip:
                self.install_pip_if_missing()

    def create_venv(self, venv_target_dir, py_exec_path=sys.executable, log=True):
        # Create venv with given or current sys.exectuable
        r = subprocess.run([py_exec_path, '-m', 'venv', f'{venv_target_dir}'], capture_output=True)
        if log:
            log_process(r)
        return process_was_succ(r)

    def destroy_venv(self, venv_dir):
        # TODO OS AGNOSTIC and use self.
        # os.system(f'rm -r {venv_dir}')
        pass
    def glob_py_exec_from_venv(self,venv_dir, raise_except=True):
        py_exec_path = glob.glob(f'{venv_dir}/bin/*python*')
        if len(py_exec_path) == 0:
            if raise_except:
                raise Exception(f"Could not find Python Executable in venv dir = {venv_dir} "
                                f"Please Specify correct path manually")
            else:
                return False

        py_exec_path = py_exec_path[0]
        return py_exec_path

    def is_pip_in_venv(self, log=True):
        r = subprocess.run([self.py_exec_path, '-m', 'pip'], capture_output=True)
        if log:
            log_process(r)
        return process_was_succ(r)

    def install_pip_in_venv(self, log=True):
        pip_url = 'https://bootstrap.pypa.io/get-pip.py'
        os.system(f'! wget {pip_url}')
        r = subprocess.run([self.py_exec_path, 'get-pip.py'], capture_output=True)
        if log:
            log_process(r)
        return process_was_succ(r)

    def install_pip_if_missing(self):
        if not self.is_pip_in_venv():
            if not self.install_pip_in_venv():
                raise Exception(f'Could not find or setup pip in venv at  {self.py_exec_path}')

    def install_to_venv(self, pypi_name, log=True):
        r = subprocess.run([self.py_exec_path, '-m', 'pip', 'install', pypi_name], capture_output=True)
        if log:
            log_process(r)
        return process_was_succ(r)

    def uninstall_from_venv(self, pypi_name, log=True):
        r = subprocess.run([self.py_exec_path, '-m', 'pip', 'uninstall', pypi_name, '-y'], capture_output=True)
        if log:
            log_process(r)
        return process_was_succ(r)

    def is_lib_in_venv(self, module_name, log=True):
        r = subprocess.run([self.py_exec_path, '-c', f'import {module_name}'], capture_output=True)
        if log:
            log_process(r)
        return process_was_succ(r)

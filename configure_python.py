# setup a virtual environment with the proper packages for running DICE simulations

from __future__ import print_function
import subprocess
import sys
import os

if sys.version_info < (3, 0):
    version_str = '.'.join(str(x) for x in sys.version_info[:3])
    print(f"Must use Python 3, you're using version {version_str}")
    sys.exit(0)

import venv
from types import SimpleNamespace

PACKAGES = [
    'numpy',
    'pandas',
    'scipy'
]

done_msg = """
====================================================================================

\033[32;1mEverything is set up!\033[0m

To get started, you must first activate your Python virtual environment. You can
do this by using your terminal to run the command

	\033[1m{}\033[0m

"""

remote_exec_fix_msg = """
===================================================================================

\033[31;1mError!\033[0m

It looks like you don't have the right permissions to create a virtual environemt.
To configure Python properly, please open a PowerShell prompt as administrator and run:

    \033[1mSet-ExecutionPolicy -Scope CurrentUser RemoteSigned\033[0m

For details on why this is necessary, please visit:

    \033[4mhttps://www.stanleyulili.com/powershell/solution-to-running-scripts-is-disabled-on-this-system-error-on-powershell/\033[0m
    \033[4mhttps://tecadmin.net/powershell-running-scripts-is-disabled-system/\033[0m
"""

class DICEBuilder(venv.EnvBuilder):
    def post_setup(self, context: SimpleNamespace) -> None:
        is_windows = sys.platform == 'win32'

        if is_windows:
            python_exe = os.path.join(context.bin_path, 'python.exe')
        else:
            python_exe = os.path.join(context.bin_path, 'python')

        cmd = [python_exe, '-m', 'pip', 'install', '--upgrade']
        cmd.extend(['pip', 'setuptools'])

        # install the right packages
        cmd.extend(PACKAGES)

        subprocess.check_call(cmd)

        # ensure everything runs properly on windows
        if is_windows:
            exec_policy = subprocess.run(
                'powershell Get-ExecutionPolicy', shell=True, capture_output=True
            )
            assert (
                exec_policy.returncode == 0
            ), 'Unable to check execution level for Powershell'

            policy = exec_policy.stdout.decode('utf-8').strip()
            if policy.lower() in ['default', 'restriced', 'undefined']:
                print(remote_exec_fix_msg)
                sys.exit(1)


# setup environment
if __name__ == '__main__':
    if sys.platform == 'win32':
        os.system('') # enable escape codes for colorful output on windows

    NAME = 'DICE'

    DICEBuilder(
        symlinks=(os.name != 'nt'),
        with_pip=True,
    ).create(NAME)

    print(
        done_msg.format(
            f".\\{NAME}\\Scripts\\activate"
            if sys.platform == 'win32'
            else f'source {NAME}/bin/activate'
        )
    )

from typing import List
import os, subprocess

from aicmder.commands import register, _commands
from aicmder.commands.utils import _command_prefix as cmd


@register(name='{}.stop'.format(cmd), description='Stop serving.')
class StopCommand:
    def execute(self, argv: List) -> bool:
        print(argv)
        for process in argv:
            shell_cmd = "ps -ef|grep " + process + "|grep -v grep| awk '{print $2}'| xargs kill -9"
            print(shell_cmd)
            subprocess.check_output(shell_cmd, shell = True)
        os.system("ps -ef|grep aicmder|grep -v grep| awk '{print $2}'| xargs kill -9")
        return True
# -*- coding: utf-8 -*-

import os
import sys
from subprocess import check_output

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))
sys.path.append(os.path.join(parent_folder_path, "plugin"))


from flowlauncher import FlowLauncher


class Vagrant(FlowLauncher):
    def query(self, arguments: str):
        if not arguments:
            return self.list_vms()

    def list_vms(self):
        cmd = "vagrant global-status"
        output = check_output(cmd, shell=True).decode()
        return output


if __name__ == "__main__":
    Vagrant()

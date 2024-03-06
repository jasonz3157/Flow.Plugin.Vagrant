# -*- coding: utf-8 -*-

import os
import re
import sys
from collections import namedtuple
from subprocess import check_output

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))
sys.path.append(os.path.join(parent_folder_path, "plugin"))


from flowlauncher import FlowLauncher


class Vagrant(FlowLauncher):
    running_ico = "Images/running.png"
    stopped_ico = "Images/stopped.png"

    def query(self, arguments: str):
        if not arguments:
            if vms := self.list_vms():
                self.vms = vms
                return [
                    {
                        "Title": vm.id,
                        "SubTitle": f"{vm.name} {vm.state}",
                        "IcoPath": (
                            self.running_ico
                            if {vm.state} == "running"
                            else self.stopped_ico
                        ),
                    }
                    for vm in self.vms
                ]
            else:
                return

    def list_vms(self):
        cmd = ["vagrant", "global-status"]
        output = check_output(cmd, shell=True).decode().splitlines()
        vm = namedtuple("vm", ["id", "name", "state"])
        try:
            return [
                vm(id=n.split()[0], name=n.split()[1], state=n.split()[3])
                for n in output
                if re.match(r"^[a-z0-9]{7}\s", n)
            ]
        except Exception:
            return


if __name__ == "__main__":
    Vagrant()

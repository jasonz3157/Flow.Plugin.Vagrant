# -*- coding: utf-8 -*-

import os
import re
import subprocess
import sys
from collections import namedtuple

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))
sys.path.append(os.path.join(parent_folder_path, "plugin"))


from flowlauncher import FlowLauncher, FlowLauncherAPI


class Vagrant(FlowLauncher):
    # running saved poweroff

    def query(self, arguments: str):
        if not arguments:
            if vms := self.list_vms():
                return [
                    {
                        "Title": vm.name.strip(),
                        "SubTitle": f"{vm.provider} {vm.id.strip()} ({vm.state.strip()})",
                        "IcoPath": f"Images/{vm.state.strip()}.png",
                        "jsonRPCAction": {
                            "method": "control_vm",
                            "parameters": [
                                vm.id.strip(),
                                "up" if vm.state.strip() != "running" else "suspend",
                            ],
                        },
                    }
                    for vm in vms
                ]
            else:
                return

        input_name = arguments.strip().split()[0]
        if vms := self.list_vms():
            if vm := [vm for vm in vms if vm.name.strip() == input_name][0]:
                msgs = []
                if vm.state.strip() == "running":
                    actions = ["suspend", "halt"]
                else:
                    actions = ["up"]
                for action in actions:
                    msgs.append(
                        {
                            "Title": f"{action.upper()} {vm.name.strip()}",
                            "SubTitle": f"{vm.id.strip()}",
                            "IcoPath": f"Images/{action}.png",
                            "jsonRPCAction": {
                                "method": "control_vm",
                                "parameters": [vm.id.strip(), action],
                            },
                        }
                    )
                return msgs
            else:
                return
        else:
            return

    def list_vms(self):
        cmd = ["vagrant", "global-status", "--prune"]
        _o = subprocess.check_output(cmd, shell=True)
        del _o
        output = subprocess.check_output(cmd[:2], shell=True).decode().splitlines()
        vm = namedtuple("vm", ["id", "name", "state", "provider"])
        try:
            return [
                vm(
                    id=n.split()[0],
                    name=n.split()[1],
                    state=n.split()[3],
                    provider=n.split()[2],
                )
                for n in output
                if re.match(r"^[a-z0-9]{7}\s", n)
            ]
        except Exception:
            return

    def control_vm(self, id, action):
        subprocess.run(["vagrant", action, id])
        return


if __name__ == "__main__":
    Vagrant()

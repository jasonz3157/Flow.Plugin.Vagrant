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


from flowlauncher import FlowLauncher


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
                                "up" if vm.state.strip() != "running" else "halt",
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
                    actions = ["suspend", "halt", "open dir"]
                else:
                    actions = ["up", "open dir"]
                for action in actions:
                    msgs.append(
                        {
                            "Title": action,
                            "SubTitle": f"{vm.name.strip()} {vm.id.strip()} {vm.path}",
                            "IcoPath": f"Images/{action}.png",
                            "jsonRPCAction": {
                                "method": "control_vm",
                                "parameters": [vm.id.strip(), action, vm.path],
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
        vm = namedtuple("vm", ["id", "name", "state", "provider", "path"])
        vms = []
        for line in output:
            try:
                groups = re.search(
                    r"^(?P<id>[a-z0-9]{7})\s+(?P<name>[a-z0-9]+)\s+(?P<prov>[a-z]+)\s+(?P<state>[a-z]+)\s+(?P<path>.*)$",
                    line,
                )
                vms.append(
                    vm(
                        id=groups.group("id"),
                        name=groups.group("name"),
                        state=groups.group("state"),
                        provider=groups.group("prov"),
                        path=groups.group("path"),
                    )
                )
                del groups
            except Exception:
                continue
        return vms

    def control_vm(self, id, action, path=None):
        if action == "open dir" and path:
            os.startfile(os.path.realpath(path))
        else:
            subprocess.run(["vagrant", action, id])


if __name__ == "__main__":
    Vagrant()

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
        if vms := self.list_vms():
            self.vms = vms
        else:
            return
        if not arguments:
            return [
                {
                    "Title": vm.name.strip(),
                    "SubTitle": f"{vm.id.strip()} ({vm.state.strip()})",
                    "IcoPath": f"Images/{vm.state.strip()}.png",
                    "jsonRPCAction": {
                        "method": "control_vm",
                        "parameters": [
                            vm.id.strip(),
                            "up" if vm.state.strip() != "running" else "suspend",
                        ],
                        "dontHideAfterAction": False,
                    },
                }
                for vm in self.vms
            ]

        input_name = arguments.strip().split()[0]
        if vm := [vm for vm in self.vms if vm.name.strip() == input_name][0]:
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
                            "dontHideAfterAction": False,
                        },
                    }
                )
            return msgs
        else:
            return

    def list_vms(self):
        cmd = ["vagrant", "global-status"]
        output = subprocess.check_output(cmd, shell=True).decode().splitlines()
        vm = namedtuple("vm", ["id", "name", "state"])
        try:
            return [
                vm(id=n.split()[0], name=n.split()[1], state=self.stat_vm(n.split()[0]))
                for n in output
                if re.match(r"^[a-z0-9]{7}\s", n)
            ]
        except Exception:
            return

    def stat_vm(self, id):
        """global-status has cache, use status id"""
        cmd = ["vagrant", "status", id]
        output = subprocess.check_output(cmd, shell=True).decode().splitlines()
        for n in output:
            try:
                grps = re.search(
                    "^([a-z0-9]{7})\s+([a-z0-9]+)\s+([a-z]+)\s+([a-z]+)", n
                )
                return grps.group(3)
            except Exception:
                continue
        else:
            return "unknown"

    def control_vm(self, id, action):
        subprocess.Popen(["vagrant", action, id], shell=True)
        return


if __name__ == "__main__":
    Vagrant()

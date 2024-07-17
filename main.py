# -*- coding: utf-8 -*-

import os
import re
import subprocess
import sys

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))
sys.path.append(os.path.join(parent_folder_path, "plugin"))

from flowlauncher import FlowLauncher


class Vagrant(FlowLauncher):
    # running saved poweroff
    # up suspend halt
    vms = []

    def list_vm(self, prune=False):
        cmd = "vagrant global-status --prune" if prune else "vagrant global-status"
        output = subprocess.check_output(cmd, shell=True).decode("utf-8")
        output_lines = output.splitlines()
        reg_vm = re.compile(
            r"(?P<id>[a-z0-9]{7})\s+(?P<name>\S+)\s+virtualbox\s+(?P<state>[a-z]+)\s+(?P<dir>.+)\s+"
        )
        all_vms = []
        for line in output_lines:
            m = reg_vm.search(line)
            try:
                assert m.groupdict()
            except Exception:
                continue
            else:
                all_vms.append(m.groupdict())
        self.vms = all_vms

    def control_vm(self, vm_id, action):
        subprocess.run(["vagrant", action, vm_id])

    def query(self, arguments: str):
        self.list_vm()
        # 没有参数时，获取当前 vm 列表
        if not arguments:
            return [
                {
                    "Title": _.get("name"),
                    "SubTitle": _.get("state") + ", " + _.get("id"),
                    "IcoPath": (
                        "Images/ok.png"
                        if _.get("state") == "running"
                        else "Images/notok.png"
                    ),
                }
                for _ in self.vms
            ] + [
                {
                    "Title": "刷新",
                    "SubTitle": "重新获取虚拟机列表及状态",
                    "IcoPath": "Images/reload.png",
                    "jsonRPCAction": {"method": "list_vm", "parameters": [True]},
                },
            ]
        if arguments in [_.get("name") for _ in self.vms]:
            vm = [_ for _ in self.vms if _.get("name") == arguments][0]
            if vm.get("state") == "running":
                actions = ["suspend", "halt"]
            else:
                actions = ["up"]
            return [
                {
                    "Title": f"{action.upper()} {arguments}",
                    "IcoPath": f"Images/{action}.png",
                    "jsonRPCAction": {
                        "method": "control_vm",
                        "parameters": [vm.get("id"), action],
                    },
                }
                for action in actions
            ]
        else:
            return []


if __name__ == "__main__":
    Vagrant()

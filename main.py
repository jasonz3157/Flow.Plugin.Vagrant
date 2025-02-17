# -*- coding: utf-8 -*-

import os
import re
import subprocess
import sys
import pickle

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))
sys.path.append(os.path.join(parent_folder_path, "plugin"))

from flowlauncher import FlowLauncher

state_map = {
    "running": "运行中",
    "poweroff": "已关机",
    "saved": "已暂停",
    "aborted": "已中止",
}
action_map = {
    "suspend": "暂停",
    "up": "启动",
    "halt": "关机",
}


class Vagrant(FlowLauncher):
    # running saved poweroff
    # up suspend halt
    pickle_file = os.path.join(parent_folder_path, "vms.pkl")

    def list_vm(self, prune=False):
        cmd = "vagrant global-status --prune" if prune else "vagrant global-status"
        output = subprocess.check_output(cmd, shell=True).decode("utf-8")
        output_lines = output.splitlines()
        reg_vm = re.compile(
            r"(?P<id>[a-z0-9]{7})\s+(?P<name>\S+)\s+virtualbox\s+(?P<state>[a-z\s]+)\s+(?P<dir>[A-Z].+)$"
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
        with open(self.pickle_file, "wb") as f:
            pickle.dump(all_vms, f)
        return all_vms

    def control_vm(self, vm_id, action):
        subprocess.run(["vagrant", action, vm_id])

    def open_dir(self, path):
        os.startfile(os.path.realpath(path))

    def query(self, arguments: str):
        # 没有参数时，获取当前 vm 列表
        if not arguments:
            return [
                {
                    "Title": _.get("name"),
                    "SubTitle": state_map.get(_.get("state"))
                    + " | "
                    + _.get("id")
                    + " | "
                    + _.get("dir").rstrip(),
                    "IcoPath": (
                        "Images/ok.png"
                        if _.get("state") == "running"
                        else "Images/notok.png"
                    ),
                    "jsonRPCAction": {
                        "method": "control_vm",
                        "parameters": [
                            _.get("id"),
                            "halt" if _.get("state") == "running" else "up",
                        ],
                    },
                }
                for _ in self.list_vm()
            ] + [
                {
                    "Title": "刷新",
                    "SubTitle": "重新获取虚拟机列表及状态",
                    "IcoPath": "Images/reload.png",
                    "jsonRPCAction": {"method": "list_vm", "parameters": [True]},
                },
            ]
        else:
            with open(self.pickle_file, "rb") as f:
                vms = pickle.load(f)
        if arguments in [_.get("name") for _ in vms]:
            vm = [_ for _ in vms if _.get("name") == arguments][0]
            if vm.get("state") == "running":
                actions = ["suspend", "halt"]
            else:
                actions = ["up"]
            return [
                {
                    "Title": f"{action_map.get(action)} {arguments}",
                    "IcoPath": f"Images/{action}.png",
                    "jsonRPCAction": {
                        "method": "control_vm",
                        "parameters": [vm.get("id"), action],
                    },
                }
                for action in actions
            ] + [
                {
                    "Title": f"打开 {arguments} 的 Vagrant 目录",
                    "SubTitle": vm.get("dir").rstrip(),
                    "IcoPath": f"Images/open_dir.png",
                    "jsonRPCAction": {
                        "method": "open_dir",
                        "parameters": [vm.get("dir")],
                    },
                }
            ]
        else:
            return []


if __name__ == "__main__":
    Vagrant()

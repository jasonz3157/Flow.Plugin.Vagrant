# Flow.Plugin.Vagrant
A Flow plugin to up/halt/suspend vagrant vms.


## Usage
Trigger this plugin without any parameter, will listing virtual machines on your PC (by exec `vagrant global-status`, it may take several seconds).

<img src="https://s2.loli.net/2024/03/07/VnLzwYWUGSyX592.png" width=400>

> [!TIP]
> Click an item in this list:
> - If the virtual machine is RUNNING, will SUSPEND it.
> - If the virtual machine is not RUNNING, will UP it.

Use virtual machine's name as parameter:
- If the virtual machine is RUNNING, you'll see HALT and SUSPEND actions.

    <img src="https://s2.loli.net/2024/03/07/LcI7l9g8eVRhTbP.png" width=400>
- If the virtual machine is not RUNNING, you'll see UP action.

    <img src="https://s2.loli.net/2024/03/07/KLmpyD3PlFbJSuo.png" width=400>

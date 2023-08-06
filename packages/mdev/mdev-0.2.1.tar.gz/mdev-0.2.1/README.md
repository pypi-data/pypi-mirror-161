This is the MXOS meta tool, ``mdev`` written by Snow Yang.

https://www.mxchip.com

Installation
------------

Using pip:

``pip3 install mdev``

(Use ``pip3 uninstall mdev`` to uninstall it.)

Basic Usage
-----------

Build ``demos/helloworld`` and flash APP image into EMC3080.

``mdev build -m emc3080 demos/helloworld -f APP``

Additional Commands
-------------------

mdev has multiple sub-commands. 

For a list of available commands, run ``mdev -h``. Get help on a
command with ``mdev <command> -h``.

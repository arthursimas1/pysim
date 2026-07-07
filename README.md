# pySim

> *Fork with support for additional SIM cards*

pySim provides a set of Python tools for reading, decoding, browsing, and programming SIM, UICC, USIM, ISIM, HPSIM, and eUICC cards. It is a comprehensive tool for interacting with cellular network subscriber identity modules.

For full documentation, usage instructions, and examples, please consult the [official pySim documentation](https://downloads.osmocom.org/docs/latest/pysim/) and the [upstream project wiki](https://osmocom.org/projects/pysim/wiki).

## Changes in this Fork

This fork adds initial support for the following programmable SIM cards:

- **Oyeitimes R16**
- **SmartJac SMA-OT500B**

These changes implement the card models and file structures required to interact with the vendor-specific features of these cards.

## Out-of-Tree Maintenance

These modifications will be kept out-of-tree and are not planned to be submitted as a Pull Request to the upstream Osmocom project since I will not be able to continuously and actively maintain the code.

I am keeping these changes here for anyone who might find them useful :)

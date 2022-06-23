# SCABox Notebook

[Website](https://emse-sas-lab.github.io/SCAbox/)

## Overview

This repository contains a Python library to retrieve side-channel acquisition data from serial
port and perform an attack. It is part of the [SCABox](https://emse-sas-lab.github.io/SCAbox/) project.

- Library : tools to perform attack, serial communication and correlation
- Notebook: A demo notebook to launch simple SCA attacks

## Features

- Deserialization of acquisition data
- Acquisition data exports and imports
- CPA computation and statistics
- Leakage model hypothesis generation
- Leakage signal processing
- Advanced Encryption Standard (AES)

## Install

To install the repository you must clone the sources from GitHub and install the pip requirements

```
$ git clone https://github.com/emse-sas-lab/SCAbox-notebook
$ cd SCAbox-notebook
$ pip install -r requirements.txt
```

You might alternatively create a venv and install the requirements inside to use the project. 

## Compatibility

The project is compatible with Python 3.8 and latter. It is platform independent.

## Usage

### Library

The library provides a complete API to develop your own application.
In order to get started you can take a look at the examples and the reference.

### Notebook

The jupyter notebook can be started by installing jupyter lab and launching it from the SCAbox-sca repository.

```$ jupyter lab```

## More


SCABox is a project on the topic of side-channel analysis.
The goal of SCABox is to provide an efficient test-bench for FPGA-based side-channel analysis.

To know more about SCABox please visit our [website](https://emse-sas-lab.github.io/SCAbox/)

It provides a tutorials and a wiki about side-channel analysis.

SCABox is an open-source project, all the sources are hosted on GitHub

- [IP repository](https://github.com/emse-sas-lab/SCAbox-ip/)
- [Acquisition demo](https://github.com/emse-sas-lab/SCAbox-demo/)
- [Attack notebook](https://github.com/emse-sas-lab/SCAbox-notebook/)
- [SCAbox website](https://github.com/emse-sas-lab/SCAbox/)

Contributing
---------------------------------------------------------------

Please feel free to take part into SCABox project, all kind of contributions are welcomed.

The project aims at gathering a significant number of IP cores, crypto-algorithms and attack models 
in order to provide an exhaustive view of today's remote SCA threat.

Software and embedded improvements are also greatly welcomed. Since the project is quite vast and invovles
a very heterogeneous technical stack, it is difficult to maintain the quality with a reduced size team.  

License
---------------------------------------------------------------

All the contents of the SCABox project are licensed under the [MIT license](https://choosealicense.com/licenses/mit/) provided in each GitHub repository.

Copyright (c) 2020, EMSE

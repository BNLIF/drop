# About DROP

**D**ata **R**econstruction **O**ffline **P**ackage (**DROP**) is a collection of python toolbox to process and analyze the data collected by the Water-based Liquid Scintillator (WbLS) 1-tonne demonstrator. The binary decoder part is based on [CAENReader](https://github.com/tlangfor/CAENReader). The rest is developed according to the needs of BNL WbLS experiment, although it can be extended for other experiments.

![Data Flowchart](fig/data_flowchart.png)

The write access to this gitlab repoistory is grant to the WbLS group, or individual invitation-only. For developer & maintainer access, please contact Xin: <xxiang@bnl.gov>

# Getting Started

## Prerequisites

- Minimal Python3 Dependence:
  - uproot 4.1.0+
  - numpy 1.20.0+
  - pyYAML 5.1+
  - scipy, matplotlib (?+)

The full dependence is specified in requirememts.txt. 

## Installation and Setup

Download is open to public, but write permission is limited to BNL Intensity Frontier (BNLIF). 

Upgrade your pip (optional) to keep up to date with the dependence requirement:
```bash
pip install --upgrade pip
```

Create a virtual environment and activate it (optional):
```bash
python3 -m venv env
source env/bin/activate
```
If everything goes right, you are now in a virutial environment named `env`. If you do not know how to use virtial enironment, check out [here](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/). The same page also includes instruction on how to use `pip`. Both `venv` and `pip` are common tools for python users. 

Install the exact package dependence from requirement within your virtual env (optional).
```bash
pip install -r requirements.txt
```
Alternatively, you can pip install package one by one.

## Usage

Enter virtual environment if not already in (recommneded):
```
source env/bin/activate
```

Source the setup script in the drop directory. This will setup a few enviromental variables needed.
```bash
source setup.sh
```

To convert the raw data from binary file to root file, check out the rooter:
```bash
python src/raw_data_rooter.py --help
```
The rooter is fairly fast. Please check the global parameters (ALL CAP) defined at the beginning of this script; they may not affect the output root file, but may affect the processing speed and the accuracy of the print out. 


In your virtual env (recommended), check out the help manual. 

```bash
python src/run_drop.py --help
```

**Note: the pipeline is still under-development. For example, the RQ file saved into a root tree has a limited number of branches. **

When you're done, exit the virtual env:

```
deactivate
```

# Contributing

The master branch is not protected at the moment since the team is small. 

**Style**. I tried to follow [PEP 8](https://realpython.com/python-pep8/) convention as much as possible. Not a requirement, but I hope you do it too so that we have a clean and consistent coding style. For quick formating, you can use `black` or other automatic formating software. `black` will not change variable naming for you. 

Naming Conventions:
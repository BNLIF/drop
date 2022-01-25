# DROP

**D**ata **R**econstruction **O**ffline **P**ackage (**DROP**) is a python toolbox to process and analyze the data collected by the Water-based Liquid Scintillator (WbLS) 1-tonne demonstrator. The binary decoder part is based on [CAENReader](https://github.com/tlangfor/CAENReader). 

## About It

The access to this gitlab repoistory is grant to the WbLS group, or individual invitation-only. For developer & maintainer access, please contact Xin: <xxiang@bnl.gov>

## Getting Started

### Prerequisites

- Minimal Python3 Dependence:
  - uproot 4.1.0+
  - numpy 1.20.0+
  - pyYAML 5.1+
  - scipy, matplotlib (?+)

The full dependence is specified in requirememts.txt. 

### Installation and Setup

Download this repoistory:
```bash
git clone git@gitlab.com:WbLS/drop.git
```
You need to be added to WbLS gitlab group to download this repo. If you do not know how to use git, check out [here] (https://realpython.com/python-git-github-intro/).

Upgrade your pip (optional):
```bash
pip install --upgrade pip
```

Create a virtual environment and activate it (optional but recommended):
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

### Usage

In your virtual env (recommended), check out the help manual. 

```bash
python run_drop.py --help
```

**Note: the pipeline is still under-development. Ideally, the code should output a RQ in root file (or other format), but it does not have this functionality right now. You may have to call class methods individually. Sorry.**

When you're done, do the following to exit the virtual env:

```
deactivate
```

### Development

The master branch is not protected at the moment since the team is small. 

**Style**. I tried to follow [PEP 8](https://realpython.com/python-pep8/) convention as much as possible. Not a requirement, but I hope you do it too so that we have a clean and consistent coding style. For quick formating, you can use `black` or other automatic formating software. `black` will not change variable naming for you. 


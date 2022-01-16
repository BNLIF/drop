# DROP

**D**ata **R**econstruction **O**ffline **P**ackage (**DROP**) is a python toolbox to process and analyze the data collected by the Water-based Liquid Scintillator (WbLS) 1-tonne demonstrator. The binary decoder part is based on [CAENReader](https://github.com/tlangfor/CAENReader). 

## About It

The access to this gitlab repoistory is grant to the WbLS group, or individual invitation-only. For developer & maintainer access, please contact Xin: <xxiang@bnl.gov>

## Getting Started

### Prerequisites

- Python3 packages:
  - uproot4
  - numpy, matplotlib

### Installation

To download the repo, do

```bash
git clone git@gitlab.com:WbLS/drop.git
```

### Usage

The code is simple enough. No setup at the moment. Check out the help manual. 

```bash
python run_drop.py --help
```

### Development

The master branch is not protected at the moment since the team is small. 

**Style**. I tried to follow [PEP 8](https://realpython.com/python-pep8/) convention as much as possible. Not a requirement, but I hope you do it too so that we have a clean and consistent coding style. For quick formating, you can use `black` or other automatic formating software. `black` will not change variable naming for you. 


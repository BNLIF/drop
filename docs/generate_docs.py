"""
This script generates documentation in markdown files
"""

import sys
sys.path.insert(0, "../src/")

import run_drop
from lazydocs import generate_docs

# The parameters of this function correspond to the CLI options
generate_docs(["run_drop"], output_path="./")

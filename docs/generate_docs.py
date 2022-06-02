"""
This script generates documentation in markdown files
"""

import sys
sys.path.insert(0, "../src/")

import run_drop
import waveform
import pulse_finder
import rq_writer
import raw_data_rooter
import utilities
import yaml_reader
import caen_reader

from lazydocs import generate_docs

# The parameters of this function correspond to the CLI options
generate_docs(["raw_data_rooter", "run_drop", "waveform", "pulse_finder", "rq_writer", "yaml_reader", "utilities", "caen_reader"], output_path="./src_docs")


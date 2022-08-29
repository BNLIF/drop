# Example Analysis

This directory hold analysis example. The analysis may directly interact with DROP or perform analysis on the output RQ files.

- `uproot_example_v1.0.ipynb`: a bare minimal example of how to read our data into python via uproot. The raw data are available in root file. 
- `led.ipynb`: led calibration. We took LED runs at various intensity. This script loads multiple root files, find the intensity best for a PMT, and plot charge distributions.
- `data_quality_monitor`: it monitors muon data with a series of plot
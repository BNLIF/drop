import yaml
import numpy as np

"""
The following parameters do not change often. So hard coded here
"""
ADC_RATE_HZ=5e8 # Hz

class YamlReader():
    def __init__(self, file_path=None):
        self.file_path=file_path
        with open(file_path, "r") as f:
            try:
                self.data = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)

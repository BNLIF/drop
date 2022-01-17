import yaml
import numpy as np

class YamlReader():
    def __init__(self, file_path=None):
        self.file_path=file_path
        with open(file_path, "r") as f:
            try:
                self.data = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)

CONFIG = None # global variable, later filled with YamlReader::data type

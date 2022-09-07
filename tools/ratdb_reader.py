"""
Description:
Read a .RatDB file; it also read .geo file

The loaded info are saved in self.tables
"""

import re
import yaml

class RatDBReader:
    def __init__(self, file_path=None):
        """Constructor.
        RatDB (geo) file reader.

        Args:
            file_path: str. path to your file.ratdb.
        """
        if file_path is None:
            pass
        else:
            self.load(file_path)

    def load(self, file_path):
        """
        This function load ratdb file, and save them as a table. This function
        is called automatically in the constructor. You can call it again to update
        the table if file content has changed.

        Args:
            file_path: str
        """
        with open(file_path) as f:
            text = f.read()
            matches = re.findall(r"\{(.*?)\}", text, re.MULTILINE|re.DOTALL)
            f.close()

        self.tables = []
        self.n_tables=0
        for s in matches:
            s=re.sub(r"[^:]\/\/.*", "", s) # remove comments
            s=s.replace("\n", "") # remove newline
            s=s.replace(':', ': ') # yaml does not like key:value
            s=s.replace(",", ", ") # yaml does not like value1,key2
            s=s.replace("  ", " ") # I do not like extra empty
            s = "{%s}" % s # add { } back; ToDo: perserve {} in the first regex
            obj = yaml.safe_load( str(s) )
            self.n_tables += 1 # count num of tables
            self.tables.append(obj)
        return None


def test():
    """
    Example how to use RatDBReader. 
    """
    r = RatDBReader("../../BNL1TSim/data/BNL1T/PMTINFO.ratdb")
    for i in range(r.n_tables):
        t = r.tables[i]
        print('x=', t['x'], type(t['x']), type(t['x'][0]))
        print('y=', t['y'], type(t['y']), type(t['y'][0]))
        print('z=', t['z'], type(t['z']), type(t['z'][0]))

__title__ = "endurance"
__description__ = "Chromebook modification power-tool."
__author__ = "Timothy Pidashev"
__email__ = "pidashev.tim@gmail.com"
__copyright__ = "Copyright 2022-Present, Timothy Pidashev"
__license__ = "MIT"
__version__ = "0.1.0"
__status__ = "Prototype"

import argparse
import shutil

def run_as_module():
    columns = shutil.get_terminal_size().columns
    print(__description__.center(columns))

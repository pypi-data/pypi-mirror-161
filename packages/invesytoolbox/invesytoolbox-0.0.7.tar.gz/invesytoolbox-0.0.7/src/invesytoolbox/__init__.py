import sys
import os
from pathlib import Path

package_path = os.path.split(
    os.path.realpath(__file__)
)[0]

sys.path.append(package_path)

files = os.listdir(package_path)

for file in files:
    if not file.startswith('itb_'):
        continue

    module = Path(file).stem

    exec(
        f'from .{module} import *'
    )

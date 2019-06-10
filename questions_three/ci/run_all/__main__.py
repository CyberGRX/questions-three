import os
import sys

from .get_search_path import get_search_path
from .run_all import run_all

search_path = get_search_path()
if not os.path.exists(search_path):
    sys.stderr.write('Failed to locate "%s"\n' % search_path)
    exit(1)
exit(run_all(search_path))

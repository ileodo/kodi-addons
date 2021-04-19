import os
import sys

from adapter import A4KAdapter

sa = A4KAdapter()
sa.router(int(sys.argv[1]), sys.argv[2])

#!/usr/bin/env python
import os
import sys

if sys.version_info[0] < 3:
    sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), 'compat')))
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))


from pyls.__main__ import main

if __name__ == '__main__':
    sys.exit(main())

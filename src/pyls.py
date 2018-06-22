#!/usr/bin/env python
import os
import sys

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), 'py%s' % sys.version_info[0])))
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))


from pyls.__main__ import main

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3

""" PyBuild: the build system in Python """
""" It is a new build system written in Python, because y not? """
import libbuild
import os
import sys
import subprocess
from libptsd import *

# printf("Hello World!\n");

buildname = "build.py"

def lookForBuild(buildname):
    if os.path.exists(buildname):
        import build
        printf("We saw the `build.py` file inside your directory...\n");
        build.Build()
        # sys.exit()
    else:
        eprintf("ERROR: No `build.py` file found inside the current directory.")
        sys.exit(1)

lookForBuild(buildname)


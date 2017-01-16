# This is essentially just a launcher for the Shell

import spc
import sys

p = spc.Shell()
if len(sys.argv) > 1:
    p.openFile(sys.argv[1])

commands = []
if len(sys.argv) > 2:
    commands= [" ".join(sys.argv[2:])]
p.startShell(commands)

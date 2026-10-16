#!/usr/bin/env python3
import sys
import os

# Append current directory to path to ensure clean relative imports inside Termux
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import cli

if __name__ == "__main__":
    cli.main()

"""
Root-level convenience entry point.
Delegates to src/main.py so the project can be run from the repo root.
Usage: python main.py  OR  python main.py "your question"
"""
import runpy
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
runpy.run_module("main", run_name="__main__", alter_sys=True)

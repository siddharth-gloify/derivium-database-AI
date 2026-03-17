"""
Shared pytest fixtures and path setup.
"""
import sys
import os

# Make src/ importable in all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

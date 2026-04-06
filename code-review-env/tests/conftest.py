"""
Shared pytest configuration and fixtures for code-review-env tests.
"""
import sys
import os

# Ensure the project root is in the path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
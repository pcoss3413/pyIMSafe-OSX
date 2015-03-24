"""
Script for building the example.

Usage:
    python setup.py py2app --iconfile icon.icns
"""
from setuptools import setup

setup(
    app=['IMGui.py'],
    setup_requires=["py2app"],
)

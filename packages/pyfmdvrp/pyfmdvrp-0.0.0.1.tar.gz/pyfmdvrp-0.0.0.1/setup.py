# Pip_Package_Practice/setup.py
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pyfmdvrp',
    version='0.0.0.1',
    description='A python flexible multi-depot VRP (FMDVRP) simulator',
    author='Junyoung park',
    author_email='junyoungpark@kaist.ac.kr',
    long_description=long_description,
    python_requires='>=3.6',
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['docs', 'tests*', '__pycache__/']),
)
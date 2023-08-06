from pathlib import Path
from setuptools import setup, find_packages
import os

REQUIREMENTS_PATH = Path(__file__).resolve().parent / "requirements.txt"


with open(str(REQUIREMENTS_PATH), "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="pypi_example_akim",
    packages=find_packages(),
    version="0.0.2",
    description="Place for your ad",
    author="Akim",
    license="Absent",
    long_description=open("README.md").read(),
    install_requires=requirements,
    include_package_data=True,
    package_data={"pypi_example_akim": ["src/*"]},
)


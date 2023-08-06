import setuptools
from pathlib import Path

setuptools.setup(
    name="herbertpdf",
    version = 1.0,
    long_description= Path("ReadME.md").read_text() ,
    packages=setuptools.find_packages(exclude=["tests", "data"])
)
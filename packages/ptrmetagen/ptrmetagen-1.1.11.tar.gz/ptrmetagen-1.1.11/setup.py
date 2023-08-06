import pathlib
from setuptools import setup
from metagen import __version__

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="ptrmetagen",
    version=__version__,
    description="Package for generation of metastructures for Panter project",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/gisat-panther/ptr-metagen",
    author="Michal Opetal",
    author_email="michal.opletal@gisat.cz",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9"],
    packages=["metagen", "metagen.components", "metagen.utils", "metagen.config"],
    package_data = {'': ['metagen/config/config.yaml']},
    include_package_data=True,
    entry_points='''
       [console_scripts]
       metagen=metagen.config.cli:main
   ''',
    )

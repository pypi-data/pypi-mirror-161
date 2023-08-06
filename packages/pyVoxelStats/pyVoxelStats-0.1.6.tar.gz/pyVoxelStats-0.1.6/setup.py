from setuptools import setup, find_packages
import json

with open('pyVS/pkg_info.json') as fp:
    _info = json.load(fp)

setup(
    # Application name:
    name="pyVoxelStats",

    # Version number (initial):
    version=_info['version'],

    # Application author details:
    author="Sulantha Mathotaarachchi",
    author_email="sulantha.ms@gmail.com",

    # Packages
    packages=find_packages(),

    package_data = {'pyVS': ['data/*', 'pkg_info.json']},

    # Include additional files into the package
    include_package_data=True,

    # Details
    url=_info['url'],

    #
    # license="LICENSE.txt",
    description="Python implementation of the VoxelStats toolbox for neuroimage analysis",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "nibabel", "pandas", "numpy", "scipy", "numexpr",
        "pyminc",
        "statsmodels",
        "rpy2",
        "ipyparallel",
    ],
)

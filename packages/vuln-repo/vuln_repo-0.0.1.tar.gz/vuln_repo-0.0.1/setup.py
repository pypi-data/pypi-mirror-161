from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))
VERSION = '0.0.1'
DESCRIPTION = 'vulnerable repo'

# Setting up
setup(
    name="vuln_repo",
    version=VERSION,
    author="v1per",
    author_email="test@test.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['insecure-package==0.1.0'],
    keywords=['vulnerable', 'test'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
from setuptools import setup, find_packages
import codecs
import os
VERSION = '0.0.1'
DESCRIPTION = 'ZEBU free run'
LONG_DESCRIPTION = "ZEBU brocker without api"

# Setting up
setup(
    name="SASOzebu",
    version=VERSION,
    author="Gourav",
    author_email="kgourav@combiz.org",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['ZEBU', 'ZEBU api use'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
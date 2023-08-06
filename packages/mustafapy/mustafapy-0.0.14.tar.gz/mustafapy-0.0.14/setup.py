from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.14'
DESCRIPTION = 'GridSearchCV hyperparameters generation'
# Setting up
setup(
    name="mustafapy",
    version=VERSION,
    author="mustafasa (Mustafa Al Hamad)",
    author_email="<mustafa.alhamad.sa@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['sklearn', 'imblearn', 'pandas'],
    keywords=['python', 'sklearn', 'gridsearch', 'machine learning', 'automation', 'sockets'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
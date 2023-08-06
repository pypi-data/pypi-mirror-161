import setuptools
from setuptools import setup

from mypylib import __version__



with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='mypylib',
    version=__version__,

    url='https://github.com/williamchen180/mypylib',
    author='William Chen',
    author_email='williamchen180@gmail.com',

    packages=setuptools.find_packages(),
    package_data={'mypylib': ['data/alert.wav']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    dependencies=['mypylib', 'pandas', 'termcolor', 'requests', 'plotly', 'setuptools', 'matplotlib', 'numpy',
                'playsound', 'wheel', 'twine', 'cryptocode', 'line_notify', 'shioaji', 'pandasql', 'msgpack'],
)

"""A setuptools based setup module."""

import pathlib
from setuptools import setup, find_packages

from ac_websocket_server.constants import PROG, VERSION


# The text of the README file
README = (pathlib.Path(__file__).parent / "README.md").read_text()

setup(
    name=PROG,
    version=VERSION,
    description='Assetto Corsa Websockets Server',
    long_description=README,
    long_description_content_type="text/markdown",
    author='Mark Hannon',
    author_email='mark.hannon@gmail.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['websockets'],
)

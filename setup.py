# setup.py

from setuptools import setup, find_packages

setup(
    name='omnifact-cli',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'omnifact-cli=omnifact_cli.cli:cli',
        ],
    },
)
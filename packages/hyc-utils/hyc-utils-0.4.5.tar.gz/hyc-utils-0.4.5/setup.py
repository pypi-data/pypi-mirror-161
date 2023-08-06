from setuptools import setup, find_packages

setup(
    name='hyc-utils',
    version='0.4.5',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'torch',
        'tomli',
    ],
    extras_require={
        'dev': ['pytest','twine'],
    }
)

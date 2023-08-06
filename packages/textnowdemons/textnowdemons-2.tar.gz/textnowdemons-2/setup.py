from setuptools import setup, find_packages

setup(
    name='textnowdemons',
    version='2',
    author='the best',
    packages=find_packages('textnow'),
    package_dir={'': 'textnow'},
    install_requires=[
        'requests',
        'bs4'
    ]
)

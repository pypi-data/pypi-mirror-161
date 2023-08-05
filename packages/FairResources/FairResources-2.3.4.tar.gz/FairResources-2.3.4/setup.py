from setuptools import setup, find_packages
import os

current = os.getcwd()

setup(
    name='FairResources',
    version='2.3.4',
    description='Article Provider for Sources, Categorizer, Utils and more.',
    url='https://github.com/chazzcoin/FairResources',
    author='ChazzCoin',
    author_email='chazzcoin@gmail.com',
    license='BSD 2-clause',
    packages=find_packages(),
    package_dir={'res': 'FairResources'},
    package_data={
        'FairResources': ['*', '*.txt', '*.csv', '*.pickle', 'tokenizers/punkt/*.pickle', 'tokenizers/punkt/PY3/*.pickle']
    },
    install_requires=['fcore>=2.1.0'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
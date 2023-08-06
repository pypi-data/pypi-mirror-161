from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'Operating System :: MacOS',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='ioNERDSS',
    version='0.3.0',
    description='Package for analysing NERDSS inputs and outputs.',
    long_description='A python package for analysing inputs and outputs for NERDSS simulator, including generating input files for Platonic solids and output visualization, etc.',
    url='',
    author='Zixiu (Hugh) Liu',
    author_email='zliu140@jhu.edu',
    license='MIT',
    classifiers=classifiers,
    keywords='NERDSS Simulation, Analysis Tools',
    packages=find_packages(),
    install_requires=['numpy','pandas']
)

# To use a consistent encoding
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='solvency2-nlp',
    packages=find_packages(),
    version='0.1.0',
 	description='Experimental natural language processing projects with Solvency 2 documents',
	url='https://github.com/DeNederlandscheBank/solvency2-nlp.git',
    author='DeNederlandscheBank',
    python_requires='~=3.6',
    license='MIT/X',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Topic :: Office/Business',
        'Topic :: Text Processing :: Linguistic',
    ],
)

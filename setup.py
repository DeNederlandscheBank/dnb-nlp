
# To use a consistent encoding
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

requirements = [ ]

setup(
    name='src',
    packages=find_packages(),
    version='0.1.0',
 	description='Experimental natural language processing projects with central bank and supervisory documents',
	url='https://github.com/DeNederlandscheBank/dnb-nlp',
	install_requires=requirements,
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

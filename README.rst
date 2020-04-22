=============
dnb-nlp
=============

.. image:: https://img.shields.io/badge/License-MIT/X-blue.svg
        :target: https://github.com/DeNederlandscheBank/solvency2-nlp/blob/master/LICENSE
        :alt: License

Experimental natural language processing projects with central bank and supervisory documents

In this repository we publish our progress in natural language processing with documents.

Installation
============

Online installation
-------------------

Clone the project::

    git clone https://github.com/DeNederlandscheBank/dnb-nlp.git

Then start with a clean environment::
    
    conda create -n your_env_name python=3.6

And activate the environment::

    conda activate your_env_name

Make sure you are in the root of the cloned project. Install the required packages::

    pip install -r requirements.txt --find-links=pkgs/ 

This installs the packages for natural language processing that we use (scipy, gensim, nltk and lexnlp).

Offline installation
--------------------

We included all the required packages in the project, so you should be able to do an offline installation.

Make sure you have at least Anaconda 5.3.1 installed. 

Make sure you have the zip file from https://github.com/DeNederlandscheBank/dnb-nlp.git. Extract the zip file to the desired location.

Then start with a clean and empty environment::
    
    conda create -n your_env_name

And activate the environment::

    conda activate your_env_name

Install the following packages::

	conda install pkgs/vc-14-0.tar.bz2

	conda install pkgs/vs2015_runtime-14.0.25420-0.tar.bz2

Then install Python 3.6::

	conda install python=3.6

Make sure you are in the root of the cloned project. Then install the remaining packages in pkgs/.::

	pip install -r requirements.txt --no-index --find-links pkgs/

Then the following error occurs::

	ERROR: lexnlp 1.4.0 has requirement scipy==1.0.0, but you'll have scipy 1.1.0 which is incompatible.

You can ignore that.

Install data
============

The cloned project does not contain any data, but code is included to download the data easily.

Legislation data
----------------

To get the legislation data, run in the project root::
    
    python dnbnlp/utils/make_law_data.py

Then you can choose from all official European languages.

You can also run::

    python dnbnlp/utils/make_law_data.py --language EN

to get the English version of the legislation. To get all languages use ``--language ALL``.

The data is downloaded from the eur-lex website (https://eur-lex.europa.eu/homepage.html). Currently, the following European legislation is downloaded:

* EU Delegated Regulation 2015/35 (Solvency 2)

On default, the pdf-documents are put in ``/data/external/law``.

The pdf-documents are processed (text from pdf is extracted with pdfminer.six and page headers are deleted) and the txt-files are put in ``/data/interim/law`` for further processing.

SFCR data
---------

To get the SFCR data, run in the project root::
    
    python dnbnlp/utils/make_sfcr_data.py

This downloads all the SFCRs defined in ``/data/metadata_sfcr.csv`` (the cvs-files contains the urls of the SFCR documents of a number of insurance undertakings).

The pdf-documents are processed and the txt-files are put in ``/data/interim/sfcr`` for further processing.

Credits
-------

This package was created with Cookiecutter and the data science project template (https://drivendata.github.io/cookiecutter-data-science).

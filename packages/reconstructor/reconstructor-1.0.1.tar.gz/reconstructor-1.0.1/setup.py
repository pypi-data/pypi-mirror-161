# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['reconstructor']

package_data = \
{'': ['*']}

install_requires = \
['argparse>=1.4.0,<2.0.0', 'cobra==0.22.1', 'symengine>=0.9.2,<0.10.0']

setup_kwargs = {
    'name': 'reconstructor',
    'version': '1.0.1',
    'description': 'COBRApy Compatible Genome Scale Metabolic Network Reconstruction Tool: Reconstructor',
    'long_description': "# Reconstructor\nReconstructor is a COBRApy compatible, automated GENRE building tool from gene fastas based on KEGG annotations. For necessary installation files go to: https://github.com/emmamglass/reconstructor/\n\n#### /MEMOTE (on github)\ncontains benchmarking scores for 10 representative reconstructor models\n\n#### /reconstructor (on github)\ncontains all package source code\n\n#### /testfiles (on github)\nfolder containing files necessary to test for successful installation\n\n## Installation:\n### 1) Install Reconstructor python package\nThis can be done via pip in the command line\n\n```\npip install reconstructor\n```\n\n### 2) Download necessary reference databases\nGo to https://github.com/emmamglass/reconstructor/releases/tag/v0.0.1 and download all assets (excluding source code zip files)\n\n### 3) Create 'refs' folder\nGo to your local downloads folder and create a folder called 'refs' containing the downloaded assets:\n```\nbiomass.sbml \n```\n```\ncompounds.json\n```\n```\ngene_modelseed.pickle\n```\n```\ngene_names.pickle\n```\n```\nreactions.json\n```\n```\nscreened_kegg_prokaryotes_pep_db.dmnd\n```\n```\nuniversal.pickle\n```\n\n### 4) scp refs folder into the reconstructor package folder\nUse the following command (or similar) in mac terminal to copy the refs folder into the reconstructor python package folder\n```\nscp -r ~/Downloads/refs ~/opt/anaconda3/lib/python3.9/site-packages/reconstructor\n```\n\n### 5) Download diamond \nDiamond version v2.0.15 or higher is REQUIRED. Install instructions for diamond can be found here if compiling from source: https://github.com/bbuchfink/diamond/wiki/2.-Installation. \n\nAlternatively, diamond can be installed via homebrew:\nhttps://formulae.brew.sh/formula/diamond\n\nDiamond must be v2.0.15 or higher.\n\n## Test suite:\n#### 1) Download testfiles folder to your desktop\nDownload the testfiles folder onto your local desktop.\n\n#### 2) Change directory to testfiles folder\nUse command line to change your current directory to the testfiles folder. Use the following command or something similar:\n```\ncd Desktop/testfiles\n```\n\n#### 3) Run the following tests to ensure installation was successful\nRun the following three tests to ensure reconstruction was installed correctly and is functional. The first test will take approximately 45 minutes to run, second test ~8  minutes, third test ~2 minutes, dependent on computer/processor speed. :\n#### Test 1\n```\npython -m reconstructor --input 488.146.fa --type 1 --gram negative\n```\n#### Test 2\n```\npython -m reconstructor --input 488.146a.KEGGprot.out --type 2 --gram negative\n```\n#### Test 3\n```\npython -m reconstructor --input fmt.metaG.01044A.bin.149.KEGGprot.sbml --type 3\n```\n\n#### 4) Delete testfiles folder from your destktop\nYou no longer need the testfiles folder after running the installation tests, so feel free to delete this from your desktop.\n\n## Usage:\n### Use reconstructor via command line\nNow that reconstructor and all dependency databases are installed, you can proceed to use reconstructor via command line. An example would be:\n```\npython -m reconstructor --input <input fasta file> --type <1,2,3> --gram <negative, positive> --other arguments <args>\n```\n#### Type 1: Build GENRE from annotated amino acid fasta files\n```\npython -m reconstructor --input Osplanchnicus.aa.fasta --type 1 --gram negative --other_args <args>\n```\n\n#### Type 2: Build GENRE from BLASTp hits\n```\npython -m reconstructor --input Osplanchnicus.hits.out --type 2 --gram negative --other_args <args>\n```\n\n#### Type 3: Additional gap-filling (if necessary)\n```\npython -m reconstructor --input Osplanchnicus.sbml --type 3 --other_args <args>\n```\n### Required and optional parameters\n```\n--input <input file, Required>\n```\n```\n--type <input file type, .fasta = 1, diamond blastp output = 2, .sbml = 3, Required, Default = 1> \n```\n```\n--gram <Type of Gram classificiation (positive or negative), default = positive>\n```\n```\n--media <List of metabolites composing the media condition. Not required.>\n```\n```\n--tasks <List of metabolic tasks. Not required>\n```\n```\n--org <KEGG organism code. Not required>\n```\n```\n--min_frac <Minimum objective fraction required during gapfilling, default = 0.01>\n```\n```\n--max_frac <Maximum objective fraction allowed during gapfilling, default = 0.5>\n```\n```\n--out <Name of output GENRE file, default = default>\n```\n```\n--name <ID of output GENRE, default = default>\n```\n```\n--cpu <Number of processors to use, default = 1>\n```",
    'author': 'Matt Jenior and Emma Glass',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

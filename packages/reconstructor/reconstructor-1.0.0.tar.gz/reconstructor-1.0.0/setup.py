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
    'version': '1.0.0',
    'description': 'COBRApy Compatible Genome Scale Metabolic Network Reconstruction Tool: Reconstructor',
    'long_description': "# Reconstructor\nReconstructor is a COBRApy compatible, automated GENRE building tool from gene fastas based on KEGG annotations.\n\n## Installation:\n### Install Reconstructor python package\nThis can be done via pip in the command line\n\n```\npip install reconstructor\n```\n\n### Download necessary reference databases\nGo to https://github.com/emmamglass/reconstructor/releases/tag/v0.0.1 and download all assets (excluding source code zip files)\n\n### Create 'refs' folder\nGo to your local downloads folder and create a folder called 'refs' containing the downloaded assets:\n```\nbiomass.sbml \n```\n```\ncompounds.json\n```\n```\ngene_modelseed.pickle\n```\n```\ngene_names.pickle\n```\n```\nreactions.json\n```\n```\nscreened_kegg_prokaryotes_pep_db.dmnd\n```\n```\nuniversal.pickle\n```\n\n### scp refs folder into the reconstructor package folder\nUse the following command (or similar) in mac terminal to copy the refs folder into the reconstructor python package folder\n```\nscp -r ~/Downloads/refs ~/opt/anaconda3/lib/python3.9/site-packages/reconstructor\n```\n\n### Download diamond \nDiamond version v2.0.15 or higher is REQUIRED. Install instructions for diamond can be found here if compiling from source: https://github.com/bbuchfink/diamond/wiki/2.-Installation. \n\nAdditionally, diamond can be installed via homebrew:\nhttps://formulae.brew.sh/formula/diamond\n\nDiamond must be v2.0.15 or higher.\n\n## Test suite:\nRun the following three tests to ensure reconstruction was installed correctly and is functional. The first test will take approximately 45 minutes to run, second test ~  minutes, third test ~   minutes, dependent on computer/processor speed. :\n#### Test 1\n```\npython -m reconstructor --input 562.50221.fa --type 1 --gram negative\n```\n#### Test 2\n```\npython -m reconstructor --input .KEGG.prot.out --type 2 --gram negative\n```\n#### Test 3\n```\npython -m reconstructor --input 210.8698 --type 3 --gram negative\n```\n## Usage:\n### Use reconstructor via command line\nNow that reconstructor and all dependency databases are installed, you can proceed to use reconstructor via command line. An example would be:\n```\npython -m reconstructor --input <input fasta file> --type <1,2,3> --gram <negative, positive> --other arguments <args>\n```\n#### Type 1: Build GENRE from annotated amino acid fasta files\n```\npython -m reconstructor --input Osplanchnicus.aa.fasta --type 1 --gram negative --other_args <args>\n```\n\n#### Type 2: Build GENRE from BLASTp hits\n```\npython -m reconstructor --input Osplanchnicus.hits.out --type 2 --gram negative --other_args <args>\n```\n\n#### Type 3: Additional gap-filling (if necessary)\n```\npython -m reconstructor --input Osplanchnicus.sbml --type 3 --other_args <args>\n```\n### Required and optional parameters\n```\n--input <input file, Required>\n```\n```\n--type <input file type, .fasta = 1, diamond blastp output = 2, .sbml = 3, Required, Default = 1> \n```\n```\n--gram <Type of Gram classificiation (positive or negative), default = positive>\n```\n```\n--media <List of metabolites composing the media condition. Not required.>\n```\n```\n--tasks <List of metabolic tasks. Not required>\n```\n```\n--org <KEGG organism code. Not required>\n```\n```\n--min_frac <Minimum objective fraction required during gapfilling, default = 0.01>\n```\n```\n--max_frac <Maximum objective fraction allowed during gapfilling, default = 0.5>\n```\n```\n--out <Name of output GENRE file, default = default>\n```\n```\n--name <ID of output GENRE, default = default>\n```\n```\n--cpu <Number of processors to use, default = 1>\n```\n\n",
    'author': 'Matt Jenior',
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

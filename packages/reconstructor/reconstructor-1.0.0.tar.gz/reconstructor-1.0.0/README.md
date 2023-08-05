# Reconstructor
Reconstructor is a COBRApy compatible, automated GENRE building tool from gene fastas based on KEGG annotations.

## Installation:
### Install Reconstructor python package
This can be done via pip in the command line

```
pip install reconstructor
```

### Download necessary reference databases
Go to https://github.com/emmamglass/reconstructor/releases/tag/v0.0.1 and download all assets (excluding source code zip files)

### Create 'refs' folder
Go to your local downloads folder and create a folder called 'refs' containing the downloaded assets:
```
biomass.sbml 
```
```
compounds.json
```
```
gene_modelseed.pickle
```
```
gene_names.pickle
```
```
reactions.json
```
```
screened_kegg_prokaryotes_pep_db.dmnd
```
```
universal.pickle
```

### scp refs folder into the reconstructor package folder
Use the following command (or similar) in mac terminal to copy the refs folder into the reconstructor python package folder
```
scp -r ~/Downloads/refs ~/opt/anaconda3/lib/python3.9/site-packages/reconstructor
```

### Download diamond 
Diamond version v2.0.15 or higher is REQUIRED. Install instructions for diamond can be found here if compiling from source: https://github.com/bbuchfink/diamond/wiki/2.-Installation. 

Additionally, diamond can be installed via homebrew:
https://formulae.brew.sh/formula/diamond

Diamond must be v2.0.15 or higher.

## Test suite:
Run the following three tests to ensure reconstruction was installed correctly and is functional. The first test will take approximately 45 minutes to run, second test ~  minutes, third test ~   minutes, dependent on computer/processor speed. :
#### Test 1
```
python -m reconstructor --input 562.50221.fa --type 1 --gram negative
```
#### Test 2
```
python -m reconstructor --input .KEGG.prot.out --type 2 --gram negative
```
#### Test 3
```
python -m reconstructor --input 210.8698 --type 3 --gram negative
```
## Usage:
### Use reconstructor via command line
Now that reconstructor and all dependency databases are installed, you can proceed to use reconstructor via command line. An example would be:
```
python -m reconstructor --input <input fasta file> --type <1,2,3> --gram <negative, positive> --other arguments <args>
```
#### Type 1: Build GENRE from annotated amino acid fasta files
```
python -m reconstructor --input Osplanchnicus.aa.fasta --type 1 --gram negative --other_args <args>
```

#### Type 2: Build GENRE from BLASTp hits
```
python -m reconstructor --input Osplanchnicus.hits.out --type 2 --gram negative --other_args <args>
```

#### Type 3: Additional gap-filling (if necessary)
```
python -m reconstructor --input Osplanchnicus.sbml --type 3 --other_args <args>
```
### Required and optional parameters
```
--input <input file, Required>
```
```
--type <input file type, .fasta = 1, diamond blastp output = 2, .sbml = 3, Required, Default = 1> 
```
```
--gram <Type of Gram classificiation (positive or negative), default = positive>
```
```
--media <List of metabolites composing the media condition. Not required.>
```
```
--tasks <List of metabolic tasks. Not required>
```
```
--org <KEGG organism code. Not required>
```
```
--min_frac <Minimum objective fraction required during gapfilling, default = 0.01>
```
```
--max_frac <Maximum objective fraction allowed during gapfilling, default = 0.5>
```
```
--out <Name of output GENRE file, default = default>
```
```
--name <ID of output GENRE, default = default>
```
```
--cpu <Number of processors to use, default = 1>
```


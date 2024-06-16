# Local Environment Setup for Workflow Execution

To execute the workflow on the local machine, it is necessary to have `Python 3.11` and the package manager `Pip` installed. In addition, the [ClustalW](http://www.clustal.org/clustal2/)   software must be installed. All these steps have been described in the [README.md](../README.md) file.

From this point on, the instructions assume that the project has already been cloned from the git repository and that the environment is already set up.

## Dependency Installation

Before running the project, it is necessary to install the Python dependencies specified in the "requirements.txt" file. To do this, run the following command in the terminal:

```bash
pip install -r requirements.txt
```

## File Organization

Make sure that all necessary files (containing the protein sequences in FASTA format) are in the directory specified in `INPUT_PATH`.

## Workflow Steps

### 1. Phylogenetic Tree Construction

The first step of the workflow is the construction of phylogenetic trees from the provided protein sequences. To do this, run the `tree_constructor_local.py` script:

```bash
python tree_constructor_local.py
```

This script performs multiple sequence alignment using ClustalW and then constructs the phylogenetic tree using the Neighbor-Joining (NJ) method.

### 2. Subtree Construction and MAF Analysis

After the construction of the phylogenetic trees, the next step is to generate subtrees from the main trees and perform MAF (subtree pair frequency matrix) analysis.

Run the `subtree_mining_local.py` script:

```bash
python subtree_mining_local.py
```

This script will generate all subtrees from the phylogenetic trees and then calculate the subtree pair frequency matrix (MAF). The result will be displayed in the terminal.

### Output

The generated subtrees will be saved in the `PATH_OUTPUT` directory. In addition, the subtree pair frequency matrix (MAF) will be displayed in the terminal during the execution of the script.

### Temporary File Cleanup

The scripts will automatically clean up the temporary files generated during the process, as well as from old runs. The temporary files will be deleted from the `TMP_PATH` directory.

## Final Considerations

This guide provides an overview of the workflow for constructing phylogenetic trees and analyzing subtrees. Make sure that the input files are correctly organized in the indicated directories and run the scripts according to the described steps.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

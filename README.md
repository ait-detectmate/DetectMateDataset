# DetectMate Dataset

Downloads and processes log datasets for use with `DetectMate`. Datasets are downloaded and processed only once, then cached locally for future use without requiring additional downloads.

## Install the dependency

From this repository's root directory, install into the active virtual environment:

```bash
uv pip install .
```

To install into another project's virtual environment, run this from that project
and provide the path to this repository:

```bash
uv pip install /path/to/DetectMateDataset
```

## Usage

### Command line

To use the command line use:

```bash
uv run logdataset -h
```

### Download / load dataset

To download dataset for the first time do like the example.

```bash
uv run logdataset load_dataset AIT_v2_harrison Intranet-Apache 
```

Alternative you can load the dataset from a python code:

```python
from logdatasets import api

db = api.load_dataset("AIT_v2_harrison", "Intranet-Apache", do_cache=True)
```

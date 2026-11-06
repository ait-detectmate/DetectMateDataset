# LogDataset

Allows to process log datasets and use them in `DetectMate`. First time is download and process from the internet, after that the dataset is forever saved in your computer.

## Install the dependency

This will add the dependency in another project venv.

```bash
uv pip install ../DetectMateExperiments/LogData/
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

### Transfer dataset

Downloading and procesing a dataset can be time consuming. Alternative if you have a computer with the dataset already instaled, you can transfer to another computer.

#### Activate server

Open a server from the computer with the process dataset.

```bash
uv run logdataset init_server
```

### Transfer to client

To transfer to client run the next command:

```bash
uv run logdataset request_dataset AIT_v2_wilson FileShare-Audit --save_cache
```

or alternative the transfer can be done from a python code:

```python
from logdatasets.server.client import get_dataset

ip = ...
db = get_dataset("AIT_v2_harrison", "Intranet-Apache", ip=ip, save_cache=True)
```

Note that if `use_cache = False` the dataset will not be permantly save in your computer.
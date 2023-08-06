# kdp-python-connector

## Prequisites
* Python version 3.8.5
* Install dependencies with:
```
pip3 install -r requirements.txt
```

## Examples

### Example 1: Ingest CSV File


See [./examples/ingest_csv.py](./examples/ingest_csv.py) for an example of how to ingest data from a csv file into KDP.


**Step 0**

Update `ingest_csv.py` file to provide the values for the variables listed below:
* JWT - token to be used when interacting with KDP
* WORKSPACE_ID - workspace id
* DATASET_ID - dataset id
  * KDP_API_HOST - KDP API host name such as `api.dev.koverse.com`, `api.staging.koverse.com` or `api.app.koverse.com`
* PATH_TO_CSV_FILE - location to the csv file to be ingested

Optional
* batch_size - number of records in a batch.


**Step 1**

Install dependency

```
cd examples
pip3 install -r requirements.txt
```

**Step 2**

Execute the script

```
python3 ingest_csv.py
```

## Release

### Versioning

Before a better solution is implemented, `setup.py` file needs to be updated to increment the version number each time a new version is needed. Next version number can be determined from the current latest git tag and increment the minor version by one.

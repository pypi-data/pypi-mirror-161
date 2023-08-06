# Transform MQL

## Auth setup:
```bash
# Follow the prompts to either enter api_key or perform MFA
mql setup
```

**NOTE:** All configs including pinned models, api_key, bearer tokens will be stored under the default directory at `~/.transform/config.yml`. If another location is desired, please set an ENV variable at `$TFD_CONFIG_DIR` with the desired path.

## CLI Usage:
Run `mql --help` for a list of all available commands
```
Usage: mql [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose
  --debug-log-file
  --help            Show this message and exit.

Commands:
  commit-configs         Commit yaml configs found in specified config...
  contact                Instructions for how to contact Transform for help.
  drop-cache             Drop the MQL cache.
  drop-materialization   ***NEW*** Create a new MQL drop materialization...
  get-dimension-values   List all dimension values that are queryable...
  health-report          Completes a health check on MQL servers.
  identify               Identify the currently authenticated user.
  latest-mql-image       Outputs the latest MQL server image details
  list-dimensions        List all unique dimensions for the Organization.
  list-materializations  List the materializations for the Organization...
  list-metrics           List the metrics for the Organization with their...
  list-queries           Retrieve queries from mql server
  list-servers           Lists available MQL servers.
  materialize            ***NEW*** Create a new MQL materialization...
  pin-model              Pin a model id from configs that are already...
  ping                   Perform basic HTTP health check against...
  query                  Create a new MQL query, polls for completion and...
  setup                  Guides user through CLI setup.
  stream-query-logs      Retrieve queries from mql server
  unpin-model            Unpin a model id
  validate-configs       Validate yaml configs found in specified config...
  version                Print the current version of the MQL CLI.
```
#### Examples:
```
mql query --metrics messages --dimensions ds --limit 10
mql materialize --materialization-name name --start-time 2021-10-01 --end_time 2021-11-01
```

## Python Library
#### Examples:
```python
# Instantiating the object manually
from transform.mql import MQLClient

"""
Pass: 
  - api_key if you want to manually provide an api_key
  - mql_server_url if you want to override the mql server

DEFAULT: values in ~/.transform/config.yml
"""
mql = MQLClient(api_key: Optional[str], mql_server_url: Optional[str])

df = mql.query(metrics=["messages"], dimensions=["ds"], where="is_thread")
```
```python
# If authentication already exists in config
from transform import mql

df = mql.query(metrics=["messages"], dimensions=["ds"], where="is_thread")
```
## API References
See more details at https://docs.transform.co/
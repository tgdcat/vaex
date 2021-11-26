
# Configuration

All settings in Vaex can be configured in a uniform way, based on [Pydantic](https://pydantic-docs.helpmanual.io/usage/settings/). From a Python runtime, configuration of settings can be done via the `vaex.settings` module.
```python
import vaex
vaex.settings.main.thread_count = 10
vaex.settings.display.max_columns = 50
```

Via environmental variables:
```
$ VAEX_NUM_THREADS=10 VAEX_DISPLAY_MAX_COLUMNS=50 python myservice.py
```

Otherwise, values are obtained from a `.env` [file using dotenv](https://saurabh-kumar.com/python-dotenv/#usages) from the current workding directory.
```
VAEX_NUM_THREADS=22
VAEX_CHUNK_SIZE_MIN=2048
```

Lastly, a global yaml file from `$VAEX_PATH_HOME/.vaex/main.yaml` is loaded (with last priority).
```
thread_count: 33
display:
  max_columns: 44
  max_rows: 20
```

If we now run `vaex settings yaml`, we see the effective settings as yaml output:
```
$ VAEX_NUM_THREADS=10 VAEX_DISPLAY_MAX_COLUMNS=50 vaex settings yaml
...
chunk:
  size: null
  size_min: 2048
  size_max: 1048576
display:
  max_columns: 50
  max_rows: 20
thread_count: 10
...
```


## Developers

When updating `vaex/settings.py`, run the `vaex settings watch` to generate this documentation below automatically when saving the file.



<!-- autogenerate markdown below -->

## Settings
General settings for vaex

### async
How to run async code in the local executor

Environmental variable: `VAEX_ASYNC`

Example use:
 ```
$ VAEX_ASYNC=nest python myscript.py
```

Python setting `vaex.setting.main.async_`

Example use: `vaex.setting.main.async_ = 'nest'`
### aliases
Aliases to be used for vaex.open

Environmental variable: `VAEX_ALIASES`

Python setting `vaex.setting.main.aliases`
### mmap
Experimental to turn off, will avoid using memory mapping if set to False

Environmental variable: `VAEX_MMAP`

Example use:
 ```
$ VAEX_MMAP=True python myscript.py
```

Python setting `vaex.setting.main.mmap`

Example use: `vaex.setting.main.mmap = True`
### thread_count
Number of threads to use for computations, defaults to multiprocessing.cpu_count()

Environmental variable: `VAEX_NUM_THREADS`

Python setting `vaex.setting.main.thread_count`
### thread_count_io
Number of threads to use for IO, defaults to thread_count_io + 1

Environmental variable: `VAEX_NUM_THREADS_IO`

Python setting `vaex.setting.main.thread_count_io`
### process_count
Number of processes to use for multiprocessing (e.g. apply), defaults to thread_count setting

Environmental variable: `VAEX_PROCESS_COUNT`

Python setting `vaex.setting.main.process_count`
## Chunk
Configure how a dataset is broken down in smaller chunks. The executor dynamically adjusts the chunk size based on `size_min` and `size_max` and the number of threads when `size` is not set.

### size
When set, fixes the number of chunks, e.g. do not dynamically adjust between min and max

Environmental variable: `VAEX_CHUNK_SIZE`

Python setting `vaex.setting.main.chunk.size`
### size_min
Minimum chunk size

Environmental variable: `VAEX_CHUNK_SIZE_MIN`

Example use:
 ```
$ VAEX_CHUNK_SIZE_MIN=1024 python myscript.py
```

Python setting `vaex.setting.main.chunk.size_min`

Example use: `vaex.setting.main.chunk.size_min = 1024`
### size_max
Maximum chunk size

Environmental variable: `VAEX_CHUNK_SIZE_MAX`

Example use:
 ```
$ VAEX_CHUNK_SIZE_MAX=1048576 python myscript.py
```

Python setting `vaex.setting.main.chunk.size_max`

Example use: `vaex.setting.main.chunk.size_max = 1048576`

## Display
How a dataframe displays

### max_columns
How many column to display when printing out a dataframe

Environmental variable: `VAEX_DISPLAY_MAX_COLUMNS`

Example use:
 ```
$ VAEX_DISPLAY_MAX_COLUMNS=200 python myscript.py
```

Python setting `vaex.setting.display.max_columns`

Example use: `vaex.setting.display.max_columns = 200`
### max_rows
How many rows to print out before showing the first and last rows

Environmental variable: `VAEX_DISPLAY_MAX_ROWS`

Example use:
 ```
$ VAEX_DISPLAY_MAX_ROWS=10 python myscript.py
```

Python setting `vaex.setting.display.max_rows`

Example use: `vaex.setting.display.max_rows = 10`

## Paths
Paths/directories configuration

### home
Home directory for vaex, which defaults to `$HOME/.vaex`,  If both `$VAEX_PATH_HOME` and `$HOME` are not define, the current working directory is used. (Note that this setting cannot be configured from the vaex home directory itself).

Environmental variable: `VAEX_PATH_HOME`

Python setting `vaex.setting.paths.home`
### cache_compute
Storage location for compute results. Defaults to `${VAEX_PATH_HOME}/cache`

Environmental variable: `VAEX_PATH_CACHE_COMPUTE`

Python setting `vaex.setting.paths.cache_compute`
### cache_fs
Storage location for caching files from remote file systems. Defaults to `${VAEX_PATH_HOME}/file-cache/`

Environmental variable: `VAEX_PATH_CACHE_FS`

Python setting `vaex.setting.paths.cache_fs`
### data
Storage location for data files, like vaex.example(). Defaults to `${VAEX_PATH_HOME}/data/`

Environmental variable: `VAEX_PATH_DATA`

Python setting `vaex.setting.paths.data`

## Settings
Configuration options for the FastAPI server

### add_example
Add example dataset

Environmental variable: `VAEX_SERVER_ADD_EXAMPLE`

Example use:
 ```
$ VAEX_SERVER_ADD_EXAMPLE=True python myscript.py
```

Python setting `vaex.setting.server.add_example`

Example use: `vaex.setting.server.add_example = True`
### graphql
Add graphql endpoint

Environmental variable: `VAEX_SERVER_GRAPHQL`

Example use:
 ```
$ VAEX_SERVER_GRAPHQL=False python myscript.py
```

Python setting `vaex.setting.server.graphql`

Example use: `vaex.setting.server.graphql = False`
### files
Mapping of name to path

Environmental variable: `VAEX_SERVER_FILES`

Python setting `vaex.setting.server.files`

## CacheCompute
Setting for caching of computation or task results, see the [API](api.html#module-vaex.cache) for more details.

### type
Type of cache, e.g. 'memory_infinite', 'memory', 'disk', 'redis', or a multilevel cache, e.g. 'memory,disk'

Environmental variable: `VAEX_CACHE`

Python setting `vaex.setting.cache.type`
### disk_size_limit
Maximum size for cache on disk, e.g. 10GB, 500MB

Environmental variable: `VAEX_CACHEDISK_SIZE_LIMIT`

Example use:
 ```
$ VAEX_CACHEDISK_SIZE_LIMIT=10GB python myscript.py
```

Python setting `vaex.setting.cache.disk_size_limit`

Example use: `vaex.setting.cache.disk_size_limit = '10GB'`
### memory_size_limit
Maximum size for cache in memory, e.g. 1GB, 500MB

Environmental variable: `VAEX_CACHEMEMORY_SIZE_LIMIT`

Example use:
 ```
$ VAEX_CACHEMEMORY_SIZE_LIMIT=1GB python myscript.py
```

Python setting `vaex.setting.cache.memory_size_limit`

Example use: `vaex.setting.cache.memory_size_limit = '1GB'`

## MemoryTracker
Memory tracking/protection when using vaex in a service

### type
Which memory tracker to use when executing tasks

Environmental variable: `VAEX_MEMORY_TRACKER`

Example use:
 ```
$ VAEX_MEMORY_TRACKER=default python myscript.py
```

Python setting `vaex.setting.main.memory_tracker.type`

Example use: `vaex.setting.main.memory_tracker.type = 'default'`
### max
How much memory the executor can use maximally (only used for type='limit')

Environmental variable: `VAEX_MEMORY_TRACKER_MAX`

Python setting `vaex.setting.main.memory_tracker.max`

## TaskTracker
task tracking/protection when using vaex in a service

### type
Comma seperated string of trackers to run while executing tasks

Environmental variable: `VAEX_TASK_TRACKER`

Example use:
 ```
$ VAEX_TASK_TRACKER= python myscript.py
```

Python setting `vaex.setting.main.task_tracker.type`



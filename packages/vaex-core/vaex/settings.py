import os
import logging
import vaex.utils
import collections
import json
import multiprocessing
import sys

from pydantic import BaseModel, BaseSettings, Field
from typing import List, Union, Optional, Dict
from enum import Enum
from .config import ConfigDefault

logger = logging.getLogger("vaex.settings")

# we may want to use this
# class ByteAmount(str):
#     @classmethod
#     def validate(cls, value):
#         try:
#             import ast
#             value = ast.literal_eval(value)
#         except:
#             pass
#         if isinstance(value, str):
#             import dask
#             value = dask.utils.parse_bytes(value)
#         if not isinstance(value, int):
#             raise TypeError(f"Expected a number of bytes, got {value}")
#         return value

#     def __repr__(self):
#         return f'PostCode({super().__repr__()})'


class MemoryTrackerEnum(str, Enum):
    default = 'default'
    limit = 'limit'


class MemoryTracker(BaseSettings):
    """Memory tracking/protection when using vaex in a service"""
    type: MemoryTrackerEnum = Field('default', title="Which memory tracker to use when executing tasks", env="VAEX_MEMORY_TRACKER")
    max: Optional[str] = Field(None, title="How much memory the executor can use maximally (only used for type='limit')")
    class Config:
        use_enum_values = True
        env_prefix = 'vaex_memory_tracker_'



class TaskTracker(BaseSettings):
    """task tracking/protection when using vaex in a service"""
    type: str = Field('', title="Comma seperated string of trackers to run while executing tasks", env="VAEX_TASK_TRACKER")
    class Config:
        use_enum_values = True
        env_prefix = 'vaex_task_tracker_'


class Display(BaseSettings):
    """How a dataframe displays"""
    max_columns: int = Field(200, title="How many column to display when printing out a dataframe")
    max_rows: int = Field(10, title="How many rows to print out before showing the first and last rows")
    class Config:
        env_prefix = 'vaex_display_'
        env_file = ".env"
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (
                env_settings,
                file_secret_settings,
                init_settings,
            )


class Chunk(BaseSettings):
    """Configure how a dataset is broken down in smaller chunks. The executor dynamically adjusts the chunk size based on `size_min` and `size_max` and the number of threads when `size` is not set."""
    size: Optional[int] = Field(title="When set, fixes the number of chunks, e.g. do not dynamically adjust between min and max")
    size_min: int = Field(1024, title="Minimum chunk size")
    size_max: int = Field(1024**2, title="Maximum chunk size")
    class Config(ConfigDefault):
        env_prefix = 'vaex_chunk_'


class CacheCompute(BaseSettings):
    """Setting for caching of computation or task results, see the [API](api.html#module-vaex.cache) for more details."""
    type: Optional[str] = Field(None, env='VAEX_CACHE', title="Type of cache, e.g. 'memory_infinite', 'memory', 'disk', 'redis', or a multilevel cache, e.g. 'memory,disk'")
    disk_size_limit: str = Field('10GB', title='Maximum size for cache on disk, e.g. 10GB, 500MB')
    memory_size_limit: str = Field('1GB', title='Maximum size for cache in memory, e.g. 1GB, 500MB')
    class Config(ConfigDefault):
        env_prefix = 'vaex_cache'


class AsyncEnum(str, Enum):
    nest = 'nest'
    awaitio = 'awaitio'

try:
    import vaex.server
    has_server = True
except ImportError:
    has_server = False

if has_server:
    import vaex.server.settings


class Paths(BaseSettings):
    """Paths/directories configuration"""
    home: Optional[str] = Field(default_factory=vaex.utils.get_vaex_home, env="VAEX_PATH_HOME", title="Home directory for vaex, which defaults to `$HOME/.vaex`, "\
        " If both `$VAEX_PATH_HOME` and `$HOME` are not define, the current working directory is used. (Note that this setting cannot be configured from the vaex home directory itself).")
    cache_compute: Optional[str] = Field(env="VAEX_PATH_CACHE_COMPUTE", title="Storage location for compute results. Defaults to `${VAEX_PATH_HOME}/cache`")
    cache_fs: Optional[str] = Field(env="VAEX_PATH_CACHE_FS", title="Storage location for caching files from remote file systems. Defaults to `${VAEX_PATH_HOME}/file-cache/`")
    data: Optional[str] = Field(env="VAEX_PATH_DATA", title="Storage location for data files, like vaex.example(). Defaults to `${VAEX_PATH_HOME}/data/`")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.cache_compute is None:
            self.cache_compute = os.path.join(self.home, "cache")
        if self.cache_fs is None:
            self.cache_fs = os.path.join(self.home, "file-cache")
        if self.data is None:
            self.data = os.path.join(self.home, "data")

    class Config(ConfigDefault):
        env_prefix = 'vaex_path_'


class Settings(BaseSettings):
    """General settings for vaex"""
    async_: AsyncEnum = Field('nest', env='VAEX_ASYNC', title="How to run async code in the local executor", min_length=2)
    aliases: Optional[dict] = Field(title='Aliases to be used for vaex.open', default_factory=list)
    cache_compute = CacheCompute()
    chunk: Chunk = Chunk()
    display: Display = Display()
    memory_tracker = MemoryTracker()
    task_tracker = TaskTracker()
    mmap: bool = Field(True, title="Experimental to turn off, will avoid using memory mapping if set to False")
    thread_count: Optional[int] = Field(env='VAEX_NUM_THREADS', title="Number of threads to use for computations, defaults to multiprocessing.cpu_count()", gt=0)
    thread_count_io: Optional[int] = Field(env='VAEX_NUM_THREADS_IO', title="Number of threads to use for IO, defaults to thread_count_io + 1", gt=0)
    process_count: Optional[int] = Field(title="Number of processes to use for multiprocessing (e.g. apply), defaults to thread_count setting", gt=0)
    paths: Paths = Field(Paths(), title="Configuration of paths")
    if has_server:
        server: vaex.server.settings.Settings = vaex.server.settings.Settings()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # dynamic defaults
        if self.thread_count is None:
            self.thread_count = multiprocessing.cpu_count()            
        if self.thread_count_io is None:
            self.thread_count_io = self.thread_count + 1
        if self.process_count is None:
            self.process_count = self.thread_count
    class Config(ConfigDefault):
        # extra = 'allow'
        use_enum_values = True
        allow_population_by_field_name = True
        allow_population_by_alias = True
        fields = {
            'async_': 'async'
        }
        case_sensitive = False
        env_prefix = 'vaex_'

_default_values = {}
filename = os.path.join(vaex.utils.get_vaex_home(), "main.yml")
if os.path.exists(filename):
    with open(filename) as f:
        _default_values = vaex.utils.yaml_load(f)
    if _default_values is None:
        _default_values = {}


main = Settings(**_default_values)
if has_server:
    server = main.server
display = main.display
cache_compute = main.cache_compute
aliases = main.aliases
paths = main.paths


def save(exclude_defaults=True, verbose=False):
    filename = os.path.join(vaex.utils.get_private_dir(), "main.yml")
    if verbose:
        values = main.dict(by_alias=True)
        print("All values:\n")
        vaex.utils.yaml_dump(sys.stdout, values)

    with open(filename, "w") as f:
        values = main.dict(by_alias=True, exclude_defaults=exclude_defaults)
        vaex.utils.yaml_dump(f, values)
        if verbose:
            print("Saved values:\n")
            vaex.utils.yaml_dump(sys.stdout, values)


def edit_jupyter():
    import vaex.jupyter.widgets
    editor = vaex.jupyter.widgets.SettingsEditor(schema=main.schema(), values=main.dict())
    return editor


def _to_md(cls, f=sys.stdout):
    printf = lambda *x: print(*x, file=f)
    title = cls.__name__
    printf(f"## {title}")
    printf(cls.__doc__)
    printf()

    # own fields
    for name, field in cls.__fields__.items():
        pyname  = name
        name = field.alias
        if issubclass(field.type_, BaseSettings):
            continue
        printf(f"### {name}")
        title = field.field_info.title
        if title is None:
            raise ValueError(f'Title missing for {name}')
        env_name = (cls.Config.env_prefix + name).upper()
        if field.field_info.extra["env_names"]:
            if len(field.field_info.extra["env_names"]) > 1:
                raise NotImplementedError('should we support this?')
            env_name = list(field.field_info.extra["env_names"])[0].upper()
        default = field.default

        printf(title)
        printf()

        printf(f'Environmental variable: `{env_name}`')
        if default is not None:
            printf()
            printf(f'Example use:\n ```\n$ {env_name}={default} python myscript.py\n```')
        printf()
        flat = {
            Settings: 'main',
            Chunk: 'main.chunk',
            Display: 'display',
            vaex.server.settings.Settings: 'server',
            CacheCompute: 'cache',
            MemoryTracker: 'main.memory_tracker',
            TaskTracker: 'main.task_tracker',
            Paths: 'paths',
        }[cls]
        pyvar = f'vaex.setting.{flat}.{pyname}'
        printf(f'Python setting `{pyvar}`')
        if default not in [None, ""]:
            printf()
            printf(f'Example use: `{pyvar} = {default!r}`')

    # sub objects
    for name, field in cls.__fields__.items():
        pyname  = name
        name = field.alias
        if not issubclass(field.type_, BaseSettings):
            continue
        name = field.type_.__name__
        _to_md(field.type_, f=f)
        printf()


def _watch():
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class EventHandler(FileSystemEventHandler):
        def on_modified(self, event):
            super(EventHandler, self).on_modified(event)
            print(f"Change detected, running docgen...")
            if os.system("vaex settings docgen") == 0:
                print("done")
            else:
                print("error")
    observer = Observer()
    path = __file__
    print(f"Running first time")
    os.system("vaex settings docgen")
    print(f"Watching {path}")
    observer.schedule(EventHandler(), path, recursive=True)
    observer.start()
    observer.join()


def _main(args):
    if len(args) > 1:
        type = args[1]
        if type == "schema":
            print(main.schema_json(indent=2))
        elif type == "yaml":
            values = main.dict(by_alias=True)
            vaex.utils.yaml_dump(sys.stdout, values)
        elif type == "json":
            values = main.dict(by_alias=True)
            json.dump(values, sys.stdout, indent=2)
        elif type == "save":
            save(exclude_defaults=True, verbose=True)
        elif type == "set":
            save(exclude_defaults=True, verbose=True)
        elif type == "save-defaults":
            save(exclude_defaults=False, verbose=True)
        elif type == "md":
            _to_md(Settings)
        elif type == "watch":
            # runs docgen automatically
            _watch()
        elif type == "docgen":
            with open('docs/source/conf.md') as f:
                current_md = f.read()
            import io
            f = io.StringIO()
            _to_md(Settings, f=f)
            code = f.getvalue()
            marker = '<!-- autogenerate markdown below -->'
            start = current_md.find(marker)
            start = current_md.find('\n', start)
            with open('docs/source/conf.md', 'w') as f:
                print(current_md[:start+1], file=f)
                print(code, file=f)
        else:
            raise ValueError('only support schema, values, save, save-defaults or md')
    else:
        print(json.dumps(main.dict(by_alias=True), indent=2))



if __name__ == "__main__":
    _main(sys.argv)

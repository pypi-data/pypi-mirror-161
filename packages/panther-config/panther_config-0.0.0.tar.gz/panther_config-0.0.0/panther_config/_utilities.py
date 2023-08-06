# coding=utf-8
import inspect
import os
import json
import datetime
import abc
from typing import List, Dict, Any


ISO_8601_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


class ConfigNode(abc.ABC):
    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass


class _Cache:
    _data: Dict[str, List[ConfigNode]]
    _cache_dir: str
    _cache_file: str

    def __init__(self) -> None:
        self._data = dict()
        self._cache_dir = os.path.abspath(
            os.environ.get("PANTHER_CACHE_DIR") or os.path.join(".", ".panther")
        )
        self.prep_cache_dir()

        cache_file_name = (
            os.environ.get("PANTHER_CONFIG_CACHE_FILENAME") or "panther-config-cache"
        )

        self._cache_file = os.path.join(self._cache_dir, cache_file_name)

        self.prep_cache_file()

    def prep_cache_dir(self) -> None:
        if not os.path.exists(self._cache_dir):
            os.mkdir(self._cache_dir)

    def prep_cache_file(self) -> None:
        with open(self._cache_file, "w") as f:
            f.write(
                json.dumps(
                    dict(
                        key="header",
                        data=dict(
                            timestamp=datetime.datetime.now().strftime(
                                ISO_8601_TIME_FORMAT
                            )
                        ),
                    )
                )
            )
            pass

    def add(self, key: str, node: ConfigNode) -> None:
        if self._cache_file is None:
            return

        with open(self._cache_file, "a") as f:
            f.write("\n")
            f.write(
                json.dumps(
                    dict(
                        key=key,
                        data=node.to_dict(),
                    )
                )
            )


cache = _Cache()


def config_node_dict_field_value(obj: Any) -> Any:
    if isinstance(obj, ConfigNode):
        return obj.to_dict()

    if callable(obj):
        return inspect.getsource(obj)

    return obj

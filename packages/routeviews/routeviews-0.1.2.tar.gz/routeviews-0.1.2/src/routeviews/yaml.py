"""Custom yaml `load` and `dump` functions, that align with Route Views YAML conventions.

Use case: Updating Route Views ansible inventory YAML files.
"""
import io
import logging
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError

logger = logging.getLogger(__name__)


# Initialize a YAML singleton, and configure it
_yaml = YAML()
yaml_indentation_settings = {
    'mapping': 2, 
    'sequence': 4,
    'offset': 2,
}
"""These yaml_indentation_settings will output YAML like the following example: 

---
x:
  y:
    - a: 1
    - 2
  z: |
    This is how a multiline blocks is indented with this scheme.

    Always indented by 2 spaces, per the offset.

    Even this line is indented the same.
"""
_yaml.indent(**yaml_indentation_settings)


class ParseError(ParserError):
    @classmethod
    def from_ParserError(cls, error: ParserError, note):
        return cls(
            context=error.context,
            context_mark=error.context_mark,
            problem=error.problem,
            problem_mark=error.problem_mark,
            note=note if note else error.note,
        )


def load(file_path: str = None, data: str = None) -> Any:
    """Load a 

    Args:
        file_path (str): 

    Returns:
        str: _description_
    """
    global _yaml
    if file_path and data:
        logger.error('Only one of file_path or data can be loaded')
    if file_path:
        with open(file_path) as _data:
            data = _data.read()
    try:
        return _yaml.load(data)
    except ParserError as e:
        raise ParseError.from_ParserError(e, f'Unable to parse {file_path}')


def dump(data, filepath: str = None) -> str:
    """Dump data as YAML, to out_stream, or returned as string. 

    Route Views YAML conventions are maintained by this function. 

    Args:
        data: Any Python object, to be dumped to YAML.
        filepath (io.Stream, optional): Stream where to write the file. 
            Defaults to None, and instead a string is returned.


    Returns:
        str: YAML representation of data.
    """
    global _yaml
    if filepath is None:
        out_stream = io.StringIO()
        _yaml.dump(data, out_stream)
        return out_stream.getvalue()
    else:
        _yaml.dump(data, Path(filepath))

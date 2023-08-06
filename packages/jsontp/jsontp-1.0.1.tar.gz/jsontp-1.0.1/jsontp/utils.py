import os
import json
from typing import Optional, Union


class FileIO:
  """File Input/Output

  Arguments
  ---------
  str
    `src` (source), filepath to load

  Methods
  -------
  load - reads the given `json` filepath
  dump - writes the `data` to the given `dst` (destination)
  """

  def __init__(self, src: str):
    self.src = src

  @staticmethod
  def validate_path(path: str) -> Optional[FileNotFoundError]:
    if not os.path.exists(path):
      raise FileNotFoundError(path)

  def dump(self, data: dict, dst: str, indent: int = 4) -> None:
    with open(dst, 'w') as ftw:
      ftw.write(json.dumps(data, indent=indent))

  def load(self) -> Union[dict, FileNotFoundError]:
    self.validate_path(self.src)

    with open(self.src, 'r') as ftr:
      return json.loads(ftr.read())

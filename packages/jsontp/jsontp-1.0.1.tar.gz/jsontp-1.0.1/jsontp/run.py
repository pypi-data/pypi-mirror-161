import os
import json
from typing import Optional, Union, NoReturn, Any, Generator

from .config import Tree, Key
from .utils import FileIO


# TODO
#   - Rename *PageDataTree


class PageDataTree:

  def __init__(self, data: json):
    self.data = data

  # TODO: check for other types
  @staticmethod
  def join_tree(tree: str, key: str, list_index: Optional[int] = None):
    keys = [tree]

    if list_index is not None:
      keys.append(Tree.LIST_INDEX_WRAPPER.format(index=list_index))

    keys.append(key)

    return Tree.DELIMITER.join(keys)

  def process_result(self, result: str,
                           result_to: str,
                           result_value: str) -> Union[Optional[str], NoReturn]:
    # TODO: rename parameters name
    if Tree.SEARCH_FILTER_KEY and (Tree.SEARCH_FILTER_KEY not in result):
      return None

    if Tree.SEARCH_FILTER_VALUE:
      if not isinstance(result_value, (int, str)):
        return None
      if str(result_value) != Tree.SEARCH_FILTER_VALUE:
        return None

    if (Tree.SEARCH_LIMIT and Tree.SEARCH_LIMIT > 0):
      Tree.SEARCH_LIMIT -= 1

    if Tree.SEARCH_LIMIT == 0:
      exit()

    if result_to == Key.SHOW:
      print(result)

    if result_to == Key.SAVE:
      return result

  def tree_by_key(self, data: Optional[dict] = None, key: str = '',
                        gen_tree: str = Tree.ROOT, list_index: Optional[int] = None,
                        result_to: str = Key.SAVE) -> Generator[str, None, None]:
    """Yields str: ex. A -> B -> C -> *key
    """
    if data is None:
      data = self.data

    if isinstance(data, list):
      for idx, item in enumerate(data):
        yield from self.tree_by_key(
          item, key, gen_tree, list_index=idx, result_to=result_to
        )

    if isinstance(data, dict):
      for data_key, data_value in data.items():
        tree = self.join_tree(gen_tree, data_key, list_index)

        if data_key == key:
          yield self.process_result(tree, result_to, data_value)
          continue

        if data_key is None:
          continue
        if data_value is None:
          continue

        yield from self.tree_by_key(
          data_value, key, tree, result_to=result_to
        )

  def data_by_tree(self, tree: str) -> dict:
    if Tree.ROOT:
      tree = tree.replace(
        self.join_tree(Tree.ROOT, ''), '', 1
      )

    tree_keys = tree.split(Tree.DELIMITER)
    inner_data = self.data

    for key in tree_keys:
      if key.startswith(Tree.LIST_INDEX_WRAPPER[0]):
        inner_data = inner_data[int(key[1:-1])]
      else:
        inner_data = inner_data[key]

    return inner_data

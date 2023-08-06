#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from typing import Optional
from pprint import pprint

from .config import FD, Tree, Key
from .utils import FileIO

from .run import PageDataTree


def main(input_filepath: str, output_filepath: str, key: str, tree: str) -> Optional[NotImplementedError]:
    file_io = FileIO(input_filepath)
    file_data = file_io.load()

    pdt = PageDataTree(file_data)

    if key:
      pdt_tree = pdt.tree_by_key(
        key=key,
        result_to=(Key.SAVE if output_filepath else Key.SHOW)
      )
    else:
      pdt_tree = (tree,)

    for tree in pdt_tree:
      if not tree:
        continue

      tree_data = pdt.data_by_tree(tree)

      if output_filepath:
        if output_filepath == FD.STDOUT:
          print(tree)
          pprint(tree_data)
          print()
          continue

        if key:
          raise NotImplementedError('Use `-t` flag to dump a value for `tree`')

        file_io.dump(tree_data, output_filepath)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='JSON Tree parser')
  parser.add_argument('-i', type=str, help='[i]nput filepath')
  parser.add_argument('-o', type=str, help='[o]utput filepath')
  parser.add_argument('-k', type=str, help='[k]ey to search (generate) tree for')
  parser.add_argument('-t', type=str, help='[t]ree to save the data from')
  parser.add_argument('-l', type=int, help='[l]limit stdout')
  parser.add_argument('-fk', type=str, help='[f]ilter stdout by must have `key`')
  parser.add_argument('-fv', type=str, help='[f]ilter stdout by must have `value`')
  args = parser.parse_args()

  input_filepath = args.i
  output_filepath = args.o
  key = args.k
  tree = args.t

  if not input_filepath:
    print('Input filepath required')
    exit()
  if (not key) and (not tree):
    print('Key or Tree is required')
    exit()

  if args.l:
    # decrements the limit befor returning the `tree`
    Tree.SEARCH_LIMIT = (args.l+1)

  Tree.SEARCH_FILTER_KEY = args.fk or Tree.SEARCH_FILTER_KEY
  Tree.SEARCH_FILTER_VALUE = args.fv or Tree.SEARCH_FILTER_VALUE

  main(input_filepath, output_filepath, key, tree)

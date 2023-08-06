# TODO: use namedtuple


class FD:
  """File and Directory
  """
  ROOT_DIRECTORY = 'data'
  FILE_EXTENSION = '.json'
  STDOUT = '*'


class Tree:
  ROOT = 'root'
  DELIMITER = ' -> '
  LIST_INDEX_WRAPPER = "[{index}]"
  SEARCH_LIMIT = -1
  SEARCH_FILTER_KEY = ''
  SEARCH_FILTER_VALUE = ''


class Key:
  SHOW = 'print'
  SAVE = 'return'

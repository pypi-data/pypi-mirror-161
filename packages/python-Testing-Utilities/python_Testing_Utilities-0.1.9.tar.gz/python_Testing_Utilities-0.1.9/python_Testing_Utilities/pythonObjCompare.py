import copy
import json

maxRecursionDepth = 100

class DataObjectToComplexToCompare(Exception):
    pass

def assertObjectsEqual(unittestTestCaseClass, first, second, msg, ignoredRootKeys=[]):
  cleanedfirst = copy.deepcopy(first)
  cleanedsecond = copy.deepcopy(second)

  for key_to_ignore in ignoredRootKeys:
    keyPresentInEither = False
    if key_to_ignore in cleanedfirst:
      keyPresentInEither = True
    if key_to_ignore in cleanedsecond:
      keyPresentInEither = True
    if keyPresentInEither:
      cleanedfirst[key_to_ignore] = 'ignored'
      cleanedsecond[key_to_ignore] = 'ignored'

  if (objectsEqual(cleanedfirst, cleanedsecond)):
    return

  ignoredKeysMsg = ""
  if ignoredRootKeys is not None:
    if len(ignoredRootKeys) > 0:
      ignoredKeysMsg = " (Ignored keys " + str(ignoredRootKeys) + " ignored)"
  print("Object mismatch" + ignoredKeysMsg)
  a = json.dumps(str(cleanedfirst), sort_keys=True)
  b = json.dumps(str(cleanedsecond), sort_keys=True)
  print(a)
  print("--")
  print(b)

  unittestTestCaseClass.assertTrue(False, msg)

def _objectsEqual(first, second, recursionLevel):
    if recursionLevel > maxRecursionDepth:
        raise DataObjectToComplexToCompare("Data object two complex to compare")
    if type(first) != type(second):
        return False
    if first is None:
        return second is None
    if isinstance(first, str):
        return first == second
    if isinstance(first, bytes):
        return first == second
    if isinstance(first, int):
        return first == second
    if isinstance(first, list):
        return _listEqual(first, second, recursionLevel+1)
    if isinstance(first, dict):
        return _dictEqual(first, second, recursionLevel+1)

def objectsEqual(first, second):
    return _objectsEqual(first, second, 0)

def _numTimesItemIsInList(item, list, recursionLevel):
    ret = 0
    for x in list:
        if _objectsEqual(x,item, recursionLevel):
            ret += 1
    return ret

def _makeHashable(item):
    if isinstance(item, list):
        return "LIS:" + str(item) #not great but good enough
    return item

def _dictEqual(first, second, recursionLevel):
  if not _listEqual(list(first.keys()), list(second.keys()), recursionLevel):
    return False
  # we have the same keys - so just have to check values
  for key in first.keys():
    if not _objectsEqual(first[key], second[key], recursionLevel):
      return False

  return True

def _listEqual(first, second, recursionLevel):
    if len(first) != len(second):
        return False
    data = {}
    for x in first:
        data[_makeHashable(x)] = {
            "item": x,
            "times_in_first": 0,
            "times_in_second": 0
        }
    for x in second:
        data[_makeHashable(x)] = {
            "item": x,
            "times_in_first": 0,
            "times_in_second": 0
        }

    for x in data:
        data[x]["times_in_first"] = _numTimesItemIsInList(data[x]["item"],first, recursionLevel)
        data[x]["times_in_second"] = _numTimesItemIsInList(data[x]["item"],second, recursionLevel)
        if data[x]["times_in_first"] != data[x]["times_in_second"]:
            return False

    return True

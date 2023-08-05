# Assert multi line stirngs are equal giving a easy to read comparison

def assertMultiLineStringsEqual(str1, str2, testClass, msg="Strings don't match", str1Name="str1", str2Name="str2"):
  a = areMultiLinesStringsEqual(str1, str2, str1Name, str2Name)
  if a is None:
    return
  print(a)
  testClass.assertTrue(False,msg=msg)

def _appendText(outObj, line):
  outObj["text"] = outObj["text"] + line + "\n"

def _getStringOut(strArr, mismatchLines):
  res = ""
  lineNum = 0
  for curLine in strArr:
    lineNum = lineNum + 1
    mismatched = False
    if mismatchLines is None:
      mismatched = True
    else:
      if lineNum in mismatchLines:
        mismatched = True
    if mismatched:
      res += "*{:0>3d}: {}:".format(lineNum,curLine)
    else:
      res += " {:0>3d}: {}:".format(lineNum,curLine)
    res += "\n"
  return res

#Used for testing. Return output text or None if they match
def areMultiLinesStringsEqual(str1, str2, str1Name, str2Name):
  str1Arr = None
  if str1 != None:
    str1Arr = str1.split("\n")
  str2Arr = None
  if str2 != None:
    str2Arr = str2.split("\n")

  outText = {"text":""}

  if str1 is None:
    if str2 is None:
      return None
    _appendText(outText, str1Name + " lines:None")
    _appendText(outText, str2Name + " lines:" + str(len(str2Arr)))
    _appendText(outText, "Mismatched line numbers: [ ALL ]")
    _appendText(outText, str1Name + "-----")
    _appendText(outText, " ** NONE **")
    _appendText(outText, "")
    _appendText(outText, str2Name + "-----")
    _appendText(outText, _getStringOut(str2Arr, None))

    return outText["text"]
  if str2 is None:
    _appendText(outText, str1Name + " lines:" + str(len(str1Arr)))
    _appendText(outText, str2Name + " lines:None")
    _appendText(outText, "Mismatched line numbers: [ ALL ]")
    _appendText(outText, str1Name + "-----")
    _appendText(outText, _getStringOut(str1Arr, None))
    _appendText(outText, str2Name + "-----")
    _appendText(outText, " ** NONE **")
    _appendText(outText, "")

    return outText["text"]

  if str1==str2:
    return None

  minLen = len(str1Arr)
  maxLen = minLen
  if len(str1Arr)==len(str2Arr):
    _appendText(outText, "Strings both have " + str(minLen) + " lines")
  else:
    _appendText(outText, str1Name + " lines:" + str(len(str1Arr)))
    _appendText(outText, str2Name + " lines:" + str(len(str2Arr)))
    if len(str2Arr) < minLen:
      minLen = len(str2Arr)
    else:
      maxLen = len(str2Arr)

  mismatchLines = []
  for curLine in range(0,minLen):
    if str1Arr[curLine] != str2Arr[curLine]:
      mismatchLines.append((curLine+1))

  for curLine in range(minLen,maxLen):
    mismatchLines.append((curLine+1))

  _appendText(outText, "Mismatched line numbers: " + str(mismatchLines))

  _appendText(outText, str1Name + "-----")
  _appendText(outText, _getStringOut(str1Arr, mismatchLines))

  _appendText(outText, str2Name + "-----")
  _appendText(outText, _getStringOut(str2Arr, mismatchLines))

  return outText["text"]

import requests
import json
import time

def _asserter(testCaseInstance, msg):
  if testCaseInstance is None:
    raise Exception(msg)
  testCaseInstance.assertTrue(False, msg=msg)

def _callService(testCaseInstance, url, headers, method, dataDICT, maxRetries, expectedResponses, files):
  result = None
  targetURL = url
  headers = {}
  data = None
  requestsFn = None
  if method=='get':
    requestsFn = requests.get
  if method=='post':
    if dataDICT is not None:
      headers['content-type'] = 'application/json'
      data=json.dumps(dataDICT)
    requestsFn = requests.post
  if method=='put':
    if dataDICT is not None:
      headers['content-type'] = 'application/json'
      data=json.dumps(dataDICT)
    requestsFn = requests.put
  if method=='delete':
    requestsFn = requests.delete

  if requestsFn is None:
    _asserter(testCaseInstance,"Invalid method")
    return None, None

  numTries = 0
  unsucessful = True
  while unsucessful:
    unsucessful = False
    if numTries > 0:
      print(" Call failed (try " + str(numTries) + ") - retrying...")
      time.sleep(1)
    numTries = numTries + 1
    try:
      result = requestsFn(
        targetURL,
        data=data,
        headers=headers,
        files=files
      )
    except Exception as err:
      unsucessful = True
      if numTries > maxRetries:
        print("We have been trying too many times - giving up")
        raise err


  if result.status_code not in expectedResponses:
    print("Sending " + method + " to ", targetURL)
    if dataDICT is not None:
      print(" data:", dataDICT)
    if files is not None:
      print(" sending multi part files not shown")
    print("Got response ",result.status_code)
    print("     ",result.text)

    _asserter(testCaseInstance,"Did not get expected response")
    return None, None
  return result.text, result.status_code

#def input as multipart files
def callServiceSendMultiPartFiles(testCaseInstance, url, headers, method, maxRetries, expectedResponses, files):
  return _callService(testCaseInstance, url, headers, method, None, maxRetries, expectedResponses, files=files)

def callServiceSendMultiPartFilesAndData(testCaseInstance, url, headers, method, maxRetries, expectedResponses, files, data):
  return _callService(testCaseInstance, url, headers, method, data, maxRetries, expectedResponses, files=files)

#sends input as JSON
def callService(testCaseInstance, url, headers, method, dataDICT, maxRetries, expectedResponses):
  return _callService(testCaseInstance, url, headers, method, dataDICT, maxRetries, expectedResponses, files=None)


def callGetService(testCaseInstance, url, headers, maxRetries, expectedResponses):
  return callService(testCaseInstance, url, headers, "get", None, maxRetries, expectedResponses)

def callPostService(testCaseInstance, url, headers, POSTdict, maxRetries, expectedResponses):
  return callService(testCaseInstance, url, headers, "post", POSTdict, maxRetries, expectedResponses)

def callPutService(testCaseInstance, url, headers, PUTdict, maxRetries, expectedResponses):
  return callService(testCaseInstance, url, headers, "put", PUTdict, maxRetries, expectedResponses)

def callDeleteService(testCaseInstance, url, headers, maxRetries, expectedResponses):
  return callService(testCaseInstance, url, headers, "delete", None, maxRetries, expectedResponses)

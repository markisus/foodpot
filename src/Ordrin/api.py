import urllib2, re, json, hashlib

_key = ""
_url = ""

_currEmail = ""
_currPass = ""

_errs = []

_checkNums = "^\s*\d+\s*$"
_checkEmail = "^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$"
_checkCC = "^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})$"

def initialize(key, url):
  global _key, _url
  _key = key
  _url = url
  
def setCurrAcct(currEmail, currPass):
  global _currEmail, _currPass
  if not re.match(_checkEmail, currEmail):
    _errs.append("api.setCurrAcct - validation - email (invalid)")
  _currEmail = currEmail
  _currPass = hashlib.sha256(currPass).hexdigest()

def _request(type, *args):
  dataParams = []
  urlParams = []
  
  if not _key:
    _errs.append(("initialization", "must initialize with developer key for API"))
  elif not _url:
    _errs.append(("initialization", "must initialize with site at which API is running"))
  
  # seperate arguments into appropriate lists
  for i in args:
    i = str(i)
    if re.search("=", i):
      dataParams.append(i)
      print i
    else: 
      if i == "uN": # this is to prevent the header for the user API going out with the makeAcct function
        iN = "u"
        urlParams.append(iN)
      else:
        urlParams.append(i)

  append = "/" + "/".join(urlParams)
  print "URL: " + _url
  print "append: " + append
  
  opener = urllib2.build_opener(urllib2.HTTPHandler)
  request = urllib2.Request(_url + append, "&".join(dataParams))
  request.add_header('X-NAAMA-CLIENT-AUTHENTICATION', 'id="' + _key + '", version="1"')
  request.add_header("Content-Type", "application/x-www-form-urlencoded");
  
  if args[0] == "u" or args[0] == "o":
    if not _currEmail or not _currPass:
      _errs.append(("user API", "valid email and password required to access user API"))
    print "Hash is being created."
    hash = hashlib.sha256(_currPass + _currEmail + append).hexdigest()
    print "hash: " + hash
    request.add_header("X-NAAMA-AUTHENTICATION", 'username="' + _currEmail + '", response="' + hash + '", version="1"')
    print "header looks like: " + 'username="' + _currEmail + '", response="' + hash + '", version="1"'
  
  if _errs:
    print _errs
    return _errs
    raise
  
  request.get_method = lambda: type
  call = opener.open(request)
  
  result = call.read()
  print result # use next line for production -- this one is for testing
  return json.loads(result)
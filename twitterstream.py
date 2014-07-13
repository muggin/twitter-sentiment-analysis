import oauth2 as oauth
import urllib2 as urllib

_default_keys_path = '/Users/Wojtek/Documents/Projekty/Twitter_Sentiment_Analysis/keys.txt'
_debug = 0

oauth_token    = None
oauth_consumer = None

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

http_method = 'GET'
http_handler  = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

'''
Read Twitter API and access keys from external file.
File structure:
<API key>;<API secret>;<Access key>;<Access secret>
'''
def loadkeys(file_path = _default_keys_path):
    key_description = ['api_key', 'api_secret', 'access_token_key', 'access_token_secret']
    with open(file_path, 'r') as file:
        key_list = file.read().split(';')

    return dict(zip(key_description, key_list))

'''
Initialize oauth variables with Twitter access keys.
'''
def setoath(file_path = _default_keys_path):
    global oauth_token
    global oauth_consumer
    keys = loadkeys(file_path)
    oauth_token     = oauth.Token(key=keys['access_token_key'], secret=keys['access_token_secret'])
    oauth_consumer  = oauth.Consumer(key=keys['api_key'], secret=keys['api_secret'])

'''
Construct, sign, and open a twitter request using the credentials above.
'''
def twitterreq(url, method, parameters):
  req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                             token=oauth_token,
                                             http_method=http_method,
                                             http_url=url, 
                                             parameters=parameters)

  req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

  headers = req.to_header()

  if http_method == 'POST':
    encoded_post_data = req.to_postdata()
  else:
    encoded_post_data = None
    url = req.to_url()

  opener = urllib.OpenerDirector()
  opener.add_handler(http_handler)
  opener.add_handler(https_handler)

  response = opener.open(url, encoded_post_data)

  return response

def fetchsamples():
  url = 'https://stream.twitter.com/1/statuses/sample.json'
  parameters = []
  response = twitterreq(url, 'GET', parameters)
  for line in response:
    print line.strip()

if __name__ == '__main__':
    setoath()
    fetchsamples()

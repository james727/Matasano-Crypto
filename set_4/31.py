import web
import hmac
from os import urandom
import time

urls = ('/(.+)', 'index')
app = web.application(urls, globals())
KEY = urandom(16)

def get_params(params):
    pairs = params.split('&')
    if len(pairs) == 1:
        return {}
    return {pair.split('=')[0]:pair.split('=')[1] for pair in pairs}

def insecure_compare(key, filename, signature):
    real_signature = hmac.hmac(key, filename)
    print real_signature
    if len(signature) != len(real_signature):
        return '500 - invalid signature'
    for i in range(len(signature)):
        if signature[i] != real_signature[i]:
            return '500 - invalid signature'
        time.sleep(.01)
    return '200'

class index:
    def GET(self, params):
        params = get_params(params)
        if len(params) == 0:
            return ""
        filename = params['file'].encode('ascii')
        signature = params['signature'].encode('ascii')
        return insecure_compare(KEY, filename, signature)

if __name__ == "__main__":
    app.run()

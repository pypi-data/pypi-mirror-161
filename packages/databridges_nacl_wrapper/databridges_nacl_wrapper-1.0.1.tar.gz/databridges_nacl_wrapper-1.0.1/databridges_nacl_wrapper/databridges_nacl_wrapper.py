""" DataBridges Python nacl wrapper for databridges library.
    https://www.databridges.io/ 

    Copyright 2022 Optomate Technologies Private Limited.

    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import base64
import nacl.secret
import nacl.utils
from nacl import encoding

class databridges_nacl_wrapper:

    def __init__(self):
        self.secret = None

    def write(self, plaintext):
        if not plaintext:
            raise dbnwError("INVALID_DATA" , "")

        if not self.secret:
            raise  dbnwError("INVALID_SECRET" , "")
        try:
            secretKey = self.secret.encode("utf-8")
            nonce = nacl.utils.random(24)
            box = nacl.secret.SecretBox(secretKey)
            estrdata = box.encrypt(plaintext.encode('utf-8'), nonce, encoding.Base64Encoder)
            restrdata = estrdata.decode('utf-8')
            rnonce = base64.b64encode(nonce).decode('utf-8')
            restrdata2 = restrdata[len(rnonce): len(restrdata)]
            return  rnonce + ":" + restrdata2
        except Exception as e:
            raise dbnwError("NACL_EXCEPTION" , e)

    def read(self, data):

        if not data:
            raise dbnwError("INVALID_DATA" , "")

        if not self.secret:
            raise  dbnwError("INVALID_SECRET" , "")

        if ":" not in data:
            raise dbnwError("INVALID_DATA", "")
        try:
            secretKey = self.secret.encode("utf-8")
            box = nacl.secret.SecretBox(secretKey)
            encrypted = data.split(':')  # We decode the two bits independently
            nonce = base64.b64decode(encrypted[0])
            encrypted = base64.b64decode(encrypted[1])
            estrdata = box.decrypt(encrypted, nonce)
            return  estrdata.decode('utf-8')
        except Exception as e:
            print ("issue here ", e)
            raise dbnwError("NACL_EXCEPTION" , e)



class dbnwError(Exception):
    def __init__(self, codeext="", message=""):
        self.source = "DBLIB_NACL_WRAPPER"
        self.code = codeext
        self.message = message

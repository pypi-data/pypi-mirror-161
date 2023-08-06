# pytest framework ---------------------------------------------
import requests
from . import siesta
from .. import attrdict
import time
import sys
import os
import xmlrpc.client
from io import IOBase
import json
from . import apidoc
from urllib.parse import urlparse, quote


has_http2 = True
try:
    from ..protocols.sock.impl.http2 import client as h2client
except ImportError:
    has_http2 = False

has_http3 = False
if os.name != 'nt' and sys.version_info >= (3, 6):
    try:
        from ..protocols.sock.impl.http3 import client as h3client
    except ImportError:
        pass
    else:
        has_http3 = True


class Stub:
    def __init__ (self, cli, baseurl, headers = None):
        self._cli = cli
        self._headers = headers or {}
        self._baseurl = self.norm_baseurl (baseurl)

    def __enter__ (self):
        return self

    def __exit__ (self, *args):
        pass

    def __getattr__ (self, name):
        self._method = name
        return self.__proceed

    def __proceed (self, uri, *urlparams, **params):
        __data__ = {}
        if urlparams:
            if isinstance (urlparams [-1], dict):
                __data__, urlparams = urlparams [-1], urlparams [:-1]
            uri = uri.format (*urlparams)
        __data__.update (params)
        uri = self._baseurl + uri
        return self.handle_request (uri, __data__)

    def norm_baseurl (self, uri):
        uri = uri != '/' and uri or ''
        while uri:
            if uri [-1] == '/':
                uri = uri [:-1]
            else:
                break
        return uri

    def handle_request (self, uri, data):
        if self._method in ('post', 'put', 'patch', 'upload'):
            return getattr (self._cli, self._method) (uri, data, headers = self._headers)
        else:
            return getattr (self._cli, self._method) (uri, headers = self._headers)


class Target:
    '''
    f = Target ('http://localhost:5000')
    f.get ("/v1/accounts/me") # use HTTP/1.x
    f.post ("/v1/accounts/me", data = {})
    f.post ("/v1/accounts/me", json = {})
    f.h2.get ("/v1/accounts/me") # use HTTP/2
    f.h3.get ("/v1/accounts/me") # use HTTP/3
    with f.selenium () as b:
        b.navigate ('/')
    with f.stub ('/v1/accounts') as s:
        s.get ("/{}", 'me')
    '''

    def __init__ (self, endpoint, api_call = False, session = None, temp_dir = None, headers = None):
        self.endpoint = endpoint
        self.temp_dir = temp_dir
        self.s = session or requests.Session (); self.s.verify = False
        self._api_call = api_call
        self._headers = headers or {}
        self._cloned = None

        if not self._api_call:
            self.axios = Target (endpoint, True, session = self.s, headers = self._headers)
        else:
            self.set_default_header ('Accept', "application/json")
            self.set_default_header ('Content-Type', "application/json")

        self.siesta = siesta.API (endpoint, reraise_http_error = False, session = self.s, headers = self._headers)
        self._driver = None
        self.h2 = self.http2 = has_http2 and h2client.Session (endpoint, self._headers) or None
        self.h3 = self.http3 = has_http3 and h3client.Session (endpoint, self._headers) or None

    def selenium (self, agent = "chrome"):
        import chromedriver_autoinstaller
        driver_path = chromedriver_autoinstaller.install (path = os.path.expanduser ("~/.local/bin"))

        if self._driver:
            return self._driver

        from rs4.webkit import Chrome
        ENDPOINT = self.endpoint
        TEMP_DIR = self.temp_dir
        class ChromeSession (Chrome):
            def get (self, url):
                return super ().get (ENDPOINT + url)

            def capture (self):
                super ().capture (os.path.join (TEMP_DIR, 'selenium.jpg'))

        self._driver = ChromeSession (driver_path, headless = True)
        return self._driver

    def clone (self):
        if self._cloned:
            return self._cloned
        self._cloned = t = Target (self.endpoint, self._api_call, session = self.s)
        return t

    def new (self):
        return Target (self.endpoint, self._api_call)

    def set_jwt (self, token = None):
        self.siesta._set_jwt (token)
        if self._api_call:
            self.set_default_header ('Authorization', "Bearer " + token)

    def sync (self):
        if self.driver:
            for cookie in self.driver.cookies:
                if 'httpOnly' in cookie:
                    httpO = cookie.pop('httpOnly')
                    cookie ['rest'] = {'httpOnly': httpO}
                if 'expiry' in cookie:
                    cookie ['expires'] = cookie.pop ('expiry')
                self.s.cookies.set (**cookie)

            for c in self.s.cookies:
                cookie = {'name': c.name, 'value': c.value, 'path': c.path}
                if cookie.get ('expires'):
                    cookie ['expiry'] = c ['expires']
                self.driver.add_cookie (cookie)

        return dict (
            cookies = [(c.name, c.value) for c in self.s.cookies]
        )

    def websocket (self, uri):
        from websocket import create_connection

        u = urlparse (self.endpoint)
        return create_connection ("ws://" + u.netloc + uri)

    def set_default_header (self, k, v):
        self._headers [k] = v

    def unset_default_header (self, k):
        try:
            del self._headers [k]
        except KeyError:
            pass

    def api (self, point = None):
        if point:
            return siesta.API (point, reraise_http_error = False, session = self.s, headers = self._headers)
        return self.siesta

    def __enter__ (self):
        return self

    def __exit__ (self, type, value, tb):
        self._close ()

    def __del__ (self):
        self._close ()

    def _close (self):
        pass

    def resolve (self, url):
        if url.startswith ("http://") or url.startswith ("https://"):
            return url
        else:
            return self.endpoint + url

    def _request (self, method, url, *args, **kargs):
        url = self.resolve (url)
        rf = getattr (self.s, method)
        if args:
            args = list (args)
            request_data = args.pop (0)
            args = tuple (args)
        else:
            try:
                request_data = kargs.pop ('data')
            except KeyError:
                request_data = {}

        headers = self._headers.copy ()
        if 'headers' in kargs:
            custom_headers = kargs.pop ('headers')
            if hasattr (custom_headers, 'append'):
                custom_headers = dict (custom_headers)
            headers.update (custom_headers)

        if 'files' in kargs:
            try: del headers ["Content-Type"]
            except KeyError: pass
        elif self._api_call and method in ('post', 'put', 'patch') and isinstance (request_data, dict):
            request_data = json.dumps (request_data)

        if request_data:
            resp = rf (url, request_data, *args, headers = headers, **kargs)
        else:
            resp = rf (url, *args, headers = headers, **kargs)

        if resp.headers.get ('content-type', '').startswith ('application/json'):
            try:
                resp.data = resp.json ()
            except:
                resp.data = {}

            if "__spec__" in resp.data:
                reqh = kargs.get ('headers', {})
                reqh.update (self.s.headers)
                for k, v in kargs.get ('files', {}).items ():
                    request_data [k] = '<FILE: {}>'.format (v.name)
                apidoc.log_spec (method.upper (), url, resp.status_code, resp.reason, reqh, request_data, resp.headers, resp.data)
        else:
            resp.data = resp.content
        return resp

    def get (self, url, *args, **karg):
        return self._request ('get', url, *args, **karg)

    def post (self, url, *args, **karg):
        return self._request ('post', url, *args, **karg)

    def upload (self, url, data, **karg):
        files = {}
        for k in list (data.keys ()):
            if isinstance (data [k], IOBase):
                files [k] = data.pop (k)
        return self._request ('post', url, files = files, data = data, **karg)

    def put (self, url, *args, **karg):
        return self._request ('put', url, *args, **karg)

    def patch (self, url, *args, **karg):
        return self._request ('patch', url, *args, **karg)

    def delete (self, url, *args, **karg):
        return self._request ('delete', url, *args, **karg)

    def head (self, url, *args, **karg):
        return self._request ('head', url, *args, **karg)

    def options (self, url, *args, **karg):
        return self._request ('options', url, *args, **karg)

    def stub (self, baseurl = '', headers = {}):
        return Stub (self, baseurl, headers)

    def rpc (self, url, proxy_class = None):
        return (proxy_class or xmlrpc.client.ServerProxy) (self.resolve (url))
    xmlrpc = rpc

    def jsonrpc (self, url, proxy_class = None):
        import jsonrpclib
        return (proxy_class or jsonrpclib.ServerProxy) (self.resolve (url))

    def grpc (self):
        from tfserver import cli
        return cli.Server (self.endpoint)

    @property
    def http (self):
        return self

    @property
    def driver (self):
        return self.selenium ()


if __name__ == "__main__":
    if "--init" in sys.argv:
        apidoc.truncate_log_dir ()
    if "--make" in sys.argv:
        apidoc.build_doc ()
    if "--clean" in sys.argv:
        apidoc.truncate_log_dir (remove_only = True)

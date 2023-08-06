import requests

class RequestPool:
    def __init__ (self, pool_facor = 10):
        self.pool_facor = pool_facor
        self.s = requests.Session ()
        self.setup ()

    def setup (self):
        self.s.mount(
            'https://',
            requests.adapters.HTTPAdapter (pool_connections = self.pool_facor, pool_maxsize = self.pool_facor)
        )
        self.s.mount(
            'http://',
            requests.adapters.HTTPAdapter (pool_connections = self.pool_facor, pool_maxsize = self.pool_facor)
        )

    def acquire (self):
        return self.s


RequestsPool = RequestPool

if __name__ == "__main__":
    p = RequestPool (10)
    with p.acquire () as s:
        print (p.get ("http://example.com"))
        print (s.get ("http://example.com"))

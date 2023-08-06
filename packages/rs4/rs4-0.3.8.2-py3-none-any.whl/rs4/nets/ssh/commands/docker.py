from . import default
import re

RX_spt = re.compile ("\s{2,}")

class Result (default.Result):
    def parse_output (self, outputs):
        lines = outputs.split ("\n")
        self.header = lines [0]
        d = {}
        if ' ps ' in self._cmd:
            for line in lines [1:-1]:
                d = RX_spt.split (line)
                self.data.append ({
                    'Container Name': d [-1],
                    'Created': d [3],
                    'Status': d [4],
                })
        elif ' stats ' in self._cmd:
            for line in lines [1:-1]:
                d = RX_spt.split (line)
                self.data.append ({
                    'Container Name': d [1],
                    'CPU %': d [2],
                    'Mem %': d [4],
                    'Mem Usage': d [3]
                })


if __name__ == "__main__":
    import subprocess

    cmd = "docker stats --no-stream"
    res = subprocess.run(cmd, shell = True, stdout = subprocess.PIPE)
    print (res.returncode)
    print (Result (res.stdout.decode ("utf8"), cmd).data)
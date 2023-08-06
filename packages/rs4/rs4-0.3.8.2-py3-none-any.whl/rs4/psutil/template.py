#! /usr/bin/env python3

# from rs4 import importer
# settings = importer.from_file ('settings', os.path.join (os.path.dirname (__file__), 'config/settings.py'))
import os
from rs4.psutil import service, daemon_class
from datetime import datetime, timedelta, timezone
import rs4
import getopt
import sys
import time

class DaemonService (daemon_class.SimpleDaemonClass):
    NAME = "daemom-service"
    def __init__ (self, working_dir):
        super ().__init__ (working_dir)
        self.logs = []

    def session (self):
        time.sleep (3.)

    def run (self):
        while self.active:
            try:
                self.session ()
            except KeyboardInterrupt:
                raise
            except:
                self.trace ()
                time.sleep (1)


VARIABLE_DIR = os.path.abspath (os.path.join (os.path.dirname (__file__), '../rscs/tasks'))

def main ():
    from rs4 import argopt

    argopt.add_option (None, '--help', 'disply help screen')
    argopt.add_option (None, '--devel', 'run as developement env.')

    options = argopt.get_options ()
    if '--help' in options:
        argopt.usage (True)
    try:
        cmd = options.argv [0]
    except IndexError:
        cmd = None

    servicer = service.Service (DaemonService.NAME, VARIABLE_DIR)
    if cmd and not servicer.execute (cmd):
        return
    if not cmd and servicer.status (False):
        raise SystemError ("daemon is running")

    DaemonService (VARIABLE_DIR).start ()


if __name__ == "__main__":
    main ()

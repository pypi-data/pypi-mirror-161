'''
Usage:

  from rs4 import argopt

  argopt.add_option (None, '--reset')
  argopt.add_option (None, '--limit=LIMIT', default = 0)
  options = argopt.get_options ()
  if '--help' in options:
    argopt.usage (True)
  if '--reset' in options:
    ...
  limit = options.get ('--limit', 0)
'''

import getopt as optparse
import sys
from .termcolor import tc
import math

def usage (exit = False):
    maxlen = max ([len (opt) + 2 for opt, desc in helps]) + 1
    print ("\nMandatory arguments to long options are mandatory for short options too.")
    for opt, desc in helps:
        if '---' in opt:
            color = tc.red
        else:
            color = tc.white
        spaces = maxlen - (len (opt) + 1)
        line = ('  {}{}{}'.format (color (opt), ' ' * spaces, desc))
        print (line)
    exit and sys.exit ()

def add_option (sname = None, lname = None, desc = None, default = None):
    global long_opts, short_opts, aliases, defaults

    sval, lval = None, None
    if lname:
        if lname.startswith ("--"):
            lname = lname [2:]
        try: lname, lval = lname.split ("=", 1)
        except ValueError: pass
        if lname in long_opts:
            return
        long_opts.append (lname + (lval is not None and "=" or ''))

    if sname:
        if sname.startswith ("-"):
            sname = sname [1:]
        try:
            sname, sval = sname.split ("=", 1)
        except ValueError:
            pass
        if sname in short_opts:
            return
        short_opts.append (sname + (sval is not None and ":" or ''))

    if (sname and lname) and ((sval is None and lval is not None) or (lval is None and sval is not None)):
        raise SystemError ('-{} and --{} spec not matched'.format (sname, lname))

    val = sval or lval
    if lname and sname:
        aliases ['--' + lname] = '-' + sname
        aliases ['-' + sname] = '--' + lname
        opt = "-{}, --{}".format (sname, lname)
    elif sname:
        opt = '-{}'.format (sname)
    elif lname:
        opt = '    --{}'.format (lname)
    if val:
        opt += '=' + val

    desc = desc or ''
    if default:
        if sname:
            defaults ['-' + sname] = default
        if lname:
            defaults ['--' + lname] = default
        if desc:
            desc += ' (default={})'.format (default)
        else:
            desc += 'default={}'.format (default)
    helps.append ((opt, desc))

def add_options (*names):
    for name in names:
        assert name and name [0] == "-"
        if name.startswith ("--"):
            add_option (None, name [2:])
        else:
            add_option (name [1:])

class ArgumentOptions:
    def __init__ (self, kopt = {}, argv = []):
        global aliases
        self.__kopt = kopt
        self.argv = argv

        for k, v in aliases.items ():
            if k in self.__kopt:
                self.__kopt [v] = self.__kopt [k]

    def __str__ (self):
        return str (list (self.items ()))

    def __contains__ (self, k):
        return k in self.__kopt

    def __getitem__ (self, k):
        if k not in self:
            raise KeyError (f'{k} is not found')
        return self.get (k)

    def __setitem__ (self, k, v):
        self.set (k, v)

    def __delitem__ (self, k):
        self.remove (k)

    def items (self):
        return self.__kopt.items ()

    def remove (self, k):
        del self.__kopt [k]
        if k in aliases:
            del self.__kopt [aliases [k]]

    def set (self, k, v):
        self.__kopt [k] = v
        if k in aliases:
            self.__kopt [aliases [k]] = v

    def get (self, k, v = None, astype = None, _raise = False):
        global defaults

        try:
            val = self.__kopt [k]
        except KeyError:
            return (v or defaults.get (k))

        if astype is not None:
            return astype (val)

        default = defaults.get (k)
        if default is None:
            return val

        if isinstance (default, bool):
            if val in ('yes', 'true', '1', 't', 'T', 'True'):
                return True
            elif val in ('no', 'false', '0', 'f', 'F', 'False'):
                return False
            else:
                raise ValueError
        elif isinstance (default, int):
            val = int (val)
        elif isinstance (default, float):
            val = float (val)
        return val

def get_options (argv = None):
    global long_opts, short_opts
    argopt = optparse.getopt (sys.argv [1:] if argv is None else argv, "".join (short_opts).replace ("=", ":"), long_opts)
    kopts_ = {}
    for k, v in argopt [0]:
        if k in kopts_:
            if not isinstance (kopts_ [k], list):
                kopts_ [k] = {kopts_ [k]}
            kopts_ [k].add (v)
        else:
            kopts_ [k] = v
    return ArgumentOptions (kopts_, argopt [1])
options = collect = get_options

def get_option (k, v = None):
    options = get_options ()
    return options.get (k, v)

helps = []
long_opts = ['help']
short_opts = []
aliases = {}
defaults = {}

def clear ():
    global long_opts, short_opts, defaults, aliases, helps

    helps = []
    long_opts = ['help']
    short_opts = []
    aliases = {}
    defaults = {}

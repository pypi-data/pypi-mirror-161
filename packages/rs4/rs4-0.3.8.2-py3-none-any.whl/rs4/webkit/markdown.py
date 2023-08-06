import re
import os
import datetime
from io import StringIO

class Markdown:
    def __init__ (self, path = None):
        self.path = path
        self.f = []
        self.toc = []

    def sizeof_fmt (self, num, suffix='B'):
        if not isinstance (num, (float, int)):
            return '-'
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def write_table (self, rows, *cols):
        if not cols:
            cols = list (rows [0].keys ())

        self.writeln ('')
        cols = [col.split ('__') for col in cols]
        self.writeln ('|'.join ([col [0].title () for col in cols]))
        cells = []
        for col in cols:
            if len (col) == 2:
                key, fmt = col
            else:
                key, fmt = col [0], None
            v = rows and rows [0][key]
            if v == '':
                v = None
            if isinstance (v, (int, float)) or fmt == 'bytes':
                cells.append ('--------:')
            else:
                cells.append ('---------')
        self.writeln ('|'.join (cells))

        for row in rows:
            rowd = []
            for col in cols:
                if len (col) == 2:
                    key, fmt = col
                else:
                    key, fmt = col [0], None
                v = row [key]
                if fmt == 'bytes':
                    v = self.sizeof_fmt (v)
                elif fmt == 'basename':
                    v = os.path.basename (v)
                elif isinstance (v, datetime.date):
                    v = v.strftime ('%Y-%m-%d %H:%M')
                elif v is None:
                    v = '-'
                rowd.append (str (v))
            self.writeln ('|'.join (rowd))
        self.writeln ('')

    def write (self, data):
        self.f.append (data)

    def writeln (self, line):
        if line.startswith ('#'):
            self.toc.append (line)
        self.f.append (line + '\n')

    def read (self):
        with open (self.path) as f:
            return f.read ()

    def close (self, toc_title = None):
        global ANCHORS
        if self.path:
            f = open (self.path, 'w')
        else:
            f = StringIO ()

        if toc_title:
            toc = [toc_title]
            for t in self.toc:
                lev, title = t.split (' ', 1)
                if len (lev) >= 4:
                    continue
                anchor = make_anchor (title)
                toc.append ('{}- [{}](#{})'.format ('  ' * (len (lev) - 1), title, anchor))
            f.write ('\n'.join(toc))
            f.write ('\n')
        f.write (''.join(self.f))
        ANCHORS = {}

        if self.path:
            f.close ()
        else:
            return f.getvalue ()
RX = re.compile ('[^-_a-z0-9]')
RX_HYPEN = re.compile ('[-]+')
ANCHORS = {}

def make_anchor (title):
    anchor = RX.sub ('', title.lower ().replace (' ', '-'))
    if anchor [0].isdigit ():
        anchor = 'anchor-' + anchor
    try:
        ANCHORS [anchor] += 1
    except KeyError:
        ANCHORS [anchor] = 0
    if ANCHORS [anchor]:
        anchor = anchor + '-' + str (ANCHORS [anchor])
    anchor = RX_HYPEN.sub ('-', anchor)
    return anchor


RX_TITLE = re.compile (r'^(#+)\s(.+)', re.M)
CODEBLOCK = re.compile (r'^```[a-z]+\n.+?```$', re.M|re.S)


def merge (sdir, output, baseurl = ''):
    global ANCHORS
    contents = []
    toc = []
    for md in sorted (os.listdir (sdir)):
        path = os.path.join (sdir, md)
        with open (path) as f:
            content = f.read ()
            contents.append (content)
            content_ = CODEBLOCK.sub ('', content)
            for lev, title in RX_TITLE.findall (content_):
                toc.append ((md, lev, title, make_anchor (title)))
    ANCHORS = {}

    md = Markdown ()
    md.writeln ('# Table of Content')
    for file, lev, title, anchor in toc:
        file = file if baseurl else ""
        line = " " * ((len (lev) - 1) * 2)
        if lev == '#':
            line += "- **[{}]({}{}#{})**".format (title, baseurl, file, anchor)
        else:
            line += "- {}".format (title)
        md.writeln (line)
    [ md.writeln ('') for _ in range (10) ]
    toc = md.close ()

    with open (output, 'w') as f:
        for content in contents:
            content = content.replace ('<!--toc-->', toc)
            f.write (content)
            f.write ("\n" * 10)
            # if baseurl and '# Table of Content' in content:
            #    break

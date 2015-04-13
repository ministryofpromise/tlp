#!/usr/bin/python

from tlp import TLP
import sys,pprint

f = open(sys.argv[1], "rw").read()
f = f.decode('utf8')
tlp = TLP(f)
print tlp.summary
pprint.pprint(tlp.iocs)
print tlp.keywords
#print tlp.fulltext

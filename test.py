#!/usr/bin/env python

from organize import *

for line in open('tests.csv', 'r'):
  line = line.rstrip()
  fields = line.split('@')
  f,r = prepare_masks(fields[1], fields[2], (fields[3] == '1'))
  new = re.sub(f,r, fields[0])
  if new != fields[4]:
    print f
    print r
    print "'%s'!='%s'" %(new, fields[4])
    exit(1)

def has_at_least(dict_a, dict_b):
  return set(dict_b.items()).issubset(set(dict_a.items()))

parser_tests = \
  [(r'Among *.* including subfolders find <f>\<f>\<n> and move to <f>\<n> overwriting if newer or larger', {
     'LoopPattern' : '*.*',
     'IncludeSubfolders' : 'including subfolders ',
     'FindMask' : r'<f>\<f>\<n>',
     'ReplaceMask' : r'<f>\<n>',
     'DoRecycle' : None,
     'OverwriteAlways' : None,
     'OverwriteIfNotOlder' : True,
     'OverwriteIfNotSmaller' : True,
    }),
    (r'Among *.* including subfolders find <a>D<b> case-insensitive and move to ..\D\<a>D<b> overwriting always', {
      'LoopPattern' : '*.*',
      'IncludeSubfolders' : 'including subfolders ',
      'FindMask' : r'<a>D<b>',
      'ReplaceMask' : r'..\D\<a>D<b>',
      'DoRecycle' : None,
      'OverwriteAlways' : 'always',
      'OverwriteIfNotOlder' : False,
      'OverwriteIfNotSmaller' : False,
    })]
for t in parser_tests:
  d = parse_instruction(t[0])
  expected = t[1]
  assert has_at_least(d, expected), "%s\n%s\n does not have at least \n%s\n" % (t[0], pformat(d), pformat(expected))

print "All tests succeeded"

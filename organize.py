#!/usr/bin/env python3

import re
from pprint import *
import argparse
import os.path
import glob
import shutil

import paths

def parse_instruction(s):
  p = r'(?i)^((In|Among(st)?) )*(?P<LoopPattern>.*?) (?P<IncludeSubfolders>including subfolders )?(?:except (?P<ExcludePattern>.*?) )?find (?P<FindMask>.*?) (?P<CaseInsensitive>case[- ]?insensitive )?(and )?(?:(move to (?P<ReplaceMask>.*?))|(?P<DoRecycle>recycle))( overwrit(ing|e) (?:(?P<OverwriteAlways>always)|if (?:(?P<OverwriteIfNotOlder0>newer)|(?P<OverwriteIfNotSmaller0>larger))( or (?:(?P<OverwriteIfNotOlder1>newer)|(?P<OverwriteIfNotSmaller1>larger)))*))*\w*?$'
  m = re.match(p, s)
  if m is None:
    return None
  info = m.groupdict()
  info['CaseInsensitive'] = info['CaseInsensitive'] is not None
  info['OverwriteIfNotOlder'] = info['OverwriteIfNotOlder0'] is not None \
                                or info['OverwriteIfNotOlder1'] is not None
  info['OverwriteIfNotSmaller'] = info['OverwriteIfNotSmaller0'] is not None \
                                or info['OverwriteIfNotSmaller1'] is not None
  return info

def prepare_masks(find_mask, replace_mask, case_insensitive=False):
  find_mask = re.sub(r'([\.\?\+\[\{\|\(\)\^\$\\])', r'\\\1', find_mask)
  find_mask = find_mask.replace('*', '[^""><]*')
  find_mask = re.sub(r'<(.+?)>(.*)<\1>', r"<\1>\2(?P=\1)", find_mask, flags=re.IGNORECASE)
  find_mask = re.sub(r'<(.+?)>', r'(?P<\1>.*)', find_mask, flags=re.IGNORECASE)
  replace_mask = re.sub(r'([\?\+\[\{\|\(\)\\])', r'\\\1', replace_mask)
  replace_mask = re.sub(r'<(.+?)>', r'\\g<\1>', replace_mask, flags=re.IGNORECASE)
  replace_mask = replace_mask.replace('*', '[^""><]*')
  find_mask = "^%s$" %(find_mask,)
  if case_insensitive:
    find_mask = "(?i)%s" %(find_mask,)
  return find_mask, replace_mask

def import_config_file(filename):
  def import_line(line):
    d = parse_instruction(line)
    if d is None:
      print ("ERROR Exiting! Failed to parse instruction:", line)
      return None
    fm, rm = prepare_masks(d['FindMask'], d['ReplaceMask'], d['CaseInsensitive'])
    d['FindMaskRegex'] = fm
    d['ReplaceMaskRegex'] = rm
    return d
  return [import_line(line.rstrip())
          for line in open(filename, 'r')]

def main():
  p = argparse.ArgumentParser()
  p.add_argument('configfile')
  args = p.parse_args()
  config_file_dir = os.path.dirname(os.path.abspath(args.configfile))
  config = import_config_file(args.configfile)

  with paths.cd(config_file_dir):
    for dirpath, dirnames, files in os.walk('.'):
      for d in config:
        for f in glob.glob(os.path.join(glob.escape(dirpath), d['LoopPattern'])):
          oldpath = os.path.relpath(f)
          if d['ExcludePattern'] is not None and re.search(d['ExcludePattern'], oldpath):
            continue
          if not os.path.isfile(oldpath):
            continue
          fm = d['FindMaskRegex']
          rm = d['ReplaceMaskRegex']
          newpath = re.sub(fm, rm, oldpath)
          if oldpath != newpath:
            ci = 0
            if d['CaseInsensitive']:
              ci = 1
            if d['DoRecycle']:
              print ("Cannot recycle %s in Python!" %(oldpath,))
              continue
            newdir = os.path.dirname(os.path.abspath(newpath))
            if not os.path.isdir(newdir):
              os.makedirs(newdir)
            if os.path.isfile(newpath):
              oldsize = os.path.getsize(oldpath)
              newsize = os.path.getsize(newpath)
              oldtime = os.path.getmtime(oldpath)
              newtime = os.path.getmtime(newpath)
              if d['OverwriteAlways'] \
              or (d['OverwriteIfNotOlder'] and oldtime >= newtime) \
              or (d['OverwriteIfNotSmaller'] and oldsize >= newsize):
                print ("%s -> %s" %(os.path.abspath(oldpath), os.path.abspath(newpath)))
                os.remove(os.path.abspath(newpath))
                shutil.move(os.path.abspath(oldpath), os.path.abspath(newpath))
            else:
              print ("%s -> %s" %(oldpath, newpath))
              shutil.move(os.path.abspath(oldpath), os.path.abspath(newpath))
if __name__ == '__main__':
  main()


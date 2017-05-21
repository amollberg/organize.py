#!/usr/bin/env python

import os

class cd:
  """Context manager for changing the current working directory"""
  def __init__(self, new_path):
    self.new_path = os.path.expanduser(new_path)

  def __enter__(self):
    self.saved_path = os.getcwd()
    os.chdir(self.new_path)

  def __exit__(self, etype, value, traceback):
    os.chdir(self.saved_path)

# Example:
#   evaluate_relative("/home/user/dir/sub", "../other/file.txt")
#    == "/home/user/dir/other/file.txt"
def evaluate_relative(base_dir, target_path):
  with cd(base_dir):
    return os.path.abspath(target_path)
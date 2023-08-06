'''
Api for dict and list
=====================

Basic Concepts
--------------

* To maintain immutability, create new objects without altering existing ones
* When transforming a dict or list, try to keep the original order as much as possible, since newer versions of python, the key order of the dict is available




'''
from .records import *
from .extensions import read_excel, read_csv, write_csv, write_excel, insert_csv, insert_excel
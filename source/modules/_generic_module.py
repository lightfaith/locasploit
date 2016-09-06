#!/usr/bin/env python3

from source.libs.include import *
from source.libs.define import *
from source.libs.parameters import *
from source.libs.author import *
import source.libs.io as io

tb = lib.tb

# DO NOT USE THIS MODULE, JUST INHERIT
class GenericModule():
    def __init__(self):
        self.db_access = []

    def run(self):
        log.err('You should not run this module!')


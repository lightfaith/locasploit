#!/usr/bin/env python3
"""
Class definition for connection to another system.
"""
from source.libs.include import *

class Connection:
    def __init__(self, description, connector, typ):
        self.description = description  # e.g. ssh://user@127.0.0.1:22
        self.connectors = [connector]   # list of connectors, first is the main one, others are for other functionality support (e.g. sftp)
        self.typ = typ                  # e.g. SSH


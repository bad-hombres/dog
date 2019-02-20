# -*- coding: utf8 -*-
import os
import sys
import errno
import sqlite3
import datetime

def mkdir_p(directory_name):
    try:
        os.makedirs(directory_name)
    except OSError as exc: 
        if exc.errno == errno.EEXIST and os.path.isdir(directory_name):
            pass

class Project:
    base_dir = os.path.join(os.environ["HOME"], ".dog")

    def __init__(self, name, logger):
        self.name = name
        self.path = os.path.join(Project.base_dir, name)
        self.logger = logger
        mkdir_p(self.path)

    @classmethod
    def list(klass):
        return os.listdir(Project.base_dir)
        
    def save_file(self, name, content):
        with open(os.path.join(self.path, name), "w") as f:
            f.write(content)
        self.logger.info("Saved file %s for project: %s" % (name, self.name))

    def save_data(self, data):
        d = datetime.datetime.now()
        try:
            sys.stdout.write("timestamp={}~type={}~project={}~{}\n".format(d, data[0], self.name, data[1]))
            sys.stdout.flush()

        except Exception as ex:
            self.logger.error("Could not save data to db: %s" % ex)

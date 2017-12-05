import os
import sys
import errno
import sqlite3

def mkdir_p(directory_name):
    try:
        os.makedirs(directory_name)
    except OSError as exc: 
        if exc.errno == errno.EEXIST and os.path.isdir(directory_name):
            pass

class Project:
    base_dir = os.path.join(os.environ["HOME"], ".dog")

    def __init__(self, name):
        self.name = name
        self.path = os.path.join(Project.base_dir, name)
        print self.path
        mkdir_p(self.path)

    def save_file(self, name, content):
        with open(os.path.join(self.path, name), "w") as f:
            f.write(content)

    def save_data(self, data):
        db = sqlite3.connect(os.path.join(self.path, "project.db"))
        c = db.cursor()

        try:
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='%s';" % data[0])
            if c.fetchone() is None:
                c.execute("CREATE TABLE %s (%s)" % (data[0], data[0]))

            c.execute("INSERT INTO %s values ('%s')" % (data[0], data[1]))
            print "[+] Data to save....%s" % data
        except Exception as ex:
            print ex
            print "[!] Could not save data to db"
        finally:
            c.close()
            db.commit()
            db.close()


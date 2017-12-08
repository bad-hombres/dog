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

    def __init__(self, name, logger):
        self.name = name
        self.path = os.path.join(Project.base_dir, name)
        self.logger = logger
        mkdir_p(self.path)

    def save_file(self, name, content):
        with open(os.path.join(self.path, name), "w") as f:
            f.write(content)
        self.logger.info("Saved file %s for project: %s" % (name, self.name))

    def save_data(self, data):
        db = sqlite3.connect(os.path.join(self.path, "project.db"))
        c = db.cursor()

        try:
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = '%s';" % data[0])
            self.logger.info("Checked Need create table")
            if c.fetchone() is None:
                self.logger.info("Need create table")
                c.execute("CREATE TABLE %s (%s)" % (data[0], data[0]))

            sql = """
                INSERT INTO %s 
                SELECT ? WHERE NOT EXISTS (SELECT 1 FROM %s WHERE %s = ?)
            """ % (data[0], data[0], data[0])
            c.execute(sql, (data[1], data[1]))
            self.logger.info("%s %s saved for project %s" % (data[0], data[1], self.name) )
        except Exception as ex:
            self.logger.error("Could not save data to db: %s" % ex)
        finally:
            c.close()
            db.commit()
            db.close()


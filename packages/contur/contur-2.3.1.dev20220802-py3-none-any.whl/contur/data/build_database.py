import os
import sqlite3
import shutil
import sys
from contextlib import closing

class BuildDB():
    """
    Build database through sql file
    """
    def __init__(self,dbname):
        self.dbname=dbname
        self.user_dir=os.environ.get('CONTUR_USER_DIR')


    def build_db(self):
        """
        Build database through run analyses.sql.

        :param name: your database name
        """
        dbfile=os.path.join(self.user_dir,self.dbname)
        sqlfile=os.path.join(os.environ.get('CONTUR_DATA_PATH'),"data","DB","analyses.sql")

        with closing(sqlite3.connect(dbfile)) as conn:
            with closing(conn.cursor()) as cur:
                sql_file=open(sqlfile)
                sql_as_string=sql_file.read()
                cur.executescript(sql_as_string)
        print(f'Successfully created {self.dbname}')

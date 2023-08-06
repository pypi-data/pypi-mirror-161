import logging

from django.db import OperationalError, InterfaceError, IntegrityError
from django.db.backends.mysql import base

logger = logging.getLogger('mysqldbwrapper')

def lost_connection(db_wrapper):
    def decorate(f):
        def wrapper(self, query, args=None):
            try:
                return f(self, query, args)
            except (OperationalError, InterfaceError) as e:
                logger.warn("MySQL server has gone away. Rerunning query: %s", query)
                if (
                    'MySQL server has gone away' in str(e) or
                    'Lost connection to MySQL server during query' in str(e) or 
                    'Too many connections' in str(e)
                ):
                    db_wrapper.connection.close()
                    db_wrapper.connect()
                    self.cursor = db_wrapper.connection.cursor()
                    return f(self, query, args)
                if e.args[0] in self.codes_for_integrityerror:
                    raise IntegrityError(*tuple(e.args))
                raise
        return wrapper
    return decorate


class DatabaseWrapper(base.DatabaseWrapper):
    def create_cursor(self, name=None):
        class CursorWrapper(base.CursorWrapper):
            @lost_connection(self)
            def execute(self, query, args=None):
                return self.cursor.execute(query, args)
            @lost_connection(self)
            def executemany(self, query, args):
                return self.cursor.executemany(query, args)
        cursor = self.connection.cursor()
        return CursorWrapper(cursor)
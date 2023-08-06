""" Wrapper for psycopg2. """
import os
import re

import dotenv
import psycopg2
import psycopg2.extras

dotenv.load_dotenv()

class Pgdb:
    """ Wrapper class. """

    def __init__(self):
        self.__connection = None

        # Selection of environment variables with a special ending
        # (DB_NAME, DB_HOST, DB_PORT, DB_USER, DB_PWD)
        # for automatic connection creation.
        creds = {
            '_'.join(key.split('_')[-2:]):value
            for key, value in os.environ.items()
            if re.search('(DB_NAME|DB_HOST|DB_PORT|DB_USER|DB_PWD)$', key)
            }

        # Connect to database.
        self.connect(
            creds.get('DB_HOST'),
            creds.get('DB_PORT', 5432),
            creds.get('DB_NAME'),
            creds.get('DB_USER'),
            creds.get('DB_PWD')
            )

    def connect(self,
                host,
                port,
                db_name,
                user,
                pwd,
                *,
                autocommit=True
                ):
        """ Database connection. """
        try:
            self.__connection = psycopg2.connect(
                host=host,
                port=port,
                dbname=db_name,
                user=user,
                password=pwd)

            self.__connection.autocommit = autocommit
        except psycopg2.Error as exc:
            print(f'===PGDBERR: {exc}')

    def disconnect(self):
        """ Connection closure. """
        if self.__connection:
            self.__connection.close()

    def execute(self, query, pars=None):
        """ Database query execution. """
        cursor = self.__connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        # Attemp to execute a request.
        try:
            cursor.execute(query, pars)
        except psycopg2.ProgrammingError as exc:
            print(f'===PGDBERR: {exc}')
            raise exc
        # Attempt to retrieve data from query results.
        # If no data (e.g. for DELETE) returns None.
        try:
            return cursor.fetchall()
        except psycopg2.ProgrammingError as exc:
            if str(exc) != 'no results to fetch':
                print(f'===PGDBERR: {exc}\n{query}')
        finally:
            cursor.close()

DB_OBJ = Pgdb()

"""
xenops.connector.storage
~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import logging
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectorStorage:
    """Connector storage class"""

    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, db_path):
        """
        Init ConnectorStorage

        :param str db_path:
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """Create storage tables"""
        trigger_table_query = """
        CREATE TABLE IF NOT EXISTS triggers (
            trigger_code varchar NOT NULL,
            last_run datetime NOT NULL,
            PRIMARY KEY (trigger_code)
        );
        """

        identifiers_table_query = """
        CREATE TABLE IF NOT EXISTS identifiers (
            type_code varchar NOT NULL,
            local_id varchar NOT NULL,
            object_id varchar NOT NULL,
            PRIMARY KEY (type_code, local_id, object_id)
        );
        """

        with self.connection as conn:
            cursor = conn.cursor()
            cursor.execute(trigger_table_query)
            cursor.execute(identifiers_table_query)

    def get_last_run(self, trigger_code):
        """
        Get last run from given trigger code

        :param str trigger_code:
        :return datetime.datetime:
        """
        query = """SELECT last_run FROM triggers WHERE trigger_code = ?"""

        try:
            return datetime.strptime(self.fetch_one_col(query, [trigger_code]), self.DATE_FORMAT)
        except Exception as e:
            logger.error(e)

        return None

    def get_local_id(self, datatype, object_id):
        """
        Get local id

        :param DataType datatype:
        :param str object_id:
        :return str:
        """
        query = """SELECT local_id FROM identifiers WHERE type_code = ? AND object_id = ?"""

        return self.fetch_one_col(query, [datatype.code, object_id])

    def get_object_id(self, datatype, local_id):
        """
        Get object id

        :param DataType datatype:
        :param str local_id:
        :return str:
        """
        query = """SELECT object_id FROM identifiers WHERE type_code = ? AND local_id = ?"""

        return self.fetch_one_col(query, [datatype.code, local_id])

    def fetch_one_col(self, query, params=None):
        """
        Fetch first row from and column given query

        :param str query:
        :param list params:
        :return:
        """
        params = params if params else []

        with self.connection as conn:
            cursor = conn.cursor()

            cursor.execute(query, params)
            result = cursor.fetchone()

            return result[0] if result else None

    def update_local_id(self, old_id, new_id):
        """
        Update local id

        :param str old_id:
        :param str new_id:
        :return bool:
        """
        query = """UPDATE identifiers SET local_id = ? WHERE local_id = ?"""

        return self.execute_query(query, [new_id, old_id])

    def set_last_run(self, trigger_code, date):
        """
        Set last run time

        :param str trigger_code:
        :param datetime.datetime date:
        :return bool:
        """
        query = """REPLACE INTO triggers (trigger_code, last_run) VALUES (?, ?)"""

        return self.execute_query(query, [trigger_code, date.strftime(self.DATE_FORMAT)])

    def set_object_id(self, datatype, local_id, object_id):
        """
        Set object id

        :param DataType datatype:
        :param str local_id:
        :param str object_id:
        :return bool:
        """
        query = """REPLACE INTO identifiers (type_code, local_id, object_id) VALUES (?, ?, ?)"""

        return self.execute_query(query, [datatype.code, local_id, object_id])

    def execute_query(self, query, params=None):
        """
        Execute given query

        :param str query:
        :param list params:
        :return bool:
        """
        params = params if params else []

        try:
            with self.connection as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
            return True
        except Exception as e:
            logger.error(e)

        return False

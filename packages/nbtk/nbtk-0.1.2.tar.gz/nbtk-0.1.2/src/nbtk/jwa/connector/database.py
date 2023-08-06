import pandas

import sqlalchemy

from nbtk.jwa.connector.connector import Connector, ConnectorConfiguration


class DatabaseConfiguration(ConnectorConfiguration):

    def __init__(
            self,
            host: str,
            port: int,
            username: str,
            password: str,
            database_name: str,
    ) -> None:
        super().__init__()
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._database_name = database_name

    def host(self):
        return self._host

    def port(self):
        return self._port

    def username(self):
        return self._username

    def password(self):
        return self._password

    def database_name(self):
        return self._database_name


class DatabaseConnector(Connector):

    def __init__(
            self,
            conf: DatabaseConfiguration,
            read_sql: str = None,
            write_table_name: str = None,
            if_write_table_exists: str = "fail",
    ) -> None:
        super().__init__()
        self._conf = conf
        self._read_sql = read_sql
        self._write_table_name = write_table_name
        self._if_write_table_exists = if_write_table_exists

    def read_as_data_frame(self) -> pandas.DataFrame:
        with self._connect() as connection:
            return pandas.read_sql(self._read_sql, connection)

    def write_data_frame(self, data: pandas.DataFrame) -> None:
        with self._connect() as connection:
            data.to_sql(self._write_table_name, connection, if_exists=self._if_write_table_exists)

    def _connect(self):
        sql_engine = sqlalchemy.create_engine(self._connection_string())
        return sql_engine.connect()

    def _connection_string(self):
        raise Exception("not implement")

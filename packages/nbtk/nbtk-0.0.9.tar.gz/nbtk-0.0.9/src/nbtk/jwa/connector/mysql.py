from urllib import parse

from nbtk.jwa.connector.database import DatabaseConfiguration, DatabaseConnector


class MysqlConnector(DatabaseConnector):

    def __init__(
            self,
            conf: DatabaseConfiguration,
            read_sql: str = None,
            write_table_name: str = None,
            if_write_table_exists: str = "fail"
    ) -> None:
        super().__init__(conf, read_sql, write_table_name, if_write_table_exists)

    def _connection_string(self):
        return "mysql+pymysql://{}:{}@{}:{}/{}".format(
            self._conf.username(),
            parse.quote_plus(self._conf.password()),
            self._conf.host(),
            self._conf.port(),
            self._conf.database_name(),
        )

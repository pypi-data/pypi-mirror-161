from connector.connector import Connector
from connector.database import DatabaseConfiguration
from connector.mysql import MysqlConnector
from connector.postgresql import PostgresqlConnector


class ConnectorFactory:
    def __init__(self, configuration_map: dict) -> None:
        super().__init__()
        self._configuration_map = configuration_map

    def input_connector(self) -> Connector:
        input_connector_map = self._configuration_map["input"]
        if input_connector_map is None:
            raise Exception("input is None")
        return self._extract_connector(input_connector_map)

    def output_connector(self) -> Connector:
        input_connector_map = self._configuration_map["output"]
        if input_connector_map is None:
            raise Exception("input is None")
        return self._extract_connector(input_connector_map)

    def _extract_connector(self, connector_map: dict) -> Connector:
        connector_type = connector_map["type"]
        if "mysql" == connector_type:
            return self._mysql_connector(connector_map)
        if "postgresql" == connector_type:
            return self._postgresql_connector(connector_map)
        raise Exception("type({}) not support".format(connector_type))

    def _mysql_connector(self, connector_map: dict):
        return MysqlConnector(
            conf=self._extract_database_configuration(connector_map),
            read_sql=connector_map["read_sql"],
            write_table_name=connector_map["write_table_name"],
            if_write_table_exists=connector_map.get("if_write_table_exists", "fail"),
        )

    def _postgresql_connector(self, connector_map: dict):
        return PostgresqlConnector(
            conf=self._extract_database_configuration(connector_map),
            read_sql=connector_map.get("read_sql", None),
            write_table_name=connector_map.get("write_table_name", None),
            if_write_table_exists=connector_map.get("if_write_table_exists", "fail"),
        )

    def _extract_database_configuration(self, connector_map: dict):
        return DatabaseConfiguration(
            host=connector_map["host"],
            port=connector_map["port"],
            username=connector_map["username"],
            password=connector_map["password"],
            database_name=connector_map["database_name"],
        )

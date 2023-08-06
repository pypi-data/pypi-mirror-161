import pandas


class ConnectorConfiguration:

    def __init__(self) -> None:
        super().__init__()


class Connector:

    def __init__(self) -> None:
        super().__init__()

    def read_as_data_frame(self) -> pandas.DataFrame:
        pass

    def write_data_frame(self, df: pandas.DataFrame) -> None:
        pass

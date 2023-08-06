from sklearn.cluster import MiniBatchKMeans

from connector.connector import Connector
from log.log_handler import LogHandler


class KMeans:
    def __init__(self, configuration: dict) -> None:
        super().__init__()
        self._logger = LogHandler()
        self._cols = configuration["cols"]
        self._n_clusters: int = int(configuration["n_clusters"])
        self._max_iter: int = int(configuration["max_iter"])
        self._batch_size: int = int(configuration.get("batch_size", 10000))
        self._cluster_id_column_name = configuration.get("cluster_id_column_name", "_cluster_id_")

    def run(self, connector_in: Connector, connector_out: Connector):
        data = connector_in.read_as_data_frame()
        data = data.dropna()
        ml_model = MiniBatchKMeans(
            n_clusters=self._n_clusters,
            max_iter=self._max_iter,
            batch_size=self._batch_size
        ).fit(data[self._cols].values)
        pred = ml_model.labels_
        data[self._cluster_id_column_name] = pred.astype("int")
        self._logger.info(data)
        connector_out.write_data_frame(data)

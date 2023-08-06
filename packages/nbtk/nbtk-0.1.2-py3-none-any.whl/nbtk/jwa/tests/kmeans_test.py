import os
import unittest

from nbtk.jwa.algorithm.k_means import KMeans
from nbtk.jwa.configuration.yaml_configuration import YamlConfiguration
from nbtk.jwa.connector.factory import ConnectorFactory
from nbtk.jwa.statics import root_path


class TestStringMethods(unittest.TestCase):

    def test(self):
        config_path = os.environ.get("CONFIG_PATH", os.path.join(root_path, "config.yaml"))
        configuration_map = YamlConfiguration(config_path).as_map()
        connector_factory = ConnectorFactory(configuration_map["connector"])
        input_connector = connector_factory.input_connector()
        output_connector = connector_factory.output_connector()
        # TODO algorithm should from factory which will generate the right algorithm instance base on type
        KMeans(configuration_map["algorithm"]).run(input_connector, output_connector)


if __name__ == '__main__':
    unittest.main()

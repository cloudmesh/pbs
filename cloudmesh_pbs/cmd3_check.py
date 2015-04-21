from cloudmesh_base.locations import config_file
from cloudmesh_base.ConfigDict import ConfigDict

from cloudmesh_base.logger import LOGGER

log = LOGGER(__file__)


class cmd3_check:
    @staticmethod
    def yaml(plugin):
        """
        This function reads in the cloudmesh cmd3.yaml file and tests
        if the requested plugin module is included in the yaml file.

        an example plugin name os "cloudmesh_pbs" to which automatically a
        .plugins will be appended if not specified.

        :return: True if the plugin is in the yaml file
        """
        filename = config_file("/cmd3.yaml")
        config = ConfigDict(filename=filename)

        if not plugin.endswith(".plugins"):
            testname = plugin + ".plugins"

        return testname in config["cmd3"]["modules"]


if __name__ == "__main__":
    print (cmd3_check.yaml("test"))
    print (cmd3_check.yaml("cloudmesh_pbs"))



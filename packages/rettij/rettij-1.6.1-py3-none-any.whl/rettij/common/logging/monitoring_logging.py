"""
This module implements a mechanism to log monitoring data to an InfluxDB database.

The database connection has to be established once and can then be used from the entire project.
"""
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError

import yaml
from rettij.common.logging_utilities import LoggingSetup
from rettij.common.validated_path import ValidatedFilePath


class _MonitoringLogger:
    """
    Logger used for writing monitoring data to an InfluxDB database.
    """

    def __init__(self, config_file_path: Optional[Union[Path, str]] = None) -> None:
        """
        Create a new MonitoringLogger using the InfluxDB client.

        :param config_file_path: InfluxDB client configuration file path. File has to be in YAML format. DB default configuration corresponds with Influx python client examples. Keys:
            - url (ip address + port; default: 'http://localhost:8086')
            - org (default: 'my-org')
            - bucket (default: 'my-bucket')
            - token (default: 'my-token')
        """
        if config_file_path:
            with open(ValidatedFilePath(config_file_path), "r") as fd:
                config = yaml.load(fd)
        else:
            config = {}

        self.db_url: str = config.get("url", "http://localhost:8086")
        self.db_org: str = config.get("org", "my-org")
        self.db_bucket: str = config.get("bucket", "my-bucket")
        self.db_token: str = config.get("token", "my-token")

        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)

        self.logger.debug(
            "Creating InfluxDB database client: "
            f"port={self.db_url}, "
            f"bucket={self.db_bucket}, "
            f"token={self.db_token}, "
        )

        self.db_client = InfluxDBClient(url=self.db_url, token=self.db_token, org=self.db_org)
        self.db_writer = self.db_client.write_api(write_options=SYNCHRONOUS)

    def log(self, measurement: str, entity_name: str, attr_name: str, attr_value: Union[int, str]) -> None:
        """
        Log the supplied data with the current time as timestamp.

        :param measurement: Type of measurement (i.e. Node type)
        :param entity_name: Entity that created the measurement
        :param attr_name: Attribute that is measured
        :param attr_value: Value of the measured attribute
        """
        values: List[Dict[str, Any]] = [
            {
                "measurement": measurement,
                "tags": {"user": "rettij", "entity_name": entity_name},
                "fields": {attr_name: attr_value},
            }
        ]
        try:
            self.db_writer.write(self.db_bucket, self.db_org, values)
            self.logger.debug(f"Wrote values to InfluxDB: {values}")
        except InfluxDBError as e:
            raise Exception("InfluxDB error occured while logging rettij data: ", e.message)

        # values = [{ "measurement": "TEST"), "tags": {"user": "test", "entity_name": "test"}, "fields": {"test-attr": "abcdef"} }]


monitoring_logger: Optional[_MonitoringLogger] = None
active: bool = False


def get_logger(config_file_path: Optional[Union[Path, str]] = None) -> _MonitoringLogger:
    """
    Retrieve the monitoring logger.

    :param config_file_path: Configuration for the initial logger setup.
    :return: New MonitoringLogger on the first call, existing object on successive calls.
    """
    global monitoring_logger
    global active
    if not monitoring_logger:
        monitoring_logger = _MonitoringLogger(config_file_path)
        active = True

    return monitoring_logger


def log(measurement: str, entity_name: str, attr_name: str, attr_value: Union[int, str]) -> None:
    """
    Log a monitoring message using the MonitoringLogger class.

    :param measurement: Type of measurement (i.e. Node type)
    :param entity_name: Entity that created the measurement
    :param attr_name: Attribute that is measured
    :param attr_value: Value of the measured attribute
    """
    if active:
        get_logger().log(measurement, entity_name, attr_name, attr_value)

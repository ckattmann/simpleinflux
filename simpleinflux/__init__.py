""" simpleinflux - A simple frontend for InfluxDB """

__version__ = "0.1.0"

default_host = "localhost"
default_port = 8086
user = ""
pw = ""
default_db = ""
default_measurement = ""


from .simpleinflux import ping
from .simpleinflux import get_influx_version
from .simpleinflux import create_database
from .simpleinflux import get_databases
from .simpleinflux import drop_database
from .simpleinflux import get_measurements
from .simpleinflux import write
from .simpleinflux import read_one
from .simpleinflux import read_latest
from .simpleinflux import read_all
from .simpleinflux import read_range
from .simpleinflux import read_special_range

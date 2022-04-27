""" simpleinflux - A simple frontend for InfluxDB """

__version__ = "0.0.3"

default_host = "localhost"
default_port = 8086
user = ""
pw = ""
default_db = ""


from .simpleinflux import ping
from .simpleinflux import get_databases
from .simpleinflux import get_measurements
from .simpleinflux import write
from .simpleinflux import read_one
from .simpleinflux import read_latest
from .simpleinflux import read_range
from .simpleinflux import read_special_range

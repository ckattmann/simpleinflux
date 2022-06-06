# simpleinflux
A simple Python frontend for InfluxDB

## Installation
```
pip install simpleinflux
```
`simpleinflux` only requires time, datetime, socket, and requests, so this should work on most systems.

## Quickstart
`simpleinflux` does not use a stateful connection object, only stateless functions which execute the underlying http requests and parse the results into a sane representation. The functions
```python
import simpleinflux

# host = 'localhost' and port = 8086 are assumed, read below to change:
simpleinflux.ping()
# -> True (or False)

simpleinflux.create_database('testDB')

simpleinflux.get_databases()
# -> ['_internal', 'testDB']

simpleinflux.write(db='testDB', measurement='test', timestamp=time.time(),  {'temperature_C': 21.2})
# -> True (or False)
simpleinflux.get_measurements(db='testDB')
# -> ['test']
simpleinflux.read_latest(db='testDB', measurement='test')
# -> {'time': 1654500223, 'temperature_C':21.2}

# Set default database and measurement on package level:
simpleinflux.default_db = 'testDB'
simpleinflux.default_measurement = 'test'

simpleinflux.write(timestamp=time.time(),  {'temperature_C': 21.3})
simpleinflux.read_latest()
# -> {'time': 1654500223, 'temperature_C':21.2}
```

## Changing host and port
`simpleinflux` assumes `host = 'localhost'` and `port = 8086`, which can be changed with optional arguments in most functions, e.g.
```python
ping_ok = simpleinflux.ping(host='localhost', port=28086)
data = simpleinflux.read_latest(measurement='test', host='localhost', port=28086)
```
or on the package level, e.g.
```python
simpleinflux.default_host = 'db.mydomain.com'
simpleinflux.default_port = 28086
data = simpleinflux.read_latest(measurement='test')
```

## Timestamps
All timestamps in InfluxDB are integers with explicit precision. `simpleinflux` uses second-precision as standard for both writes and reads. Other precisions can be set with the `precision` parameter in the `write`-function and the `output_time_unit` parameter in the various `read_`-functions.  
InfluxDB recommends using the broadest precision timestamp you and your data can get away with [for optimal compression](https://docs.influxdata.com/influxdb/v1.8/tools/api/#write-http-endpoint).  

## Function Reference
```ping(raise_on_error=True, host='localhost', port=8086)```  
*returns ```ping_ok [Bool]```*  
Checks the connection to the port, and to the InfluxDB-API and returns True when successful. Does not check the connection to only the host, because supporting ping on multiple platforms seems kind of messy.  
- *raise_on_error [Bool], default: True*  
If True, raises a `ConnectionError` if either the port or the API can't be reached
- *host [String], default: 'localhost'*  
The hostname of the system to be pinged
- *port [Int], default: 8086*  
The port of the system to be pinged

## Changelog

| Version | Date | Changes |
| :------ | :----| :----------- |
| 0.0.4 | 2022-04-28 | Bugfix: Put DESC into the query for read\_latest() so that it actually returns the last entry |
| 0.0.3 | 2022-04-27 | Changed read\_latest because it didn't work correctly with all influx versions (returns time=0) |
| 0.0.2 | 2022-04-26 | Added actual functionality |

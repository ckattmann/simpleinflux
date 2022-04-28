# simpleinflux
A simple frontend for InfluxDB

### Changelog
0.0.2 | 2022-04-26 | Added actual functionality
0.0.3 | 2022-04-27 | Changed read\_latest because it didn't work correctly with all influx versions (returns time=0)
0.0.4 | 2022-04-28 | Bugfix: Put DESC into the query for read\_latest() so that it actually returns the last entry

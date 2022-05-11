import time
import simpleinflux as influx

print("===================================")
print(influx.ping())

influx.default_db = "test"
measurement = "msmt"

print()
print("===================================")
databases = influx.get_databases()
print(databases)

print()
print("===================================")
measurements = influx.get_measurements()
print(measurements)

print()
print("===================================")
print(influx.default_db)
timestamp = int(time.time())
print(timestamp)
success = influx.write(measurement, timestamp, {"temperature": 12})
print(success)

print()
print("===================================")
data = influx.read_one(measurement, timestamp)
print(data)

print()
print("===================================")
data = influx.read_latest(measurement)
print(data)

print()
print("=========== read_special_range: today, no aggregation ========================")
data = influx.read_special_range(measurement, range_identifier="today")
print(data)

print()
print("=========== read_special_range: today, 10m aggregation ========================")
data = influx.read_special_range(
    measurement, range_identifier="today", aggregation="10m"
)
print(data)

print()
print(
    "=========== read_special_range: this week, 10m aggregation ========================"
)
data = influx.read_special_range(
    measurement, range_identifier="thisweek", aggregation="10m"
)
print(data)


print()
print(
    "=========== read_special_range: last 2 weeks, 10m aggregation ========================"
)
data = influx.read_special_range(
    measurement, range_identifier="last2weeks", aggregation="10m"
)
print(data)

print()
print(
    "=========== read_special_range: alltime, 10s aggregation ========================"
)
data = influx.read_special_range(
    measurement, range_identifier="alltime", aggregation="10s"
)
print(data)

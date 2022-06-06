import time
import datetime
import socket
import requests

import simpleinflux  # in order to access the package-level variables default_*

TIME_UNIT_MULTIPLIERS = {"s": 1000 ** 3, "ms": 1000 ** 2, "us": 1000, "ns": 1}
INFLUXDB_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def _substitute_defaults(
    host=None, port=None, db=None, measurement=None, measurement_required=False
):
    if not host:
        host = simpleinflux.default_host
    if not port:
        port = simpleinflux.default_port
    if not db:
        db = simpleinflux.default_db

    if not measurement_required:
        return host, port, db, None

    if not measurement:
        if not simpleinflux.default_measurement:
            raise ValueError(
                f"Measurement must be given as either parameter to the function or on the package level with simpleinflux.default_measurement='<measurement_name>'"
            )
        measurement = simpleinflux.default_measurement
    return host, port, db, measurement


def _port_reachable(host="localhost", port=8086):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) == 0


def ping(raise_on_fail=True, host="localhost", port=8086):

    # First, check if we can connect to the port:
    if not _port_reachable(host, port):
        if raise_on_fail:
            raise ConnectionError(
                f"Could not connect to port {port}, is influxd running?"
            )
        else:
            return False

    # Second, GET the /ping endpoint check if result is good (204):
    ping_endpoint_url = f"http://{host}:{port}/ping"
    try:
        res = requests.get(url=ping_endpoint_url)
    except requests.exceptions.ConnectionError:
        if raise_on_fail:
            raise ConnectionError(
                f"Could not connect to {ping_endpoint_url}, is influxd running?"
            ) from None
        return False

    if not res.ok:
        if raise_on_fail:
            raise ConnectionError(f"InfluxDB returned {res.status_code}: {res.text}")
        return False

    if res.status_code in (200, 204):
        return True

    raise ConnectionError(f"InfluxDB returned {res.status_code}: {res.text}")


def get_influx_version(host=None, port=None):

    host, port, _, _ = _substitute_defaults(host=host, port=port)

    ping_endpoint_url = f"http://{host}:{port}/ping"
    try:
        res = requests.get(url=ping_endpoint_url)
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Could not connect to {ping_endpoint_url}, is influxd running?"
        ) from None

    version_string = res.headers["X-Influxdb-Version"]
    return version_string


def _query(query, host=None, port=None, db=None, output_time_unit="s"):

    host, port, db, _ = _substitute_defaults(host=host, port=port, db=db)

    if query.startswith("DROP") or query.startswith("CREATE"):
        method = "POST"
    else:
        method = "GET"

    res = requests.request(
        method=method,
        url=f"http://{host}:{port}/query?db={db}",
        params={"q": query, "epoch": output_time_unit},
    )

    if not res.ok:
        raise ConnectionError(f"{query} returned {res.status_code}:{res.text}")

    if "error" in res.json()["results"][0]:
        error_message = res.json()["results"][0]["error"]
        raise ValueError(f"{query} returned: '{error_message}'")

    if "messages" in res.json()["results"][0]:
        print(res.json()["results"][0]["messages"])

    return res


def create_database(db, host=None, port=None):
    host, port, db, measurement = _substitute_defaults(host=host, port=port, db=db)
    query = f"CREATE DATABASE {db}"
    res = _query(query, host=host, port=port)
    return res.ok


def drop_database(db, host=None, port=None):
    host, port, db, measurement = _substitute_defaults(host=host, port=port, db=db)
    query = f"DROP DATABASE {db}"
    res = _query(query, host=host, port=port)
    return res.ok


def get_databases(host="localhost", port=8086):
    """ Execute the query "SHOW DATABASES" and parse the results """

    query = "SHOW DATABASES"

    res = _query(query, host=host, port=port)

    # Turn the wild output string into a list:
    databases = [l[0] for l in res.json()["results"][0]["series"][0]["values"]]
    return databases


def get_measurements(db=None, host="localhost", port=8086):

    query = "SHOW MEASUREMENTS"

    res = _query(query, host=host, port=port, db=db)

    # Turn the wild output string into a list:
    measurements = [l[0] for l in res.json()["results"][0]["series"][0]["values"]]
    return measurements


def write(
    timestamp,
    field_dict,
    measurement=None,
    db=None,
    tag_dict={},
    precision="s",
    additional_query_parameters={},
    host=None,
    port=None,
):

    host, port, db, measurement = _substitute_defaults(
        host=host, port=port, db=db, measurement=measurement, measurement_required=True
    )

    valid_precisions = ("n", "u", "ms", "s", "m", "h")
    if precision not in valid_precisions:
        raise ValueError(f"'precision' must one of {valid_precisions}, not {precision}")

    timestamp = int(timestamp)

    if not tag_dict:
        tag_string = ""
    else:
        # If exists, needs to start with a ',':
        tag_string = "," + ",".join([f"{n}={v}" for n, v in tag_dict.items()])
    field_string = ",".join([f"{n}={v}" for n, v in field_dict.items()])
    data_string = f"{measurement}{tag_string} {field_string} {timestamp}"

    res = requests.post(
        url=f"http://{host}:{port}/write",
        params={"db": db, "precision": precision, **additional_query_parameters},
        data=data_string.encode(),
        headers={"Content-Type": "application/octet-stream"},
    )
    return True


def read_one(
    timestamp,
    time_unit="s",
    measurement=None,
    field_keys=None,
    tag_keys=None,
    host=None,
    port=None,
    db=None,
    output_time_unit="s",
):

    host, port, db, measurement = _substitute_defaults(
        host, port, db, measurement, measurement_required=True
    )

    # Validate time_unit according to https://docs.influxdata.com/influxdb/v1.7/query_language/spec/#durations:
    valid_time_units = ("ns", "u", "µ", "ms", "s", "m", "h", "d", "w")
    if time_unit not in valid_time_units:
        raise ValueError(
            f"'time_unit' must be one of {valid_time_units}, not {time_unit}"
        )

    query = f'SELECT * FROM "{measurement}" WHERE time={timestamp}{time_unit}'

    res = _query(query, host=host, port=port, db=db, output_time_unit=output_time_unit)

    if "series" not in res.json()["results"][0]:
        raise IndexError(
            f"No data found in DB {db}, measurement {measurement}, timestamp {timestamp}{time_unit}"
        )
    field_keys = res.json()["results"][0]["series"][0]["columns"]
    field_values = res.json()["results"][0]["series"][0]["values"][0]
    data_dict = {f: v for f, v, in zip(field_keys, field_values)}

    return data_dict


def read_latest(
    measurement,
    field_keys=None,
    tag_keys=None,
    host=None,
    port=None,
    db=None,
    output_time_unit="s",
):
    # TODO: field_keys, tag_keys currently do nothing

    # You would imagine that this works:
    # query = f'SELECT LAST(*) FROM "{measurement}"'
    # But no, the returned time is 0. This was supposed to be fixed, but somehow isnt always
    # So we have to use this stupid workaround:
    query = f'SELECT * FROM "{measurement}" ORDER BY time DESC LIMIT 1'

    res = _query(query, host=host, port=port, db=db, output_time_unit=output_time_unit)

    field_keys = res.json()["results"][0]["series"][0]["columns"]
    field_values = res.json()["results"][0]["series"][0]["values"][0]
    data_dict = {f: v for f, v, in zip(field_keys, field_values)}

    return data_dict


def read_all(
    measurement=None,
    field_keys=None,
    tag_keys=None,
    host=None,
    port=None,
    db=None,
    output_time_unit="s",
):

    host, port, db, measurement = _substitute_defaults(
        host, port, db, measurement, measurement_required=True
    )

    query = f'SELECT * FROM "{measurement}"'

    res = _query(query, host=host, port=port, db=db, output_time_unit=output_time_unit)

    if "series" not in res.json()["results"][0]:
        raise IndexError(f"No data found in DB {db}, measurement {measurement}")
    field_keys = res.json()["results"][0]["series"][0]["columns"]
    field_values = res.json()["results"][0]["series"][0]["values"]
    values_list_of_lists = [
        [v[i] for v in field_values] for i in range(len(field_values[0]))
    ]

    data_dict = {f: v for f, v, in zip(field_keys, values_list_of_lists)}

    return data_dict


def read_range(
    measurement, start_timestamp, end_timestamp, aggregation=None, field_keys=None
):

    # TODO: Option for output_time_unit
    query = f'SELECT * FROM "{measurement}" WHERE time>{start_timestamp} and time>{end_timestamp}'

    res = _query(query, host=host, port=port, db=db)

    field_keys = res.json()["results"][0]["series"][0]["columns"]
    field_values = res.json()["results"][0]["series"][0]["values"][0]
    data_dict = {f: v for f, v, in zip(field_keys, field_values)}

    return data_dict


def read_special_range(
    measurement,
    range_identifier,
    aggregation=None,
    field_keys=None,
    tag_keys=None,
    host=None,
    port=None,
    db=None,
):

    # TODO: Option for output_time_unit
    if range_identifier == "today":
        start_of_today = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_of_today = start_of_today + datetime.timedelta(days=1)

        time_specifier = f"time>'{start_of_today.strftime(INFLUXDB_TIME_FORMAT)}' and time<'{end_of_today.strftime(INFLUXDB_TIME_FORMAT)}'"

    elif range_identifier == "thisweek":
        first_ts_today = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        first_ts_thisweek = first_ts_today - datetime.timedelta(
            days=first_ts_today.weekday()
        )

        time_specifier = f"time >= '{first_ts_thisweek.strftime(INFLUXDB_TIME_FORMAT)}' and time < '{first_ts_thisweek.strftime(INFLUXDB_TIME_FORMAT)}' + 7d"

    elif range_identifier == "last2weeks":
        first_ts_today = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        first_ts_thisweek = first_ts_today - datetime.timedelta(
            days=first_ts_today.weekday()
        )

        time_specifier = f"time >= '{first_ts_thisweek.strftime(INFLUXDB_TIME_FORMAT)}' - 7d and time < '{first_ts_thisweek.strftime(INFLUXDB_TIME_FORMAT)}' + 7d"

    elif range_identifier == "alltime":
        # Find first and last timestamps in the database:
        query = f'SELECT * FROM "{measurement}" ORDER BY time ASC LIMIT 1'
        res = _query(query, host=host, port=port, db=db)
        first_timestamp_s = res.json()["results"][0]["series"][0]["values"][0][0]

        query = f'SELECT * FROM "{measurement}" ORDER BY time DESC LIMIT 1'
        res = _query(query, host=host, port=port, db=db)
        last_timestamp_s = res.json()["results"][0]["series"][0]["values"][0][0]

        time_specifier = f"time >= {first_timestamp_s}s and time < {last_timestamp_s}s"

    # TODO: last_month, yesterday

    else:
        raise ValueError(
            'range_identifier must be one of "today", "thisweek", "last2weeks", or "alltime"'
        )

    if aggregation == None or aggregation.lower() == "none":
        select = "*"
        groupby = ""
    else:
        select = "mean(*)"
        groupby = f"GROUP BY time({aggregation})"

    query = f'SELECT {select} FROM "{measurement}" WHERE {time_specifier} {groupby}'

    res = _query(query, host=host, port=port, db=db)

    if "series" not in res.json()["results"][0]:
        return {}
    field_keys = res.json()["results"][0]["series"][0]["columns"]
    # Remove 'mean_' from the returned field names:
    field_keys = [key[5:] if key.startswith("mean_") else key for key in field_keys]
    field_values = res.json()["results"][0]["series"][0]["values"]
    values_list_of_lists = [
        [v[i] for v in field_values] for i in range(len(field_values[0]))
    ]

    data_dict = {f: v for f, v, in zip(field_keys, values_list_of_lists)}

    return data_dict

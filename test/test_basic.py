import time
import uuid

import pytest

import simpleinflux

import fixtures

test_db_name = "fajsdfhlakjsdhgfkjh"
test_db = fixtures.test_db
test_msmt = "msmt"

simpleinflux.default_db = fixtures.db


def test_ping():
    ping_ok = simpleinflux.ping()
    assert (
        ping_ok
    ), "Ping {simpleinflux.default_host}:{simpleinflux.default_port} failed"


def test_get_version():
    version_string = simpleinflux.get_influx_version()
    assert isinstance(version_string, str)


def test_create_and_drop_database():
    databases = simpleinflux.get_databases()
    assert test_db_name not in databases

    ok = simpleinflux.create_database(test_db_name)
    assert ok

    databases = simpleinflux.get_databases()
    assert test_db_name in databases

    ok = simpleinflux.drop_database(test_db_name)
    assert ok

    databases = simpleinflux.get_databases()
    assert test_db_name not in databases


def test_write(test_db):
    write_ok = simpleinflux.write(test_msmt, time.time(), {"temp": 20.0})
    assert write_ok


def get_measurement(test_db):
    assert simpleinflux.write(test_msmt, time.time(), {"temp": 20.0})
    measurements = simpleinflux.get_measurements()
    assert test_msmt in measurements


def test_read_one(test_db):
    timestamp_list_s = (1_654_505_295, 1_654_505_296, 1_654_505_297)
    test_data_dict = {"temperature": 12}
    for timestamp_s in timestamp_list_s:
        assert simpleinflux.write(test_msmt, timestamp_s, test_data_dict)

    for timestamp_s in timestamp_list_s:
        data = simpleinflux.read_one(test_msmt, timestamp_s)
        assert data["time"] == timestamp_s
        assert data["temperature"] == test_data_dict["temperature"]


def test_read_one_timeunit(test_db):
    timestamp_list_s = (1_654_505_295, 1_654_505_296, 1_654_505_297)
    test_data_dict = {"temperature": 12}

    # Write with nanosecond precision:
    for timestamp_s in timestamp_list_s:
        assert simpleinflux.write(
            test_msmt, timestamp_s * 1e9, test_data_dict, precision="n"
        )

    # Read with millisecond precision and return millisecond precision:
    for timestamp_s in timestamp_list_s:
        timestamp_ms = timestamp_s * 1000
        data = simpleinflux.read_one(
            test_msmt, timestamp_ms, timestamp_unit="ms", output_timestamp_unit="ms"
        )
        assert data["time"] == timestamp_ms
        assert data["temperature"] == test_data_dict["temperature"]


def test_read_all(test_db):
    timestamp_list_s = (1_654_505_295, 1_654_505_296, 1_654_505_297)
    test_data_dict = {"temperature": 12}
    for timestamp_s in timestamp_list_s:
        assert simpleinflux.write(test_msmt, timestamp_s, test_data_dict)
    data = simpleinflux.read_all(test_msmt)
    assert data["time"] == list(timestamp_list_s)
    assert data["temperature"] == [12, 12, 12]


def test_read_field(test_db):
    timestamp_list_s = (1_654_505_295, 1_654_505_296, 1_654_505_297)
    test_data_dict = {"temperature": 12, "pressure": 999}
    for timestamp_s in timestamp_list_s:
        assert simpleinflux.write(test_msmt, timestamp_s, test_data_dict)
    data = simpleinflux.read_all(test_msmt, field_keys=["temperature"])
    assert data["time"] == list(timestamp_list_s)
    assert data["temperature"] == [12, 12, 12]
    assert "pressure" not in data

    data = simpleinflux.read_all(test_msmt, field_keys=["pressure"])
    assert data["time"] == list(timestamp_list_s)
    assert data["pressure"] == [999, 999, 999]
    assert "temperature" not in data


# ============================================================================


# def test_write_explicit_db(test_db):
#     simpleinflux.create_database(db2)
#     write_ok = simpleinflux.write(
#         time.time(), {"temp": 20.0}, measurement=measurement, db=db2
#     )
#     assert write_ok
#     assert read_one


def donttest_run():
    test_db = "testdb"
    create_ok = simpleinflux.create_database(db=test_db)
    assert create_ok

    databases = simpleinflux.get_databases()
    assert test_db in databases

    test_measurement = "test_meas"
    timestamp_list_s = (1_654_505_295, 1_654_505_296, 1_654_505_297)

    for timestamp_s in timestamp_list_s:
        success = simpleinflux.write(
            timestamp_s, {"temperature": 12}, measurement=test_msmt
        )
        assert success

    measurements = simpleinflux.get_measurements()
    assert test_measurement in measurements

    for timestamp_s in timestamp_list_s:
        data = simpleinflux.read_one(test_measurement, timestamp_s)

    data = simpleinflux.read_latest(test_measurement)
    assert data["time"] == max(timestamp_list_s)

    data = simpleinflux.read_special_range(test_measurement, range_identifier="today")
    data = simpleinflux.read_special_range(
        test_measurement, range_identifier="today", aggregation="10m"
    )
    data = simpleinflux.read_special_range(
        measurement, range_identifier="thisweek", aggregation="10m"
    )
    data = simpleinflux.read_special_range(
        measurement, range_identifier="last2weeks", aggregation="10m"
    )
    data = simpleinflux.read_special_range(
        measurement, range_identifier="alltime", aggregation="10s"
    )


if __name__ == "__main__":
    test_ping()

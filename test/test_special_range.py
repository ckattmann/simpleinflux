import time

import pytest

import simpleinflux
import fixtures


msmt = "msmt"
test_db = fixtures.test_db


def test_today(test_db):
    now_s = int(time.time())
    write_ok = simpleinflux.write(msmt, now_s, {"temp": 20.0})
    data = simpleinflux.read_special_range(msmt, "today")
    assert data
    assert data["time"] == [now_s]
    assert data["temp"] == [20]


@pytest.mark.parametrize("aggregation", ("1s", "10s", "1m", "6m", "1h", "12h", "1d"))
def test_today_aggregated(test_db, aggregation):
    now_s = int(time.time())
    write_ok = simpleinflux.write(msmt, now_s, {"temp": 20.0, "pressure": 999})
    data = simpleinflux.read_special_range(msmt, "today", aggregation=aggregation)
    assert data
    assert 20 in data["temp"]
    assert 999 in data["pressure"]


@pytest.mark.parametrize("aggregation", ("1s", "1d"))
def test_today_aggregated_fieldkeys(test_db, aggregation):
    now_s = int(time.time())
    write_ok = simpleinflux.write(msmt, now_s, {"temp": 20.0, "pressure": 999})
    data = simpleinflux.read_special_range(
        msmt, "today", aggregation=aggregation, field_keys=["temp"]
    )
    assert data
    assert 20 in data["temp"]
    assert "pressure" not in data


def test_thisweek(test_db):
    now_s = int(time.time())
    write_ok = simpleinflux.write(msmt, now_s, {"temp": 20.0})
    data = simpleinflux.read_special_range(msmt, "thisweek")
    assert data
    assert data["time"] == [now_s]
    assert data["temp"] == [20]


def test_alltime(test_db):
    now_s = int(time.time())
    write_ok = simpleinflux.write(msmt, now_s, {"temp": 20.0})
    data = simpleinflux.read_special_range(msmt, "alltime")
    assert data
    assert data["time"] == [now_s]
    assert data["temp"] == [20]

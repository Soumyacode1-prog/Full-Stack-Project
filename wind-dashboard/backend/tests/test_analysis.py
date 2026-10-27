import sys
from datetime import date, time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.analysis import analyze


@pytest.fixture(autouse=True)
def use_sample_data(monkeypatch):
    monkeypatch.setenv("ELEXON_LIVE_DATA", "false")


def test_latest_forecast_before_cutoff_is_selected():
    result = analyze(
        date(2026, 1, 11),
        time(10, 0),
    )

    assert result["status"] == "success"
    assert result["series"][0]["forecast"] == 3600
    assert result["series"][0]["actual"] == 3500


def test_summary_values_are_calculated():
    result = analyze(
        date(2026, 1, 11),
        time(10, 0),
    )

    summary = result["summary"]

    assert summary["actualGeneration"] == 11100
    assert summary["forecastGeneration"] == 11400
    assert summary["error"] == -300
    assert summary["absoluteError"] == 300
    assert round(summary["accuracy"], 2) == 97.30


def test_missing_date_returns_error():
    with pytest.raises(ValueError):
        analyze(
            date(2026, 10, 26),
            time(10, 0),
        )

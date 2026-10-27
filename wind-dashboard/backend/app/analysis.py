import json
from datetime import date, datetime, time, timezone
from pathlib import Path
import os
import requests

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ELEXON_BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"

def _load_json(filename: str):
    path = DATA_DIR / filename

    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as error:
        raise ValueError(f"Required data file is missing: {filename}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON file: {filename}") from error

def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _load_elexon(dataset: str, start_date: date, end_date: date):
    response = requests.get(
        f"{ELEXON_BASE_URL}/{dataset}/stream",
        params={
            "from": f"{start_date.isoformat()}T00:00:00Z",
            "to": f"{end_date.isoformat()}T23:59:59Z",
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def analyze(decision_date: date, cutoff: time):
    use_live_data = os.getenv("ELEXON_LIVE_DATA", "true").lower() == "true"
    if use_live_data:
        try:
            actuals = _load_elexon("FUELHH", decision_date, decision_date)
            forecasts = _load_elexon(
                "WINDFOR",
                decision_date,
                decision_date,
            )
        except requests.RequestException as error:
            raise ValueError(f"Unable to fetch Elexon data: {error}") from error
    else:
        actuals = _load_json("actuals.json")
        forecasts = _load_json("forecasts.json")

    cutoff_datetime = datetime.combine(
        decision_date,
        cutoff,
    ).replace(tzinfo=timezone.utc)

    actual_by_start = {
        item["startTime"]: item
        for item in actuals
        if item.get("fuelType", "WIND").upper() == "WIND"
        and _parse_timestamp(item["startTime"]).date() == decision_date
    }

    eligible_forecasts = [
        item
        for item in forecasts
        if _parse_timestamp(item["startTime"]).date() == decision_date
        and _parse_timestamp(item["publishTime"]) <= cutoff_datetime
    ]

    latest_by_start = {}

    for item in eligible_forecasts:
        start_time = item["startTime"]
        current = latest_by_start.get(start_time)

        if current is None or _parse_timestamp(
            item["publishTime"]
        ) > _parse_timestamp(current["publishTime"]):
            latest_by_start[start_time] = item

    series = []

    for start_time, forecast in sorted(latest_by_start.items()):
        actual = actual_by_start.get(start_time)

        if actual is None:
            continue

        forecast_value = float(forecast["generation"])
        actual_value = float(actual["generation"])

        error = actual_value - forecast_value
        absolute_error = abs(error)

        percentage_error = (
            absolute_error / actual_value * 100
            if actual_value
            else None
        )

        series.append(
            {
                "startTime": start_time,
                "publishTime": forecast["publishTime"],
                "forecast": forecast_value,
                "actual": actual_value,
                "error": error,
                "absoluteError": absolute_error,
                "percentageError": percentage_error,
            }
        )

    if not series:
        actual_dates = sorted({item["startTime"][:10] for item in actuals})
        forecast_dates = sorted({item["startTime"][:10] for item in forecasts})
        raise ValueError(
            "No matching forecast and actual data exists for the selected date and cutoff. "
            f"Available actual dates: {actual_dates}; "
            f"available forecast dates: {forecast_dates}."
        )

    total_actual = sum(item["actual"] for item in series)
    total_forecast = sum(item["forecast"] for item in series)
    total_error = total_actual - total_forecast
    total_absolute_error = sum(item["absoluteError"] for item in series)

    percentage_error = (
        total_absolute_error / total_actual * 100
        if total_actual
        else None
    )

    accuracy = (
        max(0, 100 - percentage_error)
        if percentage_error is not None
        else None
    )

    return {
        "decision_date": decision_date.isoformat(),
        "cutoff": cutoff.isoformat(),
        "status": "success",
        "summary": {
            "actualGeneration": total_actual,
            "forecastGeneration": total_forecast,
            "error": total_error,
            "absoluteError": total_absolute_error,
            "percentageError": percentage_error,
            "accuracy": accuracy,
        },
        "series": series,
    }

import argparse
import csv
import math
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
KARACHI = timezone(timedelta(hours=5), "Asia/Karachi")
AQ = "https://api.openaq.org/v3/locations"
WEATHER = "https://api.open-meteo.com/v1/forecast"
KB = {
    "heat": ("Limit strenuous activity during the hottest hours and seek shade.",
             "https://www.who.int/en/news-room/fact-sheets/detail/climate-change-heat-and-health"),
    "pollution": ("People with cardiorespiratory conditions should seek clinician guidance on reducing exposure.",
                  "https://www.who.int/news-room/questions-and-answers/item/air-pollution-personal-interventions-and-risk-communication"),
}
FIELDS = "timestamp date tool request_id status seconds success valid error evidence".split()


def heat_index(celsius, rh):
    t = celsius * 1.8 + 32
    hi = (t + 0.5 * (t + 61 + (t - 68) * 1.2 + rh * .094)) / 2
    if hi >= 80:
        hi = (-42.379 + 2.04901523*t + 10.14333127*rh - .22475541*t*rh
              - .00683783*t*t - .05481717*rh*rh + .00122874*t*t*rh
              + .00085282*t*rh*rh - .00000199*t*t*rh*rh)
        if rh < 13 and 80 <= t <= 112:
            hi -= (13-rh)/4 * math.sqrt((17-abs(t-95))/17)
        if rh > 85 and 80 <= t <= 87:
            hi += (rh-85)/10 * (87-t)/5
    return (hi - 32) / 1.8


def positive(x):
    return isinstance(x, (int, float)) and math.isfinite(x) and x >= 0


def aq_valid(body, sensors, now):
    pollutants = set()
    for row in body.get("results", []):
        name, units = sensors.get(row.get("sensorsId"), ("", ""))
        stamp = row.get("datetime", {}).get("utc")
        if stamp and units in {"µg/m³", "μg/m³", "ug/m3"} and positive(row.get("value")):
            age = now - datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            if timedelta(0) <= age <= timedelta(hours=3):
                pollutants.add(name)
    return {"pm25", "pm10"} <= pollutants


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=15)
    parser.add_argument("--pause", type=float, default=1.0)
    parser.add_argument("--location", type=int, help="Verified Karachi OpenAQ location ID")
    parser.add_argument("--discover", action="store_true", help="List candidate Karachi monitoring locations")
    parser.add_argument("--weather-only", action="store_true", help="Time weather and local tools without OpenAQ")
    args = parser.parse_args()
    key = os.environ.get("OPENAQ_API_KEY")
    headers = {"X-API-Key": key} if key else {}
    evidence_root = ROOT / "evidence" / "responses"
    evidence_root.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    if args.discover:
        if not key:
            parser.error("Set OPENAQ_API_KEY in the local shell first.")
        response = session.get(AQ, headers=headers, timeout=10,
            params={"coordinates":"24.86,67.01","radius":25000,"limit":100})
        if response.status_code == 401:
            parser.exit(2, "OpenAQ rejected the key (HTTP 401). Copy the API key from your OpenAQ Explorer account and try again.\n")
        response.raise_for_status()
        rows = response.json()["results"]
        for item in rows:
            print(item["id"], item.get("name"), item.get("datetimeLast"),
                  [(s["parameter"]["name"], s["parameter"]["units"])
                   for s in item.get("sensors", [])])
        return
    if key and not args.location and not args.weather_only:
        parser.error("Use --discover, then supply a verified location with --location.")
    sensors = {}
    if args.location:
        response = session.get(f"{AQ}/{args.location}", headers=headers, timeout=10)
        response.raise_for_status()
        (evidence_root / f"location-{args.location}-{uuid.uuid4().hex}.json").write_bytes(response.content)
        for sensor in response.json()["results"][0]["sensors"]:
            param = sensor["parameter"]
            sensors[sensor["id"]] = param["name"], param["units"]
    output = ROOT / "tool_latency.csv"
    fresh = not output.exists()
    with output.open("a", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        if fresh:
            writer.writeheader()
        tool_names = ["Open-Meteo", "heat_index", "advisory_lookup"]
        if not args.weather_only:
            tool_names.insert(0, "OpenAQ")
        for _ in range(args.samples):
            for tool in tool_names:
                now = datetime.now(KARACHI)
                row = dict(timestamp=now.isoformat(), date=now.date(), tool=tool,
                           request_id=uuid.uuid4().hex, status="", success=False,
                           valid=False, error="", evidence="")
                start = time.perf_counter()
                try:
                    if tool == "heat_index":
                        value = heat_index(36, 60)
                    elif tool == "advisory_lookup":
                        value = KB["heat"]
                    elif tool == "OpenAQ":
                        url = f"{AQ}/{args.location}/latest" if args.location else AQ
                        params = None if args.location else {"coordinates": "24.86,67.01", "radius": 25000}
                        response = session.get(url, headers=headers, params=params, timeout=10)
                    else:
                        response = session.get(WEATHER, timeout=10, params=dict(
                            latitude=24.86, longitude=67.01, timezone="Asia/Karachi",
                            current="temperature_2m,relative_humidity_2m,wind_speed_10m"))
                    row["seconds"] = time.perf_counter() - start
                    if tool in {"OpenAQ", "Open-Meteo"}:
                        row["status"] = response.status_code
                        path = evidence_root / (row["request_id"] + ".json")
                        path.write_bytes(response.content)
                        row["evidence"] = path.relative_to(ROOT).as_posix()
                        response.raise_for_status()
                        row["success"] = True
                        body = response.json()
                        if tool == "OpenAQ":
                            row["valid"] = aq_valid(body, sensors, now)
                        else:
                            current = body.get("current", {})
                            units = body.get("current_units", {})
                            stamp = datetime.fromisoformat(current["time"]).replace(tzinfo=KARACHI)
                            row["valid"] = (abs(now-stamp) <= timedelta(minutes=30)
                                            and units.get("temperature_2m") == "°C"
                                            and units.get("wind_speed_10m") == "km/h"
                                            and units.get("relative_humidity_2m") == "%"
                                            and math.isfinite(current["temperature_2m"])
                                            and 0 <= current["relative_humidity_2m"] <= 100
                                            and positive(current["wind_speed_10m"]))
                        if not row["valid"]:
                            row["error"] = "Required fresh fields, units or pollutant values missing"
                    else:
                        row.update(status="local", success=True, valid=bool(value),
                                   evidence="collect.py")
                except (requests.RequestException, ValueError, KeyError, TypeError) as error:
                    row.setdefault("seconds", time.perf_counter() - start)
                    row["error"] = type(error).__name__
                    if row["status"] == 401 and tool == "OpenAQ":
                        row["error"] = "OpenAQ credentials absent or rejected (HTTP 401)"
                writer.writerow(row)
                stream.flush()
            time.sleep(args.pause)


if __name__ == "__main__":
    main()

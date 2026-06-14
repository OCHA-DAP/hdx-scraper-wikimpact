#!/usr/bin/python
"""WIKIMPACT scraper pipeline"""

import ast
import logging
import sqlite3

from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.utilities.retriever import Retrieve

logger = logging.getLogger(__name__)

_MAINTAINER = "196196be-6037-4488-8b71-d786adf4c081"
_OWNER_ORG = "ebcfe377-bad0-46d0-b68f-cca8e6b54e33"

_HEADERS = [
    "Event_ID",
    "Event_Names",
    "Main_Event",
    "Hazards",
    "Administrative_Areas_Norm",
    "Administrative_Areas_GID",
    "Administrative_Areas_Type",
    "Start_Date",
    "End_Date",
    "Total_Deaths_Min",
    "Total_Deaths_Max",
    "Total_Deaths_Approx",
    "Total_Affected_Min",
    "Total_Affected_Max",
    "Total_Affected_Approx",
    "Total_Displaced_Min",
    "Total_Displaced_Max",
    "Total_Displaced_Approx",
    "Total_Homeless_Min",
    "Total_Homeless_Max",
    "Total_Homeless_Approx",
    "Total_Injuries_Min",
    "Total_Injuries_Max",
    "Total_Injuries_Approx",
    "Total_Buildings_Damaged_Min",
    "Total_Buildings_Damaged_Max",
    "Total_Buildings_Damaged_Approx",
    "Total_Damage_Min",
    "Total_Damage_Max",
    "Total_Damage_Approx",
    "Total_Damage_Unit",
    "Total_Damage_Inflation_Adjusted",
    "Total_Damage_Inflation_Adjusted_Year",
    "Total_Insured_Damage_Min",
    "Total_Insured_Damage_Max",
    "Total_Insured_Damage_Approx",
    "Total_Insured_Damage_Unit",
    "Total_Insured_Damage_Inflation_Adjusted",
    "Total_Insured_Damage_Inflation_Adjusted_Year",
]


def _parse_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return ast.literal_eval(value)


def _join_list(value) -> str:
    return "|".join(str(item) for item in _parse_list(value))


def _join_gid_list(value) -> str:
    """Flatten list of lists: [['MEX']] -> 'MEX', [['USA'], ['CAN']] -> 'USA|CAN'"""
    parts = []
    for inner in _parse_list(value):
        if isinstance(inner, list):
            parts.append(",".join(str(g) for g in inner))
        else:
            parts.append(str(inner))
    return "|".join(parts)


def _format_date(day, month, year) -> str:
    if not day or not month or not year:
        return ""
    return f"{int(day):02d}/{int(month):02d}/{int(year):04d}"


def _iso_date(day, month, year) -> str | None:
    if not day or not month or not year:
        return None
    return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"


def _val(v) -> str:
    return "" if v is None else v


def _row_from_db(db_row) -> dict:
    return {
        "Event_ID": db_row["Event_ID"],
        "Event_Names": _join_list(db_row["Event_Names"]),
        "Main_Event": _val(db_row["Main_Event"]),
        "Hazards": _join_list(db_row["Hazards"]),
        "Administrative_Areas_Norm": _join_list(db_row["Administrative_Areas_Norm"]),
        "Administrative_Areas_GID": _join_gid_list(db_row["Administrative_Areas_GID"]),
        "Administrative_Areas_Type": _join_list(db_row["Administrative_Areas_Type"]),
        "Start_Date": _format_date(
            db_row["Start_Date_Day"],
            db_row["Start_Date_Month"],
            db_row["Start_Date_Year"],
        ),
        "End_Date": _format_date(
            db_row["End_Date_Day"],
            db_row["End_Date_Month"],
            db_row["End_Date_Year"],
        ),
        "Total_Deaths_Min": _val(db_row["Total_Deaths_Min"]),
        "Total_Deaths_Max": _val(db_row["Total_Deaths_Max"]),
        "Total_Deaths_Approx": _val(db_row["Total_Deaths_Approx"]),
        "Total_Affected_Min": _val(db_row["Total_Affected_Min"]),
        "Total_Affected_Max": _val(db_row["Total_Affected_Max"]),
        "Total_Affected_Approx": _val(db_row["Total_Affected_Approx"]),
        "Total_Displaced_Min": _val(db_row["Total_Displaced_Min"]),
        "Total_Displaced_Max": _val(db_row["Total_Displaced_Max"]),
        "Total_Displaced_Approx": _val(db_row["Total_Displaced_Approx"]),
        "Total_Homeless_Min": _val(db_row["Total_Homeless_Min"]),
        "Total_Homeless_Max": _val(db_row["Total_Homeless_Max"]),
        "Total_Homeless_Approx": _val(db_row["Total_Homeless_Approx"]),
        "Total_Injuries_Min": _val(db_row["Total_Injuries_Min"]),
        "Total_Injuries_Max": _val(db_row["Total_Injuries_Max"]),
        "Total_Injuries_Approx": _val(db_row["Total_Injuries_Approx"]),
        "Total_Buildings_Damaged_Min": _val(db_row["Total_Buildings_Damaged_Min"]),
        "Total_Buildings_Damaged_Max": _val(db_row["Total_Buildings_Damaged_Max"]),
        "Total_Buildings_Damaged_Approx": _val(db_row["Total_Buildings_Damaged_Approx"]),
        "Total_Damage_Min": _val(db_row["Total_Damage_Min"]),
        "Total_Damage_Max": _val(db_row["Total_Damage_Max"]),
        "Total_Damage_Approx": _val(db_row["Total_Damage_Approx"]),
        "Total_Damage_Unit": _val(db_row["Total_Damage_Unit"]),
        "Total_Damage_Inflation_Adjusted": _val(db_row["Total_Damage_Inflation_Adjusted"]),
        "Total_Damage_Inflation_Adjusted_Year": _val(
            db_row["Total_Damage_Inflation_Adjusted_Year"]
        ),
        "Total_Insured_Damage_Min": _val(db_row["Total_Insured_Damage_Min"]),
        "Total_Insured_Damage_Max": _val(db_row["Total_Insured_Damage_Max"]),
        "Total_Insured_Damage_Approx": _val(db_row["Total_Insured_Damage_Approx"]),
        "Total_Insured_Damage_Unit": _val(db_row["Total_Insured_Damage_Unit"]),
        "Total_Insured_Damage_Inflation_Adjusted": _val(
            db_row["Total_Insured_Damage_Inflation_Adjusted"]
        ),
        "Total_Insured_Damage_Inflation_Adjusted_Year": _val(
            db_row["Total_Insured_Damage_Inflation_Adjusted_Year"]
        ),
    }


class Pipeline:
    def __init__(
        self,
        configuration: Configuration,
        retriever: Retrieve,
        today,
        folder: str,
    ):
        self._configuration = configuration
        self._retriever = retriever
        self._today = today
        self._folder = folder

    def generate_dataset(self) -> Dataset | None:
        url = self._configuration["db_url"]
        db_path = self._retriever.download_file(url, "impactdb.db")

        con = sqlite3.connect(db_path)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM Total_Summary ORDER BY Event_ID")
        db_rows = cur.fetchall()
        con.close()

        if not db_rows:
            logger.warning("No rows found in Total_Summary table")
            return None

        rows = []
        start_iso = None
        end_iso = None

        for db_row in db_rows:
            row_start = _iso_date(
                db_row["Start_Date_Day"],
                db_row["Start_Date_Month"],
                db_row["Start_Date_Year"],
            )
            row_end = _iso_date(
                db_row["End_Date_Day"],
                db_row["End_Date_Month"],
                db_row["End_Date_Year"],
            )
            if row_start:
                if start_iso is None or row_start < start_iso:
                    start_iso = row_start
            if row_end:
                if end_iso is None or row_end > end_iso:
                    end_iso = row_end

            rows.append(_row_from_db(db_row))

        dataset = Dataset(
            {
                "name": "wikimpact-impact-database",
                "title": "WIKIMPACT Impact Database",
            }
        )
        dataset.add_other_location("world")
        dataset.set_maintainer(_MAINTAINER)
        dataset.set_organization(_OWNER_ORG)
        dataset.set_expected_update_frequency("As needed")
        dataset.set_subnational(False)
        if start_iso and end_iso:
            dataset.set_time_period(start_iso, end_iso)
        elif start_iso:
            dataset.set_time_period(start_iso)
        dataset.add_tags(["hazards and risk", "natural disasters"])

        filename = "wikimpact_impact_events.csv"
        resourcedata = {
            "name": filename,
            "description": "WIKIMPACT global disaster impact events",
        }
        dataset.generate_resource(
            self._folder,
            filename,
            rows,
            resourcedata,
            headers=_HEADERS,
            no_empty=False,
        )
        return dataset

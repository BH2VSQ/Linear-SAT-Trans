#!/usr/bin/env python3
"""
Convert WSJT-X FT4 logs into satellite FT4 ADIF logs.

Supported input:
  - WSJT-X wsjtx_log.adi / other ADIF files
  - WSJT-X wsjtx.log CSV files

Usage:
  python wsjtx_to_satlog.py --sat JO97 --input wsjtx_log.adi
  python wsjtx_to_satlog.py --sat AO73 --input wsjtx.log --output C:/logs/ao73-ft4.adi

When --output is omitted:
  - .adi/.adif input -> <original>-output.adi
  - .log/.csv input -> <original>-output.adi

The converter adds/overwrites:
  PROP_MODE = SAT
  SAT_NAME  = selected satellite
  SAT_MODE  = satellite transponder mode
  MODE      = MFSK
  SUBMODE   = FT4

Existing ADIF fields are preserved.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List

SATELLITES = {
    # FREQ: uplink frequency (MHz)
    # RX_FREQ: downlink frequency (MHz)
    # Fill in the satellite transponder frequencies here.
    "JO97": {"name": "JO-97", "sat_mode": "U/V", "freq": "435.110", "rx_freq": "145.865"},
    "AO73": {"name": "AO-73", "sat_mode": "U/V", "freq": "435.140", "rx_freq": "145.960"},
    "RS44": {"name": "RS-44", "sat_mode": "V/U", "freq": "145.965", "rx_freq": "435.640"},
}

ADIF_TAG_RE = re.compile(
    r"<(?P<tag>[A-Za-z0-9_]+)(?::(?P<len>\d+))?(?::[^>]*)?>",
    re.IGNORECASE,
)


def normalize_sat(value: str) -> str:
    key = re.sub(r"[^A-Za-z0-9]", "", value).upper()
    if key not in SATELLITES:
        choices = ", ".join(SATELLITES)
        raise ValueError(f"Unsupported satellite '{value}'. Choose one of: {choices}")
    return key


def parse_adif(path: Path) -> List[Dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    records: List[Dict[str, str]] = []
    record: Dict[str, str] = {}

    matches = list(ADIF_TAG_RE.finditer(text))
    for match in matches:
        tag = match.group("tag").upper()
        length_text = match.group("len")
        if tag == "EOR":
            if record:
                records.append(record)
                record = {}
            continue

        if length_text is None:
            # Tags such as <EOH> have no data length. Ignore them here.
            continue

        length = int(length_text)
        start = match.end()
        value = text[start:start + length]
        record[tag] = value

    if record:
        records.append(record)

    return records


def parse_wsjtx_csv(path: Path) -> List[Dict[str, str]]:
    records: List[Dict[str, str]] = []

    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        for line_no, row in enumerate(reader, start=1):
            if not row or all(not field.strip() for field in row):
                continue

            # WSJT-X wsjtx.log is normally:
            # date_on,time_on,date_off,time_off,call,grid,freq,mode,
            # srpt,rrpt,power,comment,name
            if len(row) < 10:
                print(
                    f"Warning: skipping line {line_no}: expected at least 10 CSV fields, "
                    f"got {len(row)}.",
                    file=sys.stderr,
                )
                continue

            date_on, time_on = row[0].strip(), row[1].strip()
            date_off, time_off = row[2].strip(), row[3].strip()

            rec: Dict[str, str] = {}

            if date_on:
                rec["QSO_DATE"] = date_on.replace("-", "").replace("/", "")
            if time_on:
                rec["TIME_ON"] = re.sub(r"[^0-9]", "", time_on)
            if date_off:
                rec["QSO_DATE_OFF"] = date_off.replace("-", "").replace("/", "")
            if time_off:
                rec["TIME_OFF"] = re.sub(r"[^0-9]", "", time_off)

            mapping = {
                4: "CALL",
                5: "GRIDSQUARE",
                6: "FREQ",
                7: "MODE",
                8: "RST_SENT",
                9: "RST_RCVD",
            }
            for index, tag in mapping.items():
                if index < len(row) and row[index].strip():
                    rec[tag] = row[index].strip()

            # WSJT-X uses a power string such as "7W" in this column.
            if len(row) > 10 and row[10].strip():
                power = row[10].strip()
                match = re.fullmatch(r"\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*[Ww]\s*", power)
                if match:
                    rec["TX_PWR"] = match.group(1)
                else:
                    rec["COMMENT"] = f"WSJT-X power: {power}"

            if len(row) > 11 and row[11].strip():
                existing = rec.get("COMMENT")
                rec["COMMENT"] = (
                    f"{existing}; {row[11].strip()}" if existing else row[11].strip()
                )

            if len(row) > 12 and row[12].strip():
                rec["NAME"] = row[12].strip()

            records.append(rec)

    return records


def detect_input_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".adi", ".adif"}:
        return "adif"
    if suffix in {".log", ".csv", ".txt"}:
        return "csv"

    # Content-based fallback.
    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:4096]
    if "<EOR>" in sample.upper() or "<QSO_DATE:" in sample.upper():
        return "adif"
    return "csv"


def load_records(path: Path) -> List[Dict[str, str]]:
    fmt = detect_input_format(path)
    if fmt == "adif":
        return parse_adif(path)
    return parse_wsjtx_csv(path)


def clean_adif_value(value: str) -> str:
    # ADIF stores literal values; normalize only line endings.
    return str(value).replace("\r\n", " ").replace("\n", " ").replace("\r", " ")


def adif_field(tag: str, value: str) -> str:
    value = clean_adif_value(value)
    return f"<{tag}:{len(value)}>{value}"


def write_adif(path: Path, records: Iterable[Dict[str, str]], satellite: str) -> int:
    sat = SATELLITES[satellite]
    records = list(records)

    header = [
        "Generated by wsjtx_to_satlog.py",
        f"Satellite: {sat['name']}",
        f"Satellite mode: {sat['sat_mode']}",
    ]

    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("ADIF Export\n")
        fh.write("<ADIF_VER:5>3.1.4")
        fh.write("<PROGRAMID:16>WSJT-X SAT LOG")
        fh.write(f"<COMMENT:10>{header[0]}")
        fh.write("<EOH>\n\n")

        for record in records:
            out = dict(record)

            # Satellite fields requested for a linear-transponder FT4 log.
            out["PROP_MODE"] = "SAT"
            out["SAT_NAME"] = sat["name"]
            out["SAT_MODE"] = sat["sat_mode"]

            # Assign satellite transponder frequencies.
            if sat.get("freq"):
                out["FREQ"] = sat["freq"]
            if sat.get("rx_freq"):
                out["RX_FREQ"] = sat["rx_freq"]

            out["MODE"] = "MFSK"
            out["SUBMODE"] = "FT4"

            # Remove fields that can conflict with the intended satellite mode.
            # Keep the actual frequency from the source rather than inventing
            # a Doppler-corrected uplink/downlink frequency.
            ordered_tags = [
                "QSO_DATE",
                "TIME_ON",
                "QSO_DATE_OFF",
                "TIME_OFF",
                "CALL",
                "GRIDSQUARE",
                "FREQ",
                "BAND",
                "RX_FREQ",
                "RX_BAND",
                "MODE",
                "SUBMODE",
                "RST_SENT",
                "RST_RCVD",
                "TX_PWR",
                "NAME",
                "COMMENT",
                "PROP_MODE",
                "SAT_NAME",
                "SAT_MODE",
            ]

            emitted = set()
            for tag in ordered_tags:
                if tag in out:
                    fh.write(adif_field(tag, out[tag]))
                    emitted.add(tag)

            # Preserve any less-common fields that were in the source ADIF.
            for tag, value in out.items():
                if tag in emitted:
                    continue
                if tag in {"EOR", "EOH"}:
                    continue
                fh.write(adif_field(tag, value))

            fh.write("<EOR>\n")

    return len(records)


def default_output_path(input_path: Path) -> Path:
    if input_path.suffix.lower() in {".adi", ".adif"}:
        return input_path.with_name(f"{input_path.stem}-output{input_path.suffix}")
    return input_path.with_name(f"{input_path.stem}-output.adi")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert WSJT-X FT4 logs to satellite FT4 ADIF logs."
    )
    parser.add_argument(
        "--sat",
        required=True,
        choices=["JO97", "AO73", "RS44", "JO-97", "AO-73", "RS-44"],
        help="Satellite: JO97, AO73 or RS44.",
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Input WSJT-X log (.adi/.adif/.log/.csv/.txt).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output ADIF file. Defaults to <input>-output.adi/.adif.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        satellite = normalize_sat(args.sat)
        input_path = args.input.expanduser().resolve()

        if not input_path.is_file():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        output_path = (
            args.output.expanduser().resolve()
            if args.output
            else default_output_path(input_path).resolve()
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        records = load_records(input_path)
        if not records:
            raise ValueError("No QSO records were found in the input file.")

        count = write_adif(output_path, records, satellite)

        print(f"Satellite : {SATELLITES[satellite]['name']}")
        print(f"Sat mode  : {SATELLITES[satellite]['sat_mode']}")
        print(f"Input     : {input_path}")
        print(f"Output    : {output_path}")
        print(f"QSOs      : {count}")

        return 0

    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

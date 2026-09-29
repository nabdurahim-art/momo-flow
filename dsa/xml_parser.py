"""
xml_parser.py
--------------
Parses the MoMo SMS XML export into a list of JSON-serializable
dictionaries (one per transaction).

Usage:
    from xml_parser import parse_sms_xml
    records = parse_sms_xml("../data/modified_sms_v2.xml")
"""

import xml.etree.ElementTree as ET
import json
import os

# Fields on <sms> elements we expect to read. Anything missing
# defaults to None / "" so a real modified_sms_v2.xml with slightly
# different attributes won't crash the parser.
FIELDS = [
    "id", "momo_ref_id", "type", "amount", "fee", "new_balance",
    "sender", "sender_phone", "receiver", "receiver_phone",
    "timestamp", "raw_sms_date", "status", "body",
]

NUMERIC_FIELDS = {"id", "amount", "fee", "new_balance", "raw_sms_date"}


def _cast(field, value):
    if value is None:
        return None
    if field in NUMERIC_FIELDS:
        try:
            if field in ("amount", "fee", "new_balance"):
                return float(value)
            return int(value)
        except ValueError:
            return value
    return value


def parse_sms_xml(xml_path):
    """Parse the SMS XML file into a list of transaction dicts."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    records = []
    for sms in root.findall("sms"):
        record = {}
        for field in FIELDS:
            raw_value = sms.get(field)
            record[field] = _cast(field, raw_value)
        records.append(record)

    return records


def build_index(records):
    """Build an id -> record dict for O(1) lookups (used by the API and DSA comparison).

    Records whose id is missing or not an integer cannot be addressed, so they
    are skipped instead of producing an unusable None key (a real-world XML
    export with a stray row would otherwise crash the API at startup).
    """
    return {record["id"]: record for record in records if isinstance(record.get("id"), int)}


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(here, "..", "data", "modified_sms_v2.xml")

    records = parse_sms_xml(xml_path)
    index = build_index(records)

    print(f"Parsed {len(records)} transactions from {xml_path}\n")
    print("Sample record (JSON):")
    print(json.dumps(records[0], indent=2))

    # Also drop a plain JSON file for anything else that needs it
    out_path = os.path.join(here, "..", "data", "transactions.json")
    with open(out_path, "w") as f:
        json.dump(records, f, indent=2)
    print(f"\nWrote parsed JSON to {out_path}")

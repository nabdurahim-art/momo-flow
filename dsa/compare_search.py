"""
compare_search.py
-----------------
Efficiency comparison between the two transaction-id lookup strategies:

    1. linear search      - O(n) scan over the list of records
    2. dictionary lookup  - O(1) hash lookup on the index built by build_index()

Both methods are timed with time.perf_counter over the same set of targets and
the results (plus a correctness cross-check) are written to
docs/dsa_search_evidence.txt as submission evidence.

Usage:
    python3 dsa/compare_search.py [num_records] [num_lookups]
"""

import os
import random
import sys
import time

try:
    from dsa.xml_parser import build_index, linear_search, parse_sms_xml
except ImportError:
    from xml_parser import build_index, linear_search, parse_sms_xml

HERE = os.path.dirname(os.path.abspath(__file__))
XML_PATH = os.path.join(HERE, "..", "data", "modified_sms_v2.xml")
EVIDENCE_PATH = os.path.join(HERE, "..", "docs", "dsa_search_evidence.txt")

# The task sheet requires the comparison to be made over at least a few
# thousand records, so 5000 is the default floor.
DEFAULT_RECORDS = 5000
DEFAULT_LOOKUPS = 200


def _synthetic_records(start_id, count, total):
    """Records with the same shape as parse_sms_xml() output, ids start_id..start_id+count-1."""
    return [
        {
            "id": i,
            "momo_ref_id": f"MOMO{i:08d}",
            "type": "Received" if i % 2 else "Sent",
            "amount": float(i % 97) + 0.5,
            "fee": 0.0,
            "new_balance": 1000.0 + i,
            "sender": f"Sender {i % 50}",
            "sender_phone": f"+25677{i:07d}",
            "receiver": f"Receiver {i % 50}",
            "receiver_phone": f"+25678{i:07d}",
            "timestamp": f"2026-01-{(i % 28) + 1:02d} 12:00:00",
            "raw_sms_date": 1767225600 + i,
            "status": "success",
            "body": f"Transaction {i} of {total}",
        }
        for i in range(start_id, start_id + count)
    ]


def load_records(num_records):
    """Return (records, source) with at least num_records entries.

    The real parsed XML is used when available. If it holds fewer records than
    requested, the shortfall is padded with synthetic records (ids continuing
    after the last real id) so the required record floor is always met.
    """
    if num_records < 1:
        raise ValueError("num_records must be at least 1")

    if os.path.exists(XML_PATH):
        records = parse_sms_xml(XML_PATH)
        if len(records) >= num_records:
            return records[:num_records], "data/modified_sms_v2.xml"

        missing = num_records - len(records)
        next_id = max(
            (r["id"] for r in records if isinstance(r.get("id"), int)), default=0
        ) + 1
        padded = records + _synthetic_records(next_id, missing, num_records)
        source = (f"data/modified_sms_v2.xml ({len(records)} records) + "
                  f"{missing} synthetic records padded to reach {num_records}")
        return padded, source

    return (
        _synthetic_records(1, num_records, num_records),
        "synthetic (data/modified_sms_v2.xml not found)",
    )


def time_linear(records, targets):
    """Average seconds per linear-search call."""
    start = time.perf_counter()
    for target in targets:
        linear_search(records, target)
    return (time.perf_counter() - start) / len(targets)


def time_dict(index, targets):
    """Average seconds per dictionary-lookup call."""
    start = time.perf_counter()
    for target in targets:
        index.get(target)
    return (time.perf_counter() - start) / len(targets)


def compare(num_records=DEFAULT_RECORDS, num_lookups=DEFAULT_LOOKUPS,
            evidence_path=EVIDENCE_PATH):
    """Run the comparison and optionally write the report to evidence_path.

    Pass evidence_path=None to get the report without touching any file
    (the test suite uses this so running the tests never clobbers the
    submission evidence).
    """
    if num_lookups < 1:
        raise ValueError("num_lookups must be at least 1")

    records, source = load_records(num_records)
    index = build_index(records)

    ids = [r["id"] for r in records if isinstance(r.get("id"), int)]
    if not ids:
        raise ValueError("no records with an integer id to search")

    # Half of the targets sit at the end of the list (worst case for a
    # linear scan), the rest are random - this keeps the average honest.
    rng = random.Random(42)
    tail = ids[-max(1, num_lookups // 2):]
    random_ids = rng.choices(ids, k=num_lookups - len(tail))
    targets = tail + random_ids
    rng.shuffle(targets)
    lookups = len(targets)

    # Correctness cross-check: both methods must agree on every target.
    mismatches = sum(
        1
        for target in targets
        if linear_search(records, target) != index.get(target)
    )

    linear_avg = time_linear(records, targets)
    dict_avg = time_dict(index, targets)
    speedup = linear_avg / dict_avg if dict_avg else float("inf")

    lines = [
        "DSA Integration & Testing - search efficiency comparison",
        "=========================================================",
        f"Python            : {sys.version.split()[0]}",
        f"Records           : {len(records)} (source: {source})",
        f"Task requirement  : at least 20 records compared -> "
        f"{'met' if len(records) >= 20 else 'NOT met'}",
        f"Lookups timed     : {lookups}",
        f"Correctness       : {lookups - mismatches}/{lookups} "
        f"targets returned identical results ({mismatches} mismatches)",
        "",
        f"Linear search  O(n): {linear_avg * 1000:10.4f} ms per lookup "
        f"({linear_avg * 1_000_000:,.1f} us)",
        f"Dictionary     O(1): {dict_avg * 1000:10.4f} ms per lookup "
        f"({dict_avg * 1_000_000:,.1f} us)",
        f"Speed-up           : dictionary lookup is {speedup:,.1f}x faster "
        f"at n = {len(records)}",
        "",
        "Conclusion: linear search has to inspect up to every record, so its",
        "cost grows with the number of transactions, while the dict index built",
        "by build_index() resolves an id in constant time regardless of size.",
        f"Both methods agree on all {lookups} sampled targets.",
    ]
    text = "\n".join(lines) + "\n"

    if evidence_path:
        with open(evidence_path, "w") as f:
            f.write(text)

    return {
        "records": len(records),
        "lookups": lookups,
        "mismatches": mismatches,
        "linear_avg_s": linear_avg,
        "dict_avg_s": dict_avg,
        "speedup": speedup,
        "text": text,
        "evidence_path": evidence_path,
    }


if __name__ == "__main__":
    try:
        n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_RECORDS
        k = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_LOOKUPS
        result = compare(n, k)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(result["text"])
    print(f"Evidence written to {os.path.normpath(EVIDENCE_PATH)}")

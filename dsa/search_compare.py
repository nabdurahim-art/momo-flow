"""
search_compare.py
------------------
Compares Linear Search (scanning a list) against Dictionary Lookup
(hash map by id) for finding a transaction by id.

Run:
    python3 search_compare.py
"""

import os
import time
import statistics

from xml_parser import parse_sms_xml, build_index


def linear_search(records, target_id):
    """O(n): scan the list until the id matches."""
    for record in records:
        if record["id"] == target_id:
            return record
    return None


def dict_lookup(index, target_id):
    """O(1) average: direct hash map access."""
    return index.get(target_id)


def time_it(func, *args, repeats=2000):
    """Run func repeatedly and return the average time in microseconds."""
    start = time.perf_counter()
    for _ in range(repeats):
        func(*args)
    elapsed = time.perf_counter() - start
    return (elapsed / repeats) * 1_000_000  # microseconds per call


def run_comparison(records, index):
    ids_to_test = [records[0]["id"], records[len(records) // 2]["id"], records[-1]["id"]]

    print(f"{'Target position':<20}{'Linear search (µs)':<22}{'Dict lookup (µs)':<20}")
    print("-" * 62)

    linear_times, dict_times = [], []
    labels = ["first", "middle", "last"]

    for label, target_id in zip(labels, ids_to_test):
        lt = time_it(linear_search, records, target_id)
        dt = time_it(dict_lookup, index, target_id)
        linear_times.append(lt)
        dict_times.append(dt)
        print(f"{label:<20}{lt:<22.4f}{dt:<20.4f}")

    print("-" * 62)
    print(f"{'Average':<20}{statistics.mean(linear_times):<22.4f}{statistics.mean(dict_times):<20.4f}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(here, "..", "data", "modified_sms_v2.xml")

    records = parse_sms_xml(xml_path)
    index = build_index(records)

    print(f"Comparing search methods over {len(records)} transactions\n")
    run_comparison(records, index)

    print(
        "\nReflection:\n"
        "- Linear search is O(n): worst case it inspects every record, so lookup time\n"
        "  grows with dataset size. It never needs extra memory, though.\n"
        "- Dictionary lookup is O(1) on average because Python dicts hash the key\n"
        "  directly to a bucket, so lookup time stays roughly constant regardless\n"
        "  of how many transactions exist. The trade-off is the memory used to\n"
        "  store the hash table and keeping it in sync on every insert/update/delete.\n"
        "- At 22 records the gap is tiny in wall-clock terms, but it would become\n"
        "  significant at production scale (thousands/millions of transactions).\n"
        "- A further improvement: a B-tree / sorted index (or a real database index,\n"
        "  e.g. the MySQL indexes already defined on transaction_id, transaction_date,\n"
        "  and user_id in the confirmed schema) gives O(log n) lookups plus efficient\n"
        "  range queries (e.g. 'all transactions in May'), which a plain dict can't do."
    )

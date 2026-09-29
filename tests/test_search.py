"""Tests for the DSA search implementations (linear search vs dictionary lookup).

Run from the repo root:
    python3 -m unittest discover -s tests -v
or regenerate the submission evidence with:
    bash scripts/run_dsa_tests.sh
"""

import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest import mock

from dsa import compare_search
from dsa.compare_search import compare
from dsa.xml_parser import build_index, linear_search

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEARCH_EVIDENCE = os.path.join(REPO_ROOT, "docs", "dsa_search_evidence.txt")

RECORDS = [
    {"id": 1, "amount": 10.0, "body": "first"},
    {"id": 2, "amount": 20.0, "body": "second"},
    {"id": 3, "amount": 30.0, "body": "third"},
    {"id": 7, "amount": 70.0, "body": "seventh"},
    {"id": 9, "amount": 90.0, "body": "ninth"},
]


class LinearSearchTest(unittest.TestCase):
    def test_finds_existing_ids(self):
        for record in RECORDS:
            self.assertEqual(linear_search(RECORDS, record["id"]), record)

    def test_returns_none_for_missing_id(self):
        self.assertIsNone(linear_search(RECORDS, 4))

    def test_returns_none_for_non_integer_target(self):
        self.assertIsNone(linear_search(RECORDS, None))
        self.assertIsNone(linear_search(RECORDS, "3"))
        self.assertIsNone(linear_search(RECORDS, 4.5))

    def test_float_target_matches_int_id_like_the_dict_does(self):
        # index.get(3.0) finds id 3 (equal keys, equal hash), so the linear
        # scan has to return the same record instead of rejecting the target.
        index = build_index(RECORDS)
        self.assertEqual(linear_search(RECORDS, 3.0), index.get(3.0))
        self.assertEqual(linear_search(RECORDS, 3.0), RECORDS[2])

    def test_records_with_string_ids_are_not_addressable(self):
        # build_index() skips non-integer ids, so linear search must too.
        odd = [{"id": "abc"}, {"id": 5}]
        self.assertIsNone(linear_search(odd, "abc"))
        self.assertEqual(linear_search(odd, 5), odd[1])

    def test_empty_list(self):
        self.assertIsNone(linear_search([], 1))

    def test_scales_linearly_over_records(self):
        # Scanning 5000 records must visit every element, so the result is
        # correct regardless of where the target sits.
        big = [{"id": i} for i in range(1, 5001)]
        self.assertEqual(linear_search(big, 1), {"id": 1})
        self.assertEqual(linear_search(big, 5000), {"id": 5000})
        self.assertIsNone(linear_search(big, 5001))


class DictionaryLookupTest(unittest.TestCase):
    def test_index_hits(self):
        index = build_index(RECORDS)
        self.assertEqual(index[3], RECORDS[2])
        self.assertIsNone(index.get(4))

    def test_skips_records_with_invalid_ids(self):
        index = build_index([{"id": None}, {"id": "abc"}, {"id": 5}])
        self.assertEqual(list(index), [5])

    def test_empty_records(self):
        self.assertEqual(build_index([]), {})

    def test_duplicate_id_keeps_first_occurrence(self):
        # build_index and linear_search must return the same record, so a
        # duplicated id has to resolve to the first occurrence in both.
        dupes = [{"id": 1, "body": "original"}, {"id": 1, "body": "duplicate"}]
        self.assertEqual(build_index(dupes)[1], dupes[0])
        self.assertEqual(linear_search(dupes, 1), dupes[0])


class AgreementAndEfficiencyTest(unittest.TestCase):
    def test_both_methods_agree_on_every_id(self):
        index = build_index(RECORDS)
        for record in RECORDS:
            self.assertEqual(linear_search(RECORDS, record["id"]), index.get(record["id"]))
        self.assertEqual(linear_search(RECORDS, 999), index.get(999))

    def test_both_methods_agree_on_duplicate_ids(self):
        dupes = [{"id": i % 3} for i in range(10)]
        index = build_index(dupes)
        for target in range(5):
            self.assertEqual(linear_search(dupes, target), index.get(target))

    def test_dictionary_lookup_is_faster_at_scale(self):
        # 5000 records: linear search is O(n), dict is O(1) - on identical
        # targets the dict must win by a wide margin.
        records = [{"id": i} for i in range(1, 5001)]
        index = build_index(records)
        targets = [1, 2500, 5000, 4999, 1234] * 20

        start = time.perf_counter()
        for target in targets:
            linear_search(records, target)
        linear_total = time.perf_counter() - start

        start = time.perf_counter()
        for target in targets:
            index.get(target)
        dict_total = time.perf_counter() - start

        self.assertLess(dict_total, linear_total)
        speedup = linear_total / dict_total if dict_total else float("inf")
        self.assertGreater(speedup, 2, f"expected dict to be clearly faster, got {speedup:.1f}x")


class ComparisonTest(unittest.TestCase):
    def setUp(self):
        # compare() writes to evidence_path by default; keep test runs from
        # overwriting the committed submission evidence in docs/.
        fd, self.temp_evidence = tempfile.mkstemp(prefix="dsa_search_", suffix=".txt")
        os.close(fd)

    def tearDown(self):
        if os.path.exists(self.temp_evidence):
            os.unlink(self.temp_evidence)

    def test_comparison_runs_over_5000_records(self):
        result = compare(num_records=5000, num_lookups=100,
                         evidence_path=self.temp_evidence)

        self.assertGreaterEqual(result["records"], 5000)
        self.assertEqual(result["lookups"], 100)
        self.assertEqual(result["mismatches"], 0)
        self.assertGreater(result["linear_avg_s"], result["dict_avg_s"])
        self.assertGreater(result["speedup"], 2)

    def test_evidence_file_is_written(self):
        result = compare(num_records=5000, num_lookups=50,
                         evidence_path=self.temp_evidence)

        with open(self.temp_evidence) as f:
            written = f.read()

        self.assertEqual(written, result["text"])
        for marker in ("DSA Integration & Testing", "Linear search", "Dictionary",
                       "Speed-up", "mismatches", "Records"):
            self.assertIn(marker, written)

    def test_evidence_path_none_writes_nothing(self):
        existed = os.path.exists(SEARCH_EVIDENCE)
        before = os.path.getmtime(SEARCH_EVIDENCE) if existed else None

        compare(num_records=100, num_lookups=5, evidence_path=None)

        if existed:
            self.assertEqual(os.path.getmtime(SEARCH_EVIDENCE), before)
        else:
            self.assertFalse(os.path.exists(SEARCH_EVIDENCE))

    def test_single_lookup_edge_case(self):
        result = compare(num_records=100, num_lookups=1, evidence_path=None)
        self.assertEqual(result["lookups"], 1)
        self.assertEqual(result["mismatches"], 0)

    def test_rejects_invalid_arguments(self):
        with self.assertRaises(ValueError):
            compare(num_records=0, evidence_path=None)
        with self.assertRaises(ValueError):
            compare(num_records=100, num_lookups=0, evidence_path=None)


class LoadRecordsTest(unittest.TestCase):
    def test_synthetic_when_xml_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = os.path.join(tmp, "does_not_exist.xml")
            with mock.patch.object(compare_search, "XML_PATH", missing):
                records, source = compare_search.load_records(50)

        self.assertEqual(len(records), 50)
        self.assertIn("synthetic", source)

    def test_pads_short_real_xml_up_to_the_floor(self):
        xml = (
            "<messages>"
            '<sms id="1" amount="10" fee="0" new_balance="90" body="a"/>'
            '<sms id="2" amount="20" fee="0" new_balance="70" body="b"/>'
            '<sms id="3" amount="30" fee="0" new_balance="40" body="c"/>'
            "</messages>"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sample.xml")
            with open(path, "w") as f:
                f.write(xml)
            with mock.patch.object(compare_search, "XML_PATH", path):
                records, source = compare_search.load_records(5000)

        self.assertEqual(len(records), 5000)
        self.assertIn("padded", source)
        self.assertEqual(records[0]["amount"], 10.0)  # real rows come first

        ids = [r["id"] for r in records]
        self.assertEqual(len(set(ids)), 5000, "ids must stay unique after padding")

        index = build_index(records)
        self.assertEqual(linear_search(records, 5000), index.get(5000))

    def test_truncates_long_real_xml_to_the_requested_size(self):
        rows = "".join(f'<sms id="{i}" amount="{i}"/>' for i in range(1, 11))
        xml = f"<messages>{rows}</messages>"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sample.xml")
            with open(path, "w") as f:
                f.write(xml)
            with mock.patch.object(compare_search, "XML_PATH", path):
                records, source = compare_search.load_records(5)

        self.assertEqual(len(records), 5)
        self.assertEqual(source, "data/modified_sms_v2.xml")
        self.assertEqual([r["id"] for r in records], [1, 2, 3, 4, 5])


class EvidenceFileTest(unittest.TestCase):
    def test_committed_search_evidence_exists_and_is_complete(self):
        # Read-only check: the submission evidence must be present and cover
        # the required points. (Regenerate it with: python3 dsa/compare_search.py)
        self.assertTrue(os.path.exists(SEARCH_EVIDENCE),
                        "docs/dsa_search_evidence.txt is missing")
        with open(SEARCH_EVIDENCE) as f:
            evidence = f.read()

        for marker in ("DSA Integration & Testing", "Linear search", "Dictionary",
                       "Speed-up", "mismatches", "O(n)", "O(1)"):
            self.assertIn(marker, evidence)


if __name__ == "__main__":
    unittest.main()

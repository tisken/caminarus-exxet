from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GENERATED = ROOT / "data/generated"


def load_json(name: str):
    return json.loads((GENERATED / name).read_text(encoding="utf-8"))


class GeneratedDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = load_json("index.json")
        cls.core = load_json("core-exxet.records.json")
        cls.walking = load_json("caminaron-con-nosotros.records.json")

    def test_index_lists_both_books(self):
        dataset_ids = [dataset["id"] for dataset in self.index["datasets"]]
        self.assertEqual(dataset_ids, ["core-exxet", "caminaron-con-nosotros"])

    def test_record_counts_are_reasonable(self):
        self.assertGreaterEqual(self.core["count"], 20)
        self.assertGreaterEqual(self.walking["count"], 80)

    def test_core_contains_expected_entries(self):
        names = {record["name"] for record in self.core["records"]}
        self.assertIn("Lagor (Araña Psíquica)", names)
        self.assertIn("Nezuacuatil (Enjambre de cucarachas)", names)
        self.assertIn("Dragón (Antiguo)", names)
        self.assertIn("Zombi", names)

    def test_walking_contains_expected_entries(self):
        names = {record["name"] for record in self.walking["records"]}
        self.assertIn("Abominación (Semilla Primigenia)", names)
        self.assertIn("Balzak (Sacerdote)", names)
        self.assertIn("Portador (Menor)", names)
        self.assertIn("Señor de los Muertos (No muerto supremo)", names)

    def test_no_remaining_extraction_warnings(self):
        self.assertEqual(self.core["warningCount"], 0)
        self.assertEqual(self.walking["warningCount"], 0)


if __name__ == "__main__":
    unittest.main()

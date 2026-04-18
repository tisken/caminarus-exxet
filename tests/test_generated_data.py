from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GENERATED = ROOT / "data/generated"
MANIFEST = ROOT / "module.json"
DIST_ZIP = ROOT / "dist/animu-exxet.zip"


def load_json(path: Path | str):
    if isinstance(path, str):
        path = GENERATED / path
    return json.loads(path.read_text(encoding="utf-8"))


class GeneratedDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = load_json("index.json")
        cls.records = {
            dataset["id"]: load_json(dataset["recordsFilename"])
            for dataset in cls.index["datasets"]
        }
        cls.datasets = {
            dataset["id"]: load_json(dataset["filename"])
            for dataset in cls.index["datasets"]
        }
        cls.manifest = load_json(MANIFEST)

    def test_index_lists_expected_books(self):
        dataset_ids = [dataset["id"] for dataset in self.index["datasets"]]
        self.assertEqual(
            dataset_ids,
            [
                "core-exxet",
                "caminaron-con-nosotros",
                "complemento-web-vol-1",
                "guia-del-mundo-perfecto",
                "dramatis-personae",
                "dramatis-personae-vol-2",
                "pantalla-del-director",
                "dravenor-parte-1",
                "dravenor-parte-2",
                "dravenor-parte-3",
            ],
        )

    def test_record_counts_are_reasonable(self):
        minimums = {
            "core-exxet": 20,
            "caminaron-con-nosotros": 80,
            "complemento-web-vol-1": 5,
            "guia-del-mundo-perfecto": 15,
            "dramatis-personae": 10,
            "dramatis-personae-vol-2": 10,
            "pantalla-del-director": 25,
            "dravenor-parte-1": 5,
            "dravenor-parte-2": 5,
            "dravenor-parte-3": 3,
        }
        for dataset_id, minimum in minimums.items():
            with self.subTest(dataset_id=dataset_id):
                self.assertGreaterEqual(self.records[dataset_id]["count"], minimum)

    def test_known_entries_present(self):
        expected_names = {
            "core-exxet": {
                "Lagor (Araña Psíquica)",
                "Nezuacuatil (Enjambre de cucarachas)",
                "Dragón (Antiguo)",
                "Zombi",
            },
            "caminaron-con-nosotros": {
                "Abominación (Semilla Primigenia)",
                "Balzak (Sacerdote)",
                "Portador (Menor)",
                "Señor de los Muertos (No muerto supremo)",
            },
            "dramatis-personae": {
                "XII",
                "Kali",
                "El Coronel",
            },
            "dramatis-personae-vol-2": {
                "Balthassar, el Monstruo",
                "Killrayne, Ejecutor Imperial Supremo",
                "Matthew Gaul, Arconte Supremo",
            },
            "pantalla-del-director": {
                "Faust Orbatos",
                "Shion Demeter",
                "Raptor el Ejecutor Oscuro",
            },
            "dravenor-parte-1": {
                "Araña de Tierra (La Máquina · Varna menor)",
                "Colosal (La Máquina · Varna mayor)",
            },
        }
        for dataset_id, names in expected_names.items():
            dataset_names = {record["name"] for record in self.records[dataset_id]["records"]}
            for name in names:
                with self.subTest(dataset_id=dataset_id, name=name):
                    self.assertIn(name, dataset_names)

    def test_no_remaining_extraction_warnings(self):
        for dataset_id, data in self.records.items():
            with self.subTest(dataset_id=dataset_id):
                self.assertEqual(data["warningCount"], 0)

    def test_notes_are_embedded_for_unmapped_fields(self):
        core_first = self.datasets["core-exxet"]["documents"][0]
        self.assertTrue(core_first["system"]["general"]["notes"])
        self.assertEqual(core_first["system"]["general"]["notes"][0]["type"], "note")

        dramatic = next(
            document
            for document in self.datasets["dramatis-personae"]["documents"]
            if document["name"] == "XII"
        )
        note_names = [note["name"] for note in dramatic["system"]["general"]["notes"]]
        self.assertTrue(any(name.startswith("Ki:") for name in note_names))
        self.assertTrue(any(name.startswith("Técnicas:") for name in note_names))

    def test_manifest_is_installable_from_github(self):
        self.assertEqual(self.manifest["id"], "animu-exxet")
        self.assertEqual(self.manifest["version"], "0.2.0")
        self.assertTrue(DIST_ZIP.exists())
        self.assertEqual(
            self.manifest["manifest"],
            "https://raw.githubusercontent.com/tisken/caminarus-exxet/main/module.json",
        )
        self.assertEqual(
            self.manifest["download"],
            "https://raw.githubusercontent.com/tisken/caminarus-exxet/main/dist/animu-exxet.zip",
        )
        dependency = self.manifest["relationships"]["systems"][0]
        self.assertEqual(dependency["id"], "animabf")
        self.assertIn("manifest", dependency)


if __name__ == "__main__":
    unittest.main()

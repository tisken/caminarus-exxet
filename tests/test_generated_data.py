from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GENERATED = ROOT / "data/generated"
MANIFEST = ROOT / "module.json"
DIST_ZIP = ROOT / "dist/animu-exxet.zip"
PACKS = ROOT / "packs"


def load_json(path: Path | str):
    if isinstance(path, str):
        path = GENERATED / path
    return json.loads(path.read_text(encoding="utf-8"))


def expected_token_dimensions(size_value: int | None) -> float:
    if size_value is None or size_value == '' or size_value == '0':
        return 1
    sv = int(size_value) if isinstance(size_value, str) else size_value
    if sv <= 0:
        return 1
    if sv <= 3:
        return 0.25
    if sv <= 8:
        return 0.5
    if sv <= 22:
        return 1
    if sv <= 24:
        return 2
    if sv <= 28:
        return 3
    if sv <= 33:
        return 4
    return 5


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
                "gaia-vol-1",
                "gaia-vol-2",
                "fichas-sueltas",
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
                "Raptor, el Ejecutor Oscuro",
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
        self.assertEqual(self.manifest["version"], "2.2.0")
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

    def test_manifest_declares_static_pack(self):
        self.assertGreaterEqual(len(self.manifest["packs"]), 1)
        pack_names = [p["name"] for p in self.manifest["packs"]]
        self.assertIn("creatures-exxet", pack_names)

    def test_pack_directories_match_generated_counts(self):
        pack_dir = PACKS / "creatures-exxet"
        self.assertTrue(pack_dir.exists())

        import plyvel
        db = plyvel.DB(str(pack_dir), create_if_missing=False)
        actors = []
        folders = []
        for key, value in db:
            k = key.decode("utf-8")
            obj = json.loads(value.decode("utf-8"))
            if k.startswith("!actors!") and ".items!" not in k:
                actors.append(obj)
            elif k.startswith("!folders!"):
                folders.append(obj)
        db.close()

        self.assertGreaterEqual(len(folders), len(self.index["datasets"]) + 1)
        self.assertEqual(
            len(actors),
            sum(dataset["count"] for dataset in self.index["datasets"]),
        )

        folder_ids = {folder["_id"] for folder in folders}
        root_folder = next(folder for folder in folders if folder["name"] == "Creatures Exxet")
        child_folders = [folder for folder in folders if folder["folder"] == root_folder["_id"]]
        self.assertIsNone(root_folder["folder"])
        self.assertTrue(
            {dataset["label"] for dataset in self.index["datasets"]}.issubset(
                {folder["name"] for folder in child_folders}
            )
        )

        sample = actors[0]
        self.assertEqual(sample["type"], "character")
        self.assertIn("_id", sample)
        self.assertEqual(sample["ownership"]["default"], 0)
        self.assertEqual(sample["_stats"]["systemId"], "animabf")
        self.assertIn(sample["folder"], folder_ids)

    def test_token_size_table_matches_requested_ranges(self):
        self.assertEqual(expected_token_dimensions(None), 1)
        self.assertEqual(expected_token_dimensions(0), 1)
        self.assertEqual(expected_token_dimensions(1), 0.25)
        self.assertEqual(expected_token_dimensions(3), 0.25)
        self.assertEqual(expected_token_dimensions(4), 0.5)
        self.assertEqual(expected_token_dimensions(8), 0.5)
        self.assertEqual(expected_token_dimensions(9), 1)
        self.assertEqual(expected_token_dimensions(22), 1)
        self.assertEqual(expected_token_dimensions(23), 2)
        self.assertEqual(expected_token_dimensions(24), 2)
        self.assertEqual(expected_token_dimensions(25), 3)
        self.assertEqual(expected_token_dimensions(28), 3)
        self.assertEqual(expected_token_dimensions(29), 4)
        self.assertEqual(expected_token_dimensions(33), 4)
        self.assertEqual(expected_token_dimensions(34), 5)


if __name__ == "__main__":
    unittest.main()

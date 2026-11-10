#!/usr/bin/env python3
"""Apply the small, owner-approved additive recipe batch to the built site.

The large canonical data files remain untouched in GitHub. This step updates
only the compiled site copies before validation and publication.
"""
import argparse
import json
from pathlib import Path

BATCH = "approved-additions-20261110.json"

def apply(site: Path):
    data_dir = site / "data"
    raw = json.loads((data_dir / "recipes.json").read_text(encoding="utf-8"))
    media = json.loads((data_dir / "media.json").read_text(encoding="utf-8"))
    additions = json.loads((data_dir / BATCH).read_text(encoding="utf-8"))
    existing_ids = {r["id"] for r in raw["recipes"]}
    existing_photos = set(media["photos"])
    new_ids = [r["id"] for r in additions["recipes"]]
    new_photos = additions["photos"]
    assert new_ids == list(range(642, 650)), "Unexpected approved IDs"
    assert len(set(new_ids)) == len(new_ids)
    assert not existing_ids.intersection(new_ids), "Recipe ID collision"
    assert not existing_photos.intersection(new_photos), "Photo key collision"
    for item in additions["recipes"]:
        assert item["photo"] in new_photos, "Missing photo key"
        assert item["cat"] in raw["categories"], "Unknown category"
    raw["recipes"].extend(additions["recipes"])
    raw["metadata"]["total"] = len(raw["recipes"])
    media["photos"].update(new_photos)
    for name, payload in (("recipes.json", raw), ("media.json", media)):
        (data_dir / name).write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8")
    # Keep the release input self-contained and avoid a third data file in Pages.
    (data_dir / BATCH).unlink()
    print(f"Applied approved recipes {new_ids[0]}-{new_ids[-1]}: "
          f"{raw['metadata']['total']} recipes, {len(media['photos'])} photos")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    apply(parser.parse_args().site)

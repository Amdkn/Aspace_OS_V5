#!/usr/bin/env python3
"""Régénération déterministe de memory.json depuis memory.jsonl (D-N049, D4).

Règle de dérivation (prouvée byte-identique sur l'instantané existant) :
  snapshot = {"entities": <les 4 premières entités du JSONL, dans l'ordre>,
              "relations": <les relations dont les deux extrémités sont
                            parmi ces 4 entités, dans l'ordre du JSONL>}
  écriture = json.dumps(..., indent=2, ensure_ascii=False) + "\\n"

La portée (4 premières entités) reproduit la dérivation que le fichier a
toujours eue. Changer la portée est un amendement (Clara), pas un correctif
de l'instrument. La suppression de l'instantané exige un amendement prouvant
qu'aucun consommateur ne lit memory.json (le standard @modelcontextprotocol/
server-memory lit memory.json par défaut — consommateur présumé).

Usage :
  derive-memory-snapshot.py            régénère 00_Memoire/shared_brain/memory.json
  derive-memory-snapshot.py --check    vérifie que l'instantané == la dérivation (exit 1 sinon)
"""
import json
import sys
from pathlib import Path

SNAPSHOT_ENTITIES = 4
REPO = Path(__file__).resolve().parents[3]
JSONL = REPO / "00_Memoire" / "shared_brain" / "memory.jsonl"
SNAPSHOT = REPO / "00_Memoire" / "shared_brain" / "memory.json"


def derive():
    records = [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
    entities = [{k: v for k, v in r.items() if k != "type"}
                for r in records if r.get("type") == "entity"]
    names = {e["name"] for e in entities[:SNAPSHOT_ENTITIES]}
    relations = [{k: v for k, v in r.items() if k != "type"}
                 for r in records if r.get("type") == "relation"
                 and r["from"] in names and r["to"] in names]
    return json.dumps({"entities": entities[:SNAPSHOT_ENTITIES], "relations": relations},
                      indent=2, ensure_ascii=False) + "\n"


def main():
    check = "--check" in sys.argv
    derived = derive()
    if check:
        actual = SNAPSHOT.read_text(encoding="utf-8")
        if actual != derived:
            print("MISMATCH: memory.json != derivation from memory.jsonl", file=sys.stderr)
            return 1
        print(f"OK: memory.json == derivation ({len(derived)} bytes)")
        return 0
    SNAPSHOT.write_text(derived, encoding="utf-8")
    print(f"OK: memory.json regenerated ({len(derived)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

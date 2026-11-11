#!/usr/bin/env python3
"""Harnais P0 — vérification mécanique de 01_Forkable/MODULES-LOCK.json.

Vérifications (Discover piste F §8.3) :
  1. gitlink(V5 HEAD) == pin (lu dans l'arbre, pas dans un doc).
  2. adapter_parent == gel (lignée adapter ; 1er commit adapter, H-M2),
     ou écart documenté. Modules sans adapter (natif/local) : SKIP documenté.
  3. compare(gel...pin) consigné : ahead == len(commits), behind == 0,
     chaque commit ∈ adapter_commits ∪ {bind_commit} ∪ pin_extra_commits.
     Avec --live : re-vérifie le compare à l'API GitHub (gh).
  4. capabilities_owned : chaque capacité n'a qu'un seul propriétaire.
  5. state : toute montée d'état (state >= 1) cite un jugement 13e
     (numéro de journal + SHA de merge 40 car.) dans state_owner.
  6. state >= 1 exige manifeste + fiche + adapter_commit présents.

Usage (depuis la racine du repo V5) :
  python3 01_Forkable/check-modules-lock.py [--live] [--lock PATH]
Sortie : une ligne par vérification + détail par module ; code 0 si les
vérifications 1-4 sont VERTES (les 5-6 rapportent leurs trous sans masquer).
Code 1 si une vérification 1-4 échoue.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

SHA40 = re.compile(r"\b[0-9a-f]{40}\b")
# « jugement 482 » oui ; « jugement 13e » (le 13e Doctor) non — le « e »
# exclut la fausse correspondance sur le nom du validateur.
JUGEMENT = re.compile(r"jugement\s+(\d+)(?![e0-9])", re.IGNORECASE)

LOCK_PATH = pathlib.Path("01_Forkable/MODULES-LOCK.json")


def git_ls_tree(path):
    """SHA du gitlink à path dans HEAD, ou None si pas un gitlink."""
    r = subprocess.run(
        ["git", "ls-tree", "HEAD", path],
        capture_output=True, text=True, check=False)
    if r.returncode != 0:
        return "ERROR:" + r.stderr.strip()
    out = r.stdout.strip()
    if not out:
        return None
    mode, _typ, sha = out.split()[0], out.split()[1], out.split()[2]
    return sha if mode == "160000" else "NOT-GITLINK:" + mode


def gh_api(path):
    r = subprocess.run(["gh", "api", path, "--jq",
                        "{ahead: .ahead_by, behind: .behind_by, "
                        "status: .status, commits: [.commits[].sha]}"],
                       capture_output=True, text=True, check=False)
    if r.returncode != 0:
        return None, r.stderr.strip()[:200]
    try:
        return json.loads(r.stdout), None
    except json.JSONDecodeError:
        return None, "réponse gh illisible"


def gh_commit_parent(repo, sha):
    r = subprocess.run(["gh", "api", f"repos/{repo}/commits/{sha}",
                        "--jq", "{sha: .sha, parents: [.parents[].sha]}"],
                       capture_output=True, text=True, check=False)
    if r.returncode != 0:
        return None, r.stderr.strip()[:200]
    try:
        return json.loads(r.stdout), None
    except json.JSONDecodeError:
        return None, "réponse gh illisible"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true",
                    help="re-vérifie compares + parents à l'API GitHub")
    ap.add_argument("--lock", default=str(LOCK_PATH))
    args = ap.parse_args()

    lock = json.loads(pathlib.Path(args.lock).read_text())
    modules = lock["modules"]
    results = []  # (check_no, module_id, status, detail)

    # --- Vérification 1 : gitlink == pin --------------------------------
    for m in modules:
        if m["gitlink"] is None:
            why = ("greffe coupée F8 pas 5" if m["id"] == "fiber:a0:agent-zero"
                   else "adapter local, pas de fork")
            results.append((1, m["id"], "SKIP",
                            f"pas de gitlink ({why}) — documenté au lock"))
            continue
        actual = git_ls_tree(m["v5_path"])
        if actual == m["pin"]:
            results.append((1, m["id"], "PASS", f"gitlink == pin {m['pin'][:7]}"))
        else:
            results.append((1, m["id"], "FAIL",
                            f"gitlink arbre={actual} != pin={m['pin']}"))

    # --- Vérification 2 : adapter_parent == gel -------------------------
    for m in modules:
        if not m["adapter_commits"]:
            results.append((2, m["id"], "SKIP",
                            "pas d'adapter (natif RigInfinity) — documenté"))
            continue
        if m["adapter_parent"] is None:
            results.append((2, m["id"], "SKIP",
                            "adapter local versionné dans V5 (aqua) : pas de "
                            "gel amont — documenté"))
            continue
        ok = m["adapter_parent"] == m["gel"]
        detail = (f"parent du 1er adapter {m['adapter_commits'][0][:7]} = "
                  f"{(m['adapter_parent'] or '')[:7]} ; gel = "
                  f"{(m['gel'] or '')[:7]}")
        if args.live and ok:
            live, err = gh_commit_parent(m["repo"], m["adapter_commits"][0])
            if live is None:
                results.append((2, m["id"], "WARN",
                                detail + f" ; --live indisponible : {err}"))
                continue
            parents = live.get("parents", [])
            ok = parents == [m["gel"]]
            detail += f" ; --live parents={ [p[:7] for p in parents] }"
        results.append((2, m["id"], "PASS" if ok else "FAIL", detail))

    # --- Vérification 3 : compare(gel...pin) consigné -------------------
    for m in modules:
        c = m.get("gel_pin_compare")
        if c is None:
            results.append((3, m["id"], "SKIP",
                            "pas de compare gel...pin (natif/local) — documenté"))
            continue
        allowed = set(m["adapter_commits"])
        if m.get("bind_commit"):
            allowed.add(m["bind_commit"])
        allowed |= {e["sha"] for e in m.get("pin_extra_commits", [])}
        recorded = c["commits"]
        ok = (c["ahead"] == len(recorded) and c["behind"] == 0
              and set(recorded) <= allowed)
        detail = (f"consigné ahead={c['ahead']} behind={c['behind']} "
                  f"commits={[s[:7] for s in recorded]}")
        if not ok:
            detail += " ; INCOHÉRENT (ahead != len(commits), behind != 0, ou commit hors adapter/bind/extra)"
        if args.live and ok:
            live, err = gh_api(
                f"repos/{m['repo']}/compare/{m['gel']}...{m['pin']}")
            if live is None:
                results.append((3, m["id"], "WARN",
                                detail + f" ; --live indisponible : {err}"))
                continue
            ok = (live["ahead"] == c["ahead"]
                  and live["behind"] == c["behind"]
                  and live["commits"] == recorded)
            detail += (f" ; --live ahead={live['ahead']} "
                       f"behind={live['behind']} "
                       f"commits={[s[:7] for s in live['commits']]}")
        results.append((3, m["id"], "PASS" if ok else "FAIL", detail))

    # --- Vérification 4 : unicité des capabilities_owned ----------------
    owners = {}
    dup = []
    for m in modules:
        for cap in m["capabilities_owned"]:
            if cap in owners:
                dup.append((cap, owners[cap], m["id"]))
            owners[cap] = m["id"]
    if dup:
        for cap, a, b in dup:
            results.append((4, cap, "FAIL", f"deux propriétaires : {a} et {b}"))
    else:
        results.append((4, "toutes", "PASS",
                        f"{len(owners)} capacités, 1 propriétaire chacune"))

    # --- Vérification 5 : jugement 13e pour toute montée d'état ---------
    for m in modules:
        if m["state"] < 1:
            results.append((5, m["id"], "SKIP",
                            f"état {m['state']} : aucune montée à justifier"))
            continue
        j = JUGEMENT.search(m["state_owner"] or "")
        s = SHA40.search(m["state_owner"] or "")
        if j and s:
            results.append((5, m["id"], "PASS",
                            f"jugement {j.group(1)}, merge {s.group(0)[:7]}"))
        else:
            missing = []
            if not j:
                missing.append("numéro de journal 13e")
            if not s:
                missing.append("SHA de merge (40 car.)")
            results.append((5, m["id"], "GAP",
                            "manquant : " + " + ".join(missing)
                            + f" — state_owner={m['state_owner'][:120]}…"))

    # --- Vérification 6 : état >= 1 exige manifeste + fiche + adapter --
    for m in modules:
        if m["state"] < 1:
            results.append((6, m["id"], "SKIP",
                            f"état {m['state']} : manifeste/fiche non exigés"))
            continue
        missing = []
        if not m["manifest"]:
            missing.append("manifeste (null)")
        elif not pathlib.Path(m["manifest"]).exists():
            missing.append(f"manifeste absent au fichier ({m['manifest']})")
        # La fiche vit dans 00_A0_Core quel que soit le pôle du module.
        fiche = pathlib.Path(
            "01_Forkable/FKB00_Runtime/00_A0_Core/"
            f"{m['id'].split(':')[-1]}-ADAPTATION.md")
        if not fiche.exists():
            missing.append(f"fiche absente ({fiche})")
        if not m["adapter_commit"]:
            missing.append("adapter_commit (null)")
        if missing:
            results.append((6, m["id"], "FAIL", "; ".join(missing)))
        else:
            results.append((6, m["id"], "PASS",
                            "manifeste + fiche + adapter_commit présents"))

    # --- Bilan ------------------------------------------------------------
    by_check = {}
    for n, mid, st, detail in results:
        by_check.setdefault(n, []).append((mid, st, detail))
    overall_14 = True
    for n in sorted(by_check):
        statuses = [st for _, st, _ in by_check[n]]
        if n <= 4:
            ok = all(s in ("PASS", "SKIP") for s in statuses)
            overall_14 = overall_14 and ok
            verdict = "VERT" if ok else "ROUGE"
        else:
            bad = [s for s in statuses if s in ("FAIL", "GAP")]
            verdict = f"{len(bad)} trou(s) consigné(s)" if bad else "VERT"
        print(f"\n== Vérification {n} : {verdict} ==")
        for mid, st, detail in by_check[n]:
            print(f"  [{st:4}] {mid} — {detail}")
    print("\n== Bilan ==")
    print(f"  Vérifications 1-4 : {'VERTES' if overall_14 else 'ROUGE — BLOQUANT'}")
    for n in (5, 6):
        bad = [(mid, d) for mid, st, d in by_check[n] if st in ("FAIL", "GAP")]
        print(f"  Vérification {n} : {len(by_check[n]) - len(bad)}/{len(by_check[n])} "
              f"OK, {len(bad)} trou(s)")
    print(f"  Lock : {args.lock} | v5_head={lock['v5_head'][:7]} | "
          f"pin_rule={lock['pin_rule']} | modules={len(modules)}")
    return 0 if overall_14 else 1


if __name__ == "__main__":
    sys.exit(main())

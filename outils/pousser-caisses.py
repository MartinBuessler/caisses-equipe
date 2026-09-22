#!/usr/bin/env python3
"""Envoie les caisses de data/*.json vers la base, et les relit pour verifier.

    python outils/pousser-caisses.py            # toutes les caisses
    python outils/pousser-caisses.py kine-1     # une seule
    python outils/pousser-caisses.py --lire     # ne fait que lire ce qu'il y a en base

La base accepte l'ecriture sans identifiant, comme depuis un telephone :
ce script emprunte exactement le meme chemin que la page.
"""
import json, os, sys, urllib.request, urllib.error

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJET = "atelier-2sa"
CLE = "AIzaSyBPjpEZSx-QxagoFvJbWJtlc9QmHXjlpB4"
DOCS = "https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents" % PROJET


def appel(url, corps=None, methode="GET"):
    data = json.dumps(corps).encode("utf-8") if corps is not None else None
    req = urllib.request.Request(url, data=data, method=methode,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        corps_err = e.read().decode("utf-8", "replace")
        try:
            corps_err = json.loads(corps_err)
        except Exception:
            pass
        return e.code, corps_err


def lire(caisse):
    code, rep = appel("%s/caisses/%s?key=%s" % (DOCS, caisse, CLE))
    if code == 404:
        return None
    if code != 200:
        raise RuntimeError("lecture %s : %s" % (code, rep))
    brut = rep.get("fields", {}).get("donnees", {}).get("stringValue")
    return json.loads(brut) if brut else None


def ecrire(caisse, contenu):
    ecriture = {
        "update": {
            "name": "projects/%s/databases/(default)/documents/caisses/%s" % (PROJET, caisse),
            "fields": {
                "donnees": {"stringValue": json.dumps(contenu, ensure_ascii=False)},
                "maj": {"stringValue": contenu.get("maj", "")},
            },
        },
        "updateMask": {"fieldPaths": ["donnees", "maj"]},
    }
    code, rep = appel("%s:commit?key=%s" % (DOCS, CLE), {"writes": [ecriture]}, "POST")
    if code != 200:
        raise RuntimeError("ecriture %s : %s" % (code, rep))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    lecture_seule = "--lire" in sys.argv

    fichiers = sorted(f for f in os.listdir(os.path.join(RACINE, "data")) if f.endswith(".json"))
    caisses = [f[:-5] for f in fichiers]
    if args:
        caisses = [c for c in caisses if c in args]
        if not caisses:
            sys.exit("Aucune caisse ne correspond. Connues : " + ", ".join(f[:-5] for f in fichiers))

    for c in caisses:
        if lecture_seule:
            d = lire(c)
            print("%-12s %s" % (c, "absente de la base" if d is None
                                else "%s, %d produits, maj %s" % (d.get("nom"), len(d.get("produits", [])), d.get("maj", "?"))))
            continue

        with open(os.path.join(RACINE, "data", c + ".json"), encoding="utf-8") as f:
            contenu = json.load(f)
        ecrire(c, contenu)
        relu = lire(c)
        ok = relu and len(relu.get("produits", [])) == len(contenu.get("produits", []))
        print("%-12s %s (%d produits)" % (c, "envoyee et relue" if ok else "ECHEC de verification",
                                          len(relu.get("produits", [])) if relu else 0))
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ramene toutes les caisses de la base vers data/*.json.

    python outils/tirer-caisses.py

Sert a la sauvegarde automatique : le depot garde une copie lisible et
restaurable de ce que contiennent les caisses. N'ecrit un fichier que si son
contenu a change, pour ne pas fabriquer de commit inutile.
"""
import json, os, sys, urllib.request, urllib.error

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJET = "atelier-2sa"
CLE = "AIzaSyBPjpEZSx-QxagoFvJbWJtlc9QmHXjlpB4"
DOCS = "https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents" % PROJET


def appel(url):
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def main():
    code, rep = appel("%s/caisses?key=%s&pageSize=300" % (DOCS, CLE))
    if code != 200:
        print("lecture de la base impossible : %s %s" % (code, rep), file=sys.stderr)
        return 1

    documents = rep.get("documents", [])
    if not documents:
        print("la base ne contient aucune caisse", file=sys.stderr)
        return 1

    dossier = os.path.join(RACINE, "data")
    os.makedirs(dossier, exist_ok=True)
    changes = 0

    for d in documents:
        ident = d["name"].split("/")[-1]
        brut = d.get("fields", {}).get("donnees", {}).get("stringValue")
        if not brut:
            print("%-12s vide, ignoree" % ident)
            continue
        try:
            contenu = json.loads(brut)
        except Exception as e:
            print("%-12s illisible (%s), ignoree" % (ident, e), file=sys.stderr)
            continue

        texte = json.dumps(contenu, ensure_ascii=False, indent=1) + "\n"
        chemin = os.path.join(dossier, ident + ".json")
        ancien = None
        if os.path.exists(chemin):
            with open(chemin, encoding="utf-8") as f:
                ancien = f.read()
        if ancien == texte:
            print("%-12s inchangee" % ident)
            continue
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(texte)
        changes += 1
        print("%-12s ramenee (%d produits)" % (ident, len(contenu.get("produits", []))))

    print("%d caisse(s) mise(s) a jour" % changes)
    return 0


if __name__ == "__main__":
    sys.exit(main())

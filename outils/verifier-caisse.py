#!/usr/bin/env python3
"""Verifie qu'un fichier de caisse est lisible et coherent.

    python outils/verifier-caisse.py data/epicerie.json

Sort 0 si le fichier est sain, 1 sinon, avec la raison sur la sortie d'erreur.
Sert au controle automatique declenche a chaque modification.
"""
import json
import sys


def verifier(chemin):
    with open(chemin, encoding="utf-8") as f:
        d = json.load(f)                      # leve si le JSON est casse

    if not isinstance(d, dict):
        raise ValueError("le fichier ne contient pas un objet")
    for champ in ("caisse", "nom", "produits"):
        if champ not in d:
            raise ValueError("champ manquant : %s" % champ)
    if not isinstance(d["produits"], list):
        raise ValueError("produits n'est pas une liste")
    if not isinstance(d.get("journal", []), list):
        raise ValueError("journal n'est pas une liste")
    if not str(d["caisse"]).strip():
        raise ValueError("identifiant de caisse vide")

    vus = set()
    for i, p in enumerate(d["produits"]):
        ou = "produit %d" % i
        if not isinstance(p, dict):
            raise ValueError("%s n'est pas un objet" % ou)
        for champ in ("id", "nom", "qte"):
            if champ not in p:
                raise ValueError("%s : champ manquant %s" % (ou, champ))
        if p["id"] in vus:
            raise ValueError("%s : identifiant en double (%s)" % (ou, p["id"]))
        vus.add(p["id"])
        if not isinstance(p["qte"], int) or p["qte"] < 0:
            raise ValueError("%s (%s) : quantite invalide %r" % (ou, p["nom"], p["qte"]))
        if not str(p["nom"]).strip():
            raise ValueError("%s : nom vide" % ou)

    return len(d["produits"])


def main():
    if len(sys.argv) != 2:
        sys.exit("usage : verifier-caisse.py <fichier.json>")
    chemin = sys.argv[1]
    try:
        n = verifier(chemin)
    except Exception as e:
        print("%s : %s" % (chemin, e), file=sys.stderr)
        return 1
    print("%s : %d produits, coherent" % (chemin, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())

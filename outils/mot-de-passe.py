#!/usr/bin/env python3
"""Change le mot de passe qui protege l'effacement de l'historique.

    python outils/mot-de-passe.py "mon nouveau mot de passe"

Seule l'empreinte du mot de passe est ecrite dans index.html : lire la page
publiee ne permet pas de retrouver le mot de passe. Le changement vaut pour
les trois caisses, puisqu'elles partagent la meme page.

Apres la commande, publier :
    git add index.html
    git commit -m "Nouveau mot de passe"
    git push
"""
import hashlib
import io
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(RACINE, "index.html")
MOTIF = re.compile(r"(const EMPREINTE_MDP = ')([0-9a-f]{64})(';)")


def main():
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        sys.exit('usage : mot-de-passe.py "le nouveau mot de passe"')
    mdp = sys.argv[1]
    if len(mdp) < 6:
        sys.exit("Choisis au moins six caracteres.")

    empreinte = hashlib.sha256(mdp.encode("utf-8")).hexdigest()
    s = io.open(PAGE, encoding="utf-8").read()
    if not MOTIF.search(s):
        sys.exit("Empreinte introuvable dans index.html.")
    ancienne = MOTIF.search(s).group(2)
    if ancienne == empreinte:
        print("C'est deja ce mot de passe.")
        return
    s = MOTIF.sub(lambda m: m.group(1) + empreinte + m.group(3), s, count=1)
    io.open(PAGE, "w", encoding="utf-8").write(s)
    print("Mot de passe change.")
    print("  empreinte : %s" % empreinte)
    print("Publie-le : git add index.html ; git commit -m \"Nouveau mot de passe\" ; git push")


if __name__ == "__main__":
    main()

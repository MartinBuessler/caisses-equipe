#!/usr/bin/env python3
"""Change le mot de passe d'une caisse.

Le mot de passe est demande avant toute action qui detruit ou remplace :
effacer l'historique, supprimer l'inventaire, remettre l'exemple, importer un Excel.
Chaque caisse a le sien.

    python outils/mot-de-passe.py                     # liste les caisses protegees
    python outils/mot-de-passe.py kine-1 "strap26"    # change celui d'une caisse

Seule l'empreinte est ecrite dans index.html : lire la page publiee ne permet
pas de retrouver le mot de passe. Il reste devinable si on essaie des mots
courants, donc ce garde-fou arrete les gestes malheureux, pas un acharne.

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
BLOC = re.compile(r"const EMPREINTES_MDP = \{(.*?)\};", re.S)
LIGNE = re.compile(r"'([^']+)': '([0-9a-f]{64})'")


def lire_bloc():
    s = io.open(PAGE, encoding="utf-8").read()
    m = BLOC.search(s)
    if not m:
        sys.exit("Bloc des mots de passe introuvable dans index.html.")
    return s, m


def main():
    s, m = lire_bloc()
    entrees = LIGNE.findall(m.group(1))

    if len(sys.argv) == 1:
        print("Caisses protegees :")
        for ident, _ in entrees:
            print("  %-12s %s" % (ident, "(mot de passe de secours)" if ident == "_defaut" else ""))
        print('\nPour changer :  python outils/mot-de-passe.py <caisse> "le nouveau"')
        return

    if len(sys.argv) != 3 or not sys.argv[2].strip():
        sys.exit('usage : mot-de-passe.py <caisse> "le nouveau mot de passe"')

    caisse, mdp = sys.argv[1], sys.argv[2]
    connues = [i for i, _ in entrees]
    if caisse not in connues:
        sys.exit("Caisse inconnue : %s. Connues : %s" % (caisse, ", ".join(connues)))
    if len(mdp) < 4:
        sys.exit("Choisis au moins quatre caracteres.")

    empreinte = hashlib.sha256(mdp.encode("utf-8")).hexdigest()
    ancienne = dict(entrees)[caisse]
    if ancienne == empreinte:
        print("C'est deja ce mot de passe.")
        return

    avant = m.group(0)
    apres = avant.replace("'%s': '%s'" % (caisse, ancienne), "'%s': '%s'" % (caisse, empreinte))
    if avant == apres:
        sys.exit("Remplacement impossible, verifie index.html.")
    io.open(PAGE, "w", encoding="utf-8").write(s.replace(avant, apres, 1))

    print("Mot de passe de %s change." % caisse)
    print("  empreinte : %s" % empreinte)
    print('Publie-le :  git add index.html  puis  git commit -m "Nouveau mot de passe"  puis  git push')


if __name__ == "__main__":
    main()

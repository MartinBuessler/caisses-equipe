#!/usr/bin/env python3
"""Cree ou met a jour le fichier de donnees d'une caisse : data/<id>.json

Usage :
    python outils/creer-caisse.py epicerie
    python outils/creer-caisse.py kine-antoine --nom "Malle d'Antoine" --modele kine
    python outils/creer-caisse.py buvette --nom "Buvette" --categories "Boissons,Snacks" --vide
"""
import argparse, json, os, sys
from datetime import date, timedelta

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUJ = date.today()


def j(n):
    """Date absolue a n jours d'aujourd'hui, au format AAAA-MM-JJ."""
    return (AUJ + timedelta(days=n)).isoformat()


SUCRE, SALE = "Sucré", "Salé"

MODELES = {
    "epicerie": {
        "nom": "Caisse Épicerie Coupe du Monde",
        "categories": [SUCRE, SALE],
        "produits": [
            ("Barres céréales", SUCRE, 18, "barres", 120, 6),
            ("Barres aux fruits", SUCRE, 11, "barres", 75, 4),
            ("Barres chocolat-noisette", SUCRE, 3, "barres", 5, 4),
            ("Gels énergétiques", SUCRE, 14, "gels", 200, 6),
            ("Gels caféinés", SUCRE, 5, "gels", 180, 3),
            ("Pâtes de fruits", SUCRE, 12, "pièces", 60, 4),
            ("Compotes à boire", SUCRE, 7, "gourdes", 3, 4),
            ("Compotes pomme-banane", SUCRE, 10, "gourdes", 45, 4),
            ("Bananes", SUCRE, 4, "pièces", 2, 3),
            ("Clémentines", SUCRE, 8, "pièces", 6, 4),
            ("Amandes", SUCRE, 2, "sachets", 140, 1),
            ("Abricots secs", SUCRE, 1, "sachet", 130, 1),
            ("Dattes", SUCRE, 2, "boîtes", -2, 1),
            ("Biscuits sablés", SUCRE, 6, "paquets", 90, 2),
            ("Céréales petit-déjeuner", SUCRE, 2, "paquets", 150, 1),
            ("Confiture", SUCRE, 3, "pots", 400, 1),
            ("Miel", SUCRE, 1, "pot", 900, 1),
            ("Pâte à tartiner", SUCRE, 0, "pot", 200, 1),
            ("Chocolat noir", SUCRE, 4, "tablettes", 240, 2),
            ("Chocolat en poudre", SUCRE, 1, "boîte", 280, 1),
            ("Jus de fruits", SUCRE, 9, "briquettes", 110, 4),
            ("Lait d'amande", SUCRE, 2, "briques", -4, 1),
            ("Thon en boîte", SALE, 6, "boîtes", 700, 3),
            ("Sardines en boîte", SALE, 2, "boîtes", 650, 2),
            ("Maïs en boîte", SALE, 3, "boîtes", 500, 2),
            ("Haricots verts en boîte", SALE, 2, "boîtes", 500, 2),
            ("Riz (sachets cuisson rapide)", SALE, 8, "sachets", 600, 3),
            ("Pâtes", SALE, 3, "paquets", 600, 1),
            ("Semoule", SALE, 1, "paquet", 400, 1),
            ("Sauce tomate", SALE, 4, "briques", 300, 2),
            ("Soupe déshydratée", SALE, 10, "sachets", 250, 4),
            ("Bouillon cube", SALE, 0, "boîte", 300, 1),
            ("Galettes de riz", SALE, 2, "paquets", 80, 1),
            ("Pain de mie", SALE, 1, "paquet", 4, 1),
            ("Crackers apéritif", SALE, 5, "paquets", 120, 2),
            ("Chips", SALE, 0, "paquets", 60, 2),
            ("Cacahuètes salées", SALE, 3, "sachets", 180, 2),
            ("Jambon sec", SALE, 2, "paquets", 20, 1),
            ("Fromage à tartiner", SALE, 4, "portions", 30, 2),
            ("Œufs durs", SALE, 6, "pièces", 7, 3),
            ("Huile d'olive", SALE, 1, "bouteille", 400, 1),
            ("Sel & poivre", SALE, 2, "boîtes", None, 1),
            ("Eau (bouteilles 50 cl)", SALE, 12, "bouteilles", 600, 6),
            ("Café soluble", SALE, 1, "pot", 365, 1),
            ("Thé & infusions", SALE, 30, "sachets", 500, 10),
        ],
    },
    "kine": {
        "nom": "Malle du Kiné",
        "categories": ["Strapping", "Soins", "Matériel"],
        "produits": [
            ("Bande élastique 6 cm", "Strapping", 12, "rouleaux", None, 4),
            ("Bande élastique 8 cm", "Strapping", 8, "rouleaux", None, 3),
            ("Tape rigide 3,8 cm", "Strapping", 10, "rouleaux", None, 4),
            ("Tape rigide 2,5 cm", "Strapping", 4, "rouleaux", None, 4),
            ("K-tape", "Strapping", 6, "rouleaux", None, 2),
            ("Sous-bande mousse", "Strapping", 9, "rouleaux", None, 3),
            ("Spray adhérent", "Strapping", 2, "aérosols", 400, 1),
            ("Ciseaux à bandes", "Strapping", 3, "paires", None, 2),
            ("Bande cohésive", "Strapping", 0, "rouleaux", None, 3),
            ("Crème de massage", "Soins", 4, "tubes", 300, 2),
            ("Huile de massage", "Soins", 2, "flacons", 250, 1),
            ("Gel chauffant", "Soins", 3, "tubes", 180, 1),
            ("Gel froid", "Soins", 1, "tube", 5, 2),
            ("Poches de froid instantané", "Soins", 6, "poches", 500, 4),
            ("Arnica", "Soins", 2, "tubes", -10, 1),
            ("Compresses stériles", "Soins", 20, "sachets", 600, 8),
            ("Désinfectant cutané", "Soins", 1, "flacon", 120, 1),
            ("Pansements", "Soins", 30, "pièces", 700, 10),
            ("Steri-strips", "Soins", 0, "sachets", 400, 3),
            ("Sérum physiologique", "Soins", 8, "dosettes", 90, 4),
            ("Gants jetables", "Matériel", 40, "paires", None, 15),
            ("Élastiques de rééducation", "Matériel", 5, "bandes", None, 2),
            ("Balles de massage", "Matériel", 4, "pièces", None, 2),
            ("Rouleau de massage", "Matériel", 1, "pièce", None, 1),
            ("Électrodes", "Matériel", 2, "sachets", 200, 2),
            ("Thermomètre", "Matériel", 1, "pièce", None, 1),
            ("Sacs poubelle", "Matériel", 10, "sacs", None, 5),
        ],
    },
}


def produits_json(lignes):
    out = []
    for i, (nom, cat, qte, unite, jours, mini) in enumerate(lignes, start=1):
        out.append({
            "id": "p%03d" % i,
            "nom": nom,
            "cat": cat,
            "qte": qte,
            "unite": unite,
            "date": "" if jours is None else j(jours),
            "min": mini,
        })
    return out


def main():
    ap = argparse.ArgumentParser(description="Cree le fichier de donnees d'une caisse")
    ap.add_argument("id", help="identifiant de la caisse, en minuscules sans espace (ex. kine-antoine)")
    ap.add_argument("--nom", help="nom affiche en haut de la page")
    ap.add_argument("--modele", choices=sorted(MODELES), default="kine",
                    help="contenu de depart (defaut : kine)")
    ap.add_argument("--categories", help="categories separees par des virgules")
    ap.add_argument("--vide", action="store_true", help="creer la caisse sans aucun produit")
    ap.add_argument("--ecraser", action="store_true", help="remplacer un fichier existant")
    a = ap.parse_args()

    ident = "".join(c for c in a.id.lower() if c.isalnum() or c in "-_")
    if not ident:
        sys.exit("Identifiant invalide.")

    modele = MODELES[a.modele]
    cats = [c.strip() for c in a.categories.split(",")] if a.categories else list(modele["categories"])
    produits = [] if a.vide else produits_json(modele["produits"])
    if a.vide is False and a.categories:
        # on garde seulement les produits dont la categorie existe encore
        produits = [p for p in produits if p["cat"] in cats]

    caisse = {
        "caisse": ident,
        "nom": a.nom or modele["nom"],
        "categories": cats,
        "maj": AUJ.isoformat() + "T00:00:00.000Z",
        "produits": produits,
        "journal": [],
    }

    dossier = os.path.join(RACINE, "data")
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, ident + ".json")
    if os.path.exists(chemin) and not a.ecraser:
        sys.exit("Le fichier %s existe deja. Ajoute --ecraser pour le remplacer." % chemin)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(caisse, f, ensure_ascii=False, indent=1)
        f.write("\n")

    # on tient a jour la liste des caisses, utilisee pour generer les QR codes
    liste_chemin = os.path.join(RACINE, "caisses.json")
    liste = []
    if os.path.exists(liste_chemin):
        with open(liste_chemin, encoding="utf-8") as f:
            liste = json.load(f)
    liste = [c for c in liste if c["id"] != ident]
    liste.append({"id": ident, "nom": caisse["nom"]})
    liste.sort(key=lambda c: c["id"])
    with open(liste_chemin, "w", encoding="utf-8") as f:
        json.dump(liste, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print("Caisse creee : %s" % chemin)
    print("  nom        : %s" % caisse["nom"])
    print("  categories : %s" % ", ".join(cats))
    print("  produits   : %d" % len(produits))
    print("  adresse    : ?c=%s" % ident)


if __name__ == "__main__":
    main()

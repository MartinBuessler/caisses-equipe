# Déployer et séparer les caisses

Ce dépôt héberge à la fois la page et les données. Une caisse, c'est trois choses :
un identifiant, un fichier `data/<id>.json`, une adresse `?c=<id>`. Rien d'autre.

| | |
| --- | --- |
| Dépôt | `MartinBuessler/caisses-equipe` |
| Site | https://martinbuessler.github.io/caisses-equipe/ |
| Caisses existantes | `epicerie`, `kine-1`, `kine-2` |

---

> Les commandes ci-dessous sont écrites pour **PowerShell**, le terminal par défaut de
> Windows. Chaque commande va sur sa propre ligne : `&&` n'y fonctionne pas. Sous Git
> Bash ou macOS, tout marche aussi, et tu peux y enchaîner avec `&&`.

## 0. Une seule fois : installer les bibliothèques

Nécessaire uniquement pour générer les QR codes.

```powershell
python -m pip install "qrcode[pil]" reportlab
```

Déjà fait sur cette machine, pour le Python `miniconda3` qui répond à `python`.

## 1. Créer la caisse d'un kiné

> Les caisses existantes sont numérotées : `kine-1`, `kine-2`. La suivante est donc
> `kine-3`. Remplace le numéro et le nom par ce que tu veux voir sur l'étiquette.

Une commande, dans le dossier du projet :

```powershell
python outils/creer-caisse.py kine-3 --nom "Malle Kiné 3" --modele kine
```

Elle écrit `data/kine-3.json` avec un stock de kiné crédible (strapping, soins,
matériel) et inscrit la caisse dans `caisses.json`.

Options utiles :

```powershell
# une caisse vide, à remplir depuis le téléphone
python outils/creer-caisse.py kine-4 --nom "Malle Kiné 4" --vide

# des catégories sur mesure
python outils/creer-caisse.py buvette --nom "Buvette" --categories "Boissons,Snacks" --vide
```

Chaque caisse impose ses propres catégories. L'épicerie affiche Sucré et Salé, une malle
de kiné affiche Strapping, Soins et Matériel. La page s'adapte à la caisse ouverte.

## 2. Publier

Trois lignes, à lancer l'une après l'autre :

```powershell
git add -A
git commit -m "Nouvelle caisse : Malle Kine 3"
git push
```

Une minute plus tard, la caisse est en ligne à l'adresse
`https://martinbuessler.github.io/caisses-equipe/?c=kine-3`.

## 3. Imprimer l'étiquette

```powershell
python outils/generer-qr.py kine-3
```

Quatre fichiers apparaissent dans `qr/` : le QR seul en PNG et en SVG, l'étiquette A6
en PDF prête à imprimer et son aperçu PNG. Sans argument, la commande régénère toutes
les caisses.

L'étiquette fait 105 × 148 mm, soit un quart de A4. Imprime en taille réelle, sans
« ajuster à la page », sinon le QR rétrécit.

---

## Enregistrement et droits d'écriture

Sans clé, la page affiche le stock et garde les modifications sur le téléphone, rien
de plus. Avec la clé de l'équipe, chaque modification part sur GitHub et devient
visible par tout le monde.

**Créer la clé**, une seule fois pour toutes les caisses :

1. GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Generate new token
3. Repository access → Only select repositories → `caisses-equipe`
4. Permissions → Repository permissions → **Contents : Read and write**
5. Expiration : un an
6. Generate, puis copie la clé `github_pat_…` immédiatement, elle ne se réaffiche jamais

**Installer la clé sur un téléphone** : ouvrir la caisse, toucher la pastille en haut
à gauche, coller la clé dans le champ, puis « Enregistrer maintenant ». La pastille
passe au vert. C'est à faire une fois par téléphone, pas par caisse.

Plus rapide pour un groupe : envoie le lien
`https://martinbuessler.github.io/caisses-equipe/?c=epicerie#k=LA_CLE`. Au premier
ouverture la clé est rangée puis effacée de la barre d'adresse.

> Ce lien contient la clé. Il se transmet à l'équipe, pas sur l'étiquette collée sur
> la caisse ni sur un groupe ouvert. En cas de fuite, révoque la clé sur GitHub et
> refais-en une : le dépôt n'est pas exposé au-delà de ce seul dossier, et l'historique
> permet de revenir en arrière.

## Deux téléphones en même temps

Les modifications ne s'écrasent pas. Chaque téléphone garde la liste de ce qu'il a
fait, la rejoue sur la version du serveur, puis réécrit. Si quelqu'un a écrit entre
temps, la fusion est refaite automatiquement. Une personne qui sort deux bananes et
une autre qui range trois chips aboutissent bien à moins deux bananes et plus trois
chips, sans perte.

## Sauvegardes

Quatre filets, du plus immédiat au plus lointain :

1. **À chaque changement, un commit.** Une prise notée sur un téléphone devient
   aussitôt une version dans l'historique Git. Rien n'attend la nuit.
2. **À chaque changement, une vérification automatique.** Le fichier est contrôlé
   dès son arrivée : JSON lisible, champs présents, quantités positives, pas
   d'identifiant en double. S'il est abîmé, la dernière version saine est remise
   toute seule et un commit « Restauration automatique » le signale. Aucune
   intervention n'est nécessaire.
3. **À chaque changement, une copie hors de la branche**, conservée 90 jours dans
   l'onglet Actions. Elle survit même à une réécriture de l'historique.
4. **Une copie datée par jour**, dans `sauvegardes/AAAA-MM-JJ/`, produite à 3 h.
   Les soixante dernières sont conservées.

Pour contrôler une caisse à la main :

```powershell
python outils/verifier-caisse.py data/epicerie.json
```

**Restaurer une journée** :

```powershell
git pull
copy sauvegardes\2026-09-20\epicerie.json data\epicerie.json
git commit -am "Retour de l'epicerie au 20 septembre"
git push
```

**Annuler une seule bêtise**, sans tout restaurer :

```powershell
git log --oneline -- data/epicerie.json     # repérer le commit fautif
git revert <commit>
git push
```

Le bouton « Exporter » dans la page enregistre aussi la caisse courante en JSON sur
le téléphone, pratique avant une manipulation risquée.

---

## Séparer une caisse dans son propre dépôt

Utile si les kinés doivent gérer leurs malles sans toucher au reste, avec leurs
propres droits. Le prix à payer : deux sites, deux clés, deux sauvegardes à surveiller.

```powershell
# 1. nouveau dépôt à partir de celui-ci
gh repo create malles-kine --public --clone
cd malles-kine
copy ..\caisses-equipe\index.html .
copy ..\caisses-equipe\caisses.json .
xcopy /E /I ..\caisses-equipe\outils outils
xcopy /E /I ..\caisses-equipe\.github .github
mkdir data
copy ..\caisses-equipe\data\kine*.json data\

# 2. pointer le code vers le nouveau dépôt : dans index.html, bloc DEPOT,
#    remplacer  nom: 'caisses-equipe'  par  nom: 'malles-kine'
#    et         caisseParDefaut: 'epicerie'  par  'kine-1'
#    dans outils/generer-qr.py, corriger SITE de la même façon

# 3. publier
git add -A
git commit -m "Malles des kines"
git push
gh api -X POST repos/MartinBuessler/malles-kine/pages -f "source[branch]=main" -f "source[path]=/"

# 4. étiquettes à la nouvelle adresse
python outils/generer-qr.py
```

Il faut alors une clé distincte, limitée à `malles-kine`, et retirer les fichiers
`data/kine*.json` de l'ancien dépôt pour éviter deux vérités.

## Ce que ce montage ne fait pas

- **Le dépôt est public, donc le contenu des caisses est lisible par tous.** C'est un
  inventaire de nourriture et de matériel, sans donnée personnelle. Si cela devient
  gênant, passe le dépôt en privé : le site cesse alors d'être servi par GitHub Pages
  et il faut un autre hébergeur.
- **Écrire demande la clé.** Quelqu'un qui scanne sans l'avoir voit le stock et peut
  noter ses prises, mais elles restent sur son téléphone jusqu'à ce qu'une clé arrive.
- **Ce n'est pas du temps réel.** La page relit les données toutes les minutes et à
  chaque retour sur l'écran. Deux personnes devant la caisse voient leurs changements
  à quelques secondes d'intervalle, pas instantanément.

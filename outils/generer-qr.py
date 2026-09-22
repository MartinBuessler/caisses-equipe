#!/usr/bin/env python3
"""Genere, pour chaque caisse de caisses.json, le QR code et l'etiquette A6 a coller.

    python outils/generer-qr.py                 # toutes les caisses
    python outils/generer-qr.py kine-antoine    # une seule

Sort dans qr/ : <id>-qr.png, <id>-qr.svg, <id>-etiquette.pdf, <id>-etiquette.png
"""
import json, os, sys
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.svg import SvgPathImage
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "qr")
SITE = "https://martinbuessler.github.io/caisses-equipe/"
BLEU, ROUGE, TEXTE, GRIS = "#0b2a5b", "#d62828", "#111827", "#6b7280"
POLICES = "C:/Windows/Fonts"

try:
    pdfmetrics.registerFont(TTFont("Titre", os.path.join(POLICES, "arialbd.ttf")))
    pdfmetrics.registerFont(TTFont("Corps", os.path.join(POLICES, "arial.ttf")))
    F_T, F_C = "Titre", "Corps"
except Exception:
    F_T, F_C = "Helvetica-Bold", "Helvetica"


def police(fichier, taille):
    try:
        return ImageFont.truetype(os.path.join(POLICES, fichier), taille)
    except Exception:
        return ImageFont.load_default()


def qr_de(url, box=20, bord=2):
    q = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=box, border=bord)
    q.add_data(url)
    q.make(fit=True)
    return q


def couper(texte, police_pil, largeur, dessin):
    """Coupe un titre trop long en deux lignes."""
    if dessin.textlength(texte, font=police_pil) <= largeur:
        return [texte]
    mots, lignes, courante = texte.split(), [], ""
    for m in mots:
        essai = (courante + " " + m).strip()
        if dessin.textlength(essai, font=police_pil) <= largeur or not courante:
            courante = essai
        else:
            lignes.append(courante)
            courante = m
    lignes.append(courante)
    return lignes[:2]


def etiquette_pdf(chemin, titre, url, qr_png):
    L, H = 105 * mm, 148 * mm
    c = canvas.Canvas(chemin, pagesize=(L, H))
    # fond tricolore
    c.setFillColor(HexColor(BLEU));  c.rect(0, 0, L / 3, H, stroke=0, fill=1)
    c.setFillColor(white);           c.rect(L / 3, 0, L / 3, H, stroke=0, fill=1)
    c.setFillColor(HexColor(ROUGE)); c.rect(2 * L / 3, 0, L / 3, H, stroke=0, fill=1)
    # carte blanche
    marge = 8 * mm
    c.setFillColor(white); c.setStrokeColor(HexColor("#d9dee8"))
    c.roundRect(marge, marge, L - 2 * marge, H - 2 * marge, 5 * mm, stroke=1, fill=1)
    # titre, sur deux lignes si besoin
    c.setFillColor(HexColor(BLEU))
    taille = 20
    while taille > 12 and c.stringWidth(titre, F_T, taille) > L - 26 * mm:
        taille -= 1
    y = H - 24 * mm
    if c.stringWidth(titre, F_T, taille) > L - 26 * mm:
        mots = titre.split()
        milieu = len(mots) // 2
        l1, l2 = " ".join(mots[:milieu]), " ".join(mots[milieu:])
        c.setFont(F_T, taille); c.drawCentredString(L / 2, y, l1)
        c.drawCentredString(L / 2, y - taille * 0.95, l2)
        y -= taille * 0.95
    else:
        c.setFont(F_T, taille); c.drawCentredString(L / 2, y, titre)
    c.setFillColor(HexColor(TEXTE)); c.setFont(F_C, 10)
    c.drawCentredString(L / 2, y - 7 * mm, "Inventaire de l'équipe")
    # QR
    taille_qr = 60 * mm
    bas_qr = y - 7 * mm - 6 * mm - taille_qr
    c.drawImage(qr_png, (L - taille_qr) / 2, bas_qr, taille_qr, taille_qr)
    # consignes
    yc = bas_qr - 8 * mm
    c.setFillColor(HexColor(ROUGE)); c.setFont(F_T, 11)
    c.drawCentredString(L / 2, yc, "Scanne avant de te servir")
    c.setFillColor(HexColor(TEXTE)); c.setFont(F_C, 8.5)
    c.drawCentredString(L / 2, yc - 6 * mm, "Tu prends quelque chose ? Tu ranges quelque chose ?")
    c.drawCentredString(L / 2, yc - 10.5 * mm, "Note-le, l'équipe sait ce qu'il reste.")
    c.setFillColor(HexColor(GRIS)); c.setFont(F_C, 6.5)
    c.drawCentredString(L / 2, marge + 4 * mm, url.replace("https://", ""))
    c.showPage(); c.save()


def etiquette_png(chemin, titre, url, qr_png, ppp=300):
    L, H = int(105 / 25.4 * ppp), int(148 / 25.4 * ppp)
    im = Image.new("RGB", (L, H), "white")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, L // 3, H], fill=BLEU)
    d.rectangle([2 * L // 3, 0, L, H], fill=ROUGE)
    m = int(8 / 25.4 * ppp)
    d.rounded_rectangle([m, m, L - m, H - m], radius=int(5 / 25.4 * ppp),
                        fill="white", outline="#d9dee8", width=3)

    def centre(txt, y, f, couleur):
        d.text(((L - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=couleur)

    f_titre = police("arialbd.ttf", 84)
    lignes = couper(titre, f_titre, L - int(26 / 25.4 * ppp), d)
    if len(lignes) > 1:
        f_titre = police("arialbd.ttf", 66)
        lignes = couper(titre, f_titre, L - int(26 / 25.4 * ppp), d)
    y = int(15 / 25.4 * ppp)
    for ligne in lignes:
        centre(ligne, y, f_titre, BLEU)
        y += int(f_titre.size * 1.15)
    centre("Inventaire de l'équipe", y + int(1 / 25.4 * ppp), police("arial.ttf", 42), TEXTE)

    taille_qr = int(60 / 25.4 * ppp)
    haut_qr = y + int(10 / 25.4 * ppp)
    qr_im = Image.open(qr_png).convert("RGB").resize((taille_qr, taille_qr), Image.NEAREST)
    im.paste(qr_im, ((L - taille_qr) // 2, haut_qr))

    yb = haut_qr + taille_qr + int(6 / 25.4 * ppp)
    centre("Scanne avant de te servir", yb, police("arialbd.ttf", 46), ROUGE)
    centre("Tu prends quelque chose ? Tu ranges quelque chose ?", yb + int(7 / 25.4 * ppp), police("arial.ttf", 34), TEXTE)
    centre("Note-le, l'équipe sait ce qu'il reste.", yb + int(11.5 / 25.4 * ppp), police("arial.ttf", 34), TEXTE)
    centre(url.replace("https://", ""), H - m - int(6 / 25.4 * ppp), police("arial.ttf", 24), GRIS)
    im.save(chemin, dpi=(ppp, ppp))


def main():
    with open(os.path.join(RACINE, "caisses.json"), encoding="utf-8") as f:
        caisses = json.load(f)
    voulues = [a for a in sys.argv[1:] if not a.startswith("-")]
    if voulues:
        caisses = [c for c in caisses if c["id"] in voulues]
        if not caisses:
            sys.exit("Aucune caisse ne correspond. Connues : " + ", ".join(c["id"] for c in caisses))

    os.makedirs(SORTIE, exist_ok=True)
    for c in caisses:
        url = SITE + "?c=" + c["id"]
        base = os.path.join(SORTIE, c["id"])
        q = qr_de(url)
        png = base + "-qr.png"
        q.make_image(fill_color=BLEU, back_color="white").save(png)
        qr_de(url, box=10).make_image(image_factory=SvgPathImage).save(base + "-qr.svg")
        etiquette_pdf(base + "-etiquette.pdf", c["nom"], url, png)
        etiquette_png(base + "-etiquette.png", c["nom"], url, png)
        print("%-16s %s" % (c["id"], url))


if __name__ == "__main__":
    main()

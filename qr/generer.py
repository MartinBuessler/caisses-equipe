# Génère le QR code et l'étiquette A6 pour La Malle de Dorine
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.svg import SvgPathImage
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

URL = "https://martinbuessler.github.io/malle-de-dorine/"
OUT = os.path.dirname(os.path.abspath(__file__))
BLEU, ROUGE, TEXTE = "#0b2a5b", "#d62828", "#111827"

def qr_img(box=20, border=2):
    q = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=box, border=border)
    q.add_data(URL); q.make(fit=True)
    return q

# --- QR seul : PNG et SVG ---
q = qr_img()
q.make_image(fill_color=BLEU, back_color="white").save(os.path.join(OUT, "qr-malle-de-dorine.png"))
q2 = qr_img(box=10, border=2)
q2.make_image(image_factory=SvgPathImage).save(os.path.join(OUT, "qr-malle-de-dorine.svg"))

# --- Étiquette A6 (105 x 148 mm) en PDF ---
W, H = 105*mm, 148*mm
fonts = "C:/Windows/Fonts"
try:
    pdfmetrics.registerFont(TTFont("Titre", os.path.join(fonts, "arialbd.ttf")))
    pdfmetrics.registerFont(TTFont("Corps", os.path.join(fonts, "arial.ttf")))
    F_T, F_C = "Titre", "Corps"
except Exception:
    F_T, F_C = "Helvetica-Bold", "Helvetica"

pdf_path = os.path.join(OUT, "etiquette-malle-de-dorine.pdf")
c = canvas.Canvas(pdf_path, pagesize=(W, H))
# Fond tricolore : trois bandes verticales
c.setFillColor(HexColor(BLEU)); c.rect(0, 0, W/3, H, stroke=0, fill=1)
c.setFillColor(white);          c.rect(W/3, 0, W/3, H, stroke=0, fill=1)
c.setFillColor(HexColor(ROUGE)); c.rect(2*W/3, 0, W/3, H, stroke=0, fill=1)
# Carte blanche centrale
marge = 8*mm
c.setFillColor(white); c.setStrokeColor(HexColor("#d9dee8"))
c.roundRect(marge, marge, W-2*marge, H-2*marge, 5*mm, stroke=1, fill=1)
# Titre
c.setFillColor(HexColor(BLEU)); c.setFont(F_T, 20)
c.drawCentredString(W/2, H-24*mm, "La Malle de Dorine")
c.setFillColor(HexColor(TEXTE)); c.setFont(F_C, 10)
c.drawCentredString(W/2, H-31*mm, "Provisions de l'équipe")
# QR
qr_png = os.path.join(OUT, "qr-malle-de-dorine.png")
taille = 62*mm
c.drawImage(qr_png, (W-taille)/2, H-31*mm-6*mm-taille, taille, taille)
# Consignes
y = H-31*mm-6*mm-taille-8*mm
c.setFillColor(HexColor(ROUGE)); c.setFont(F_T, 11)
c.drawCentredString(W/2, y, "Scanne avant de te servir")
c.setFillColor(HexColor(TEXTE)); c.setFont(F_C, 8.5)
c.drawCentredString(W/2, y-6*mm, "Tu prends quelque chose ? Tu ranges quelque chose ?")
c.drawCentredString(W/2, y-10.5*mm, "Note-le, l'équipe sait ce qu'il reste.")
c.setFillColor(HexColor("#6b7280")); c.setFont(F_C, 7)
c.drawCentredString(W/2, marge+4*mm, URL.replace("https://", ""))
c.showPage(); c.save()

# --- Étiquette en PNG (aperçu, 300 dpi) ---
dpi = 300
pw, ph = int(105/25.4*dpi), int(148/25.4*dpi)
im = Image.new("RGB", (pw, ph), "white"); d = ImageDraw.Draw(im)
d.rectangle([0, 0, pw//3, ph], fill=BLEU); d.rectangle([2*pw//3, 0, pw, ph], fill=ROUGE)
m = int(8/25.4*dpi)
d.rounded_rectangle([m, m, pw-m, ph-m], radius=int(5/25.4*dpi), fill="white", outline="#d9dee8", width=3)
def font(path, size):
    try: return ImageFont.truetype(os.path.join(fonts, path), size)
    except Exception: return ImageFont.load_default()
def centre(txt, y, f, fill):
    w = d.textlength(txt, font=f); d.text(((pw-w)/2, y), txt, font=f, fill=fill)
centre("La Malle de Dorine", int(16/25.4*dpi), font("arialbd.ttf", 84), BLEU)
centre("Provisions de l'équipe", int(27/25.4*dpi), font("arial.ttf", 42), TEXTE)
qr_im = Image.open(qr_png).convert("RGB").resize((int(62/25.4*dpi),)*2, Image.NEAREST)
im.paste(qr_im, ((pw-qr_im.width)//2, int(37/25.4*dpi)))
yb = int(37/25.4*dpi) + qr_im.height + int(5/25.4*dpi)
centre("Scanne avant de te servir", yb, font("arialbd.ttf", 46), ROUGE)
centre("Tu prends quelque chose ? Tu ranges quelque chose ?", yb+int(7/25.4*dpi), font("arial.ttf", 34), TEXTE)
centre("Note-le, l'équipe sait ce qu'il reste.", yb+int(11.5/25.4*dpi), font("arial.ttf", 34), TEXTE)
centre(URL.replace("https://", ""), ph-m-int(6/25.4*dpi), font("arial.ttf", 28), "#6b7280")
im.save(os.path.join(OUT, "etiquette-malle-de-dorine.png"), dpi=(dpi, dpi))
print("OK :", URL)

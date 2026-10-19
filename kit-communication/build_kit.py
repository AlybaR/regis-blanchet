"""Build a discussion kit using the existing website identity.

Run with the bundled Codex Python runtime (reportlab is required). The SVG files
are intentionally text-editable and use the site's font names with fallbacks.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "kit-communication"
MODELS = KIT / "modeles"
PDF = ROOT / "output" / "pdf" / "kit-communication-regis-blanchet.pdf"
MODELS.mkdir(parents=True, exist_ok=True)
PDF.parent.mkdir(parents=True, exist_ok=True)

NAVY = "#132D59"
DEEP = "#0D2144"
CREAM = "#F8F8F6"
ALT = "#F1EFEA"
INK = "#222222"
MUTED = "#5A5E65"
BRONZE = "#BD8B57"
BRONZE_DARK = "#8A5A2E"
BURGUNDY = "#983F49"
WHITE = "#FFFFFF"
W, H = 842, 595


def register_fonts() -> None:
    fonts = {
        "Serif": KIT / "fonts" / "CormorantGaramond-Semibold.ttf",
        "SerifBold": KIT / "fonts" / "CormorantGaramond-Semibold.ttf",
        "Sans": KIT / "fonts" / "Inter-Regular.ttf",
        "SansBold": KIT / "fonts" / "Inter-Bold.ttf",
    }
    for name, path in fonts.items():
        if not path.exists():
            raise FileNotFoundError(f"Police manquante : {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))


def col(value: str):
    return colors.HexColor(value)


def rect(c, x, y, w, h, fill, stroke=None, sw=1):
    c.setFillColor(col(fill))
    if stroke:
        c.setStrokeColor(col(stroke))
        c.setLineWidth(sw)
    c.rect(x, y, w, h, fill=1, stroke=int(bool(stroke)))


def txt(c, x, y, value, size=12, font="Sans", color=INK, tracking=None):
    c.setFillColor(col(color))
    c.setFont(font, size)
    t = c.beginText(x, y)
    # PDF character spacing persists between text objects unless reset explicitly.
    t.setCharSpace(0 if tracking is None else tracking)
    t.textOut(value)
    c.drawText(t)


def lines(c, x, top, value, width, size=11, leading=None, font="Sans", color=INK, max_lines=99):
    leading = leading or size * 1.42
    chunks = []
    for paragraph in value.split("\n"):
        chunks.extend(simpleSplit(paragraph, font, size, width) or [""])
    for i, line in enumerate(chunks[:max_lines]):
        txt(c, x, top - i * leading, line, size, font, color)
    return top - min(len(chunks), max_lines) * leading


def rule(c, x1, y, x2, color=BRONZE, thickness=1.3):
    c.setStrokeColor(col(color))
    c.setLineWidth(thickness)
    c.line(x1, y, x2, y)


def mark(c, x, y, size=42, dark=True):
    rect(c, x, y, size, size, NAVY if dark else WHITE)
    txt(c, x + 8, y + size * .35, "RB", size * .39, "Serif", WHITE if dark else NAVY)
    rect(c, x + 8, y + 7, size - 16, 2, BRONZE)


def header(c, section, page):
    rect(c, 0, 0, W, H, CREAM)
    mark(c, 48, 528, 32)
    txt(c, 91, 548, "RÉGIS BLANCHET", 10, "SansBold", NAVY, 1.15)
    txt(c, 91, 534, "SÉNATEUR DE L’INDRE", 7, "SansBold", BRONZE_DARK, 1.0)
    txt(c, 622, 544, section.upper(), 8, "SansBold", MUTED, .7)
    rule(c, 48, 514, 794, "#D9D6D0", .7)
    rule(c, 48, 37, 794, "#D9D6D0", .7)
    txt(c, 48, 22, "DOCUMENT DE TRAVAIL · OCTOBRE 2026 · NON OFFICIEL", 7, "SansBold", MUTED, .45)
    txt(c, 773, 22, f"{page:02d}", 8, "SansBold", NAVY)


def section_title(c, kicker, title, subtitle=""):
    txt(c, 48, 481, kicker.upper(), 8, "SansBold", BRONZE_DARK, .9)
    txt(c, 48, 439, title, 32, "Serif", NAVY)
    if subtitle:
        lines(c, 49, 413, subtitle, 735, 10, 14, "Sans", MUTED)


def chip(c, x, y, value, width):
    rect(c, x, y, width, 25, WHITE, "#DDD6CC")
    txt(c, x + 10, y + 8, value, 7.5, "SansBold", NAVY)


def page_cover(c):
    rect(c, 0, 0, W, H, CREAM)
    rect(c, 0, 0, 394, H, DEEP)
    rect(c, 0, 0, 9, H, BRONZE)
    mark(c, 52, 492, 51)
    txt(c, 118, 520, "RÉGIS BLANCHET", 13, "SansBold", WHITE, 1.15)
    txt(c, 118, 500, "SÉNATEUR DE L’INDRE", 8, "SansBold", "#D5B894", 1)
    txt(c, 52, 400, "KIT DE", 36, "Serif", WHITE)
    txt(c, 52, 351, "COMMUNICATION", 31, "Serif", WHITE)
    rect(c, 52, 323, 52, 3, BRONZE)
    lines(c, 52, 286, "Décliner la charte actuelle sur les supports du mandat.", 290, 17, 23, "Serif", "#EBE8E2")
    txt(c, 52, 67, "PROPOSITION À DISCUTER AVEC L’ÉQUIPE", 8, "SansBold", "#D5B894", .8)
    txt(c, 52, 47, "20 octobre 2026", 9, "Sans", WHITE)

    txt(c, 440, 519, "LE MÊME VISAGE, PARTOUT", 9, "SansBold", BRONZE_DARK, 1)
    txt(c, 440, 469, "Un système simple", 31, "Serif", NAVY)
    txt(c, 440, 431, "pour la durée du mandat.", 28, "Serif", NAVY)
    lines(c, 441, 389, "Le site sert de référence visuelle. Ce dossier apporte des formats prêts à adapter, avec les mêmes couleurs, la même signature et des règles de publication claires.", 332, 11, 17, "Sans", MUTED)
    for y, number, label, detail in [
        (258, "01", "Réseaux", "faits publics · terrain · dossiers"),
        (204, "02", "Lettre et documents", "couverture · en-tête · signature"),
        (150, "03", "Presse et événements", "invitation · communiqué · signalétique"),
    ]:
        rule(c, 440, y + 36, 787, "#D6D1CA", .7)
        txt(c, 440, y + 9, number, 19, "Serif", BRONZE_DARK)
        txt(c, 478, y + 17, label, 13, "SansBold", NAVY)
        txt(c, 478, y + 1, detail, 8, "Sans", MUTED)
    txt(c, 440, 48, "Maquettes de travail : textes et usages à valider avant diffusion.", 7.5, "Sans", MUTED)


def page_identity(c):
    header(c, "Socle visuel", 2)
    section_title(c, "La base retenue", "Une seule identité pour tous les supports.", "Aucune nouvelle charte : ces repères reprennent le site déjà approuvé comme base de discussion.")
    swatches = [(NAVY, "Bleu nuit", "#132D59", WHITE), (CREAM, "Fond clair", "#F8F8F6", NAVY), (BRONZE, "Accent bronze", "#BD8B57", DEEP), (BURGUNDY, "Accent ponctuel", "#983F49", WHITE)]
    for i, (fill, label, code, ink) in enumerate(swatches):
        x = 48 + i * 190
        rect(c, x, 268, 172, 103, fill, "#E4E0D9" if fill == CREAM else None)
        txt(c, x + 11, 331, label, 11, "SansBold", ink)
        txt(c, x + 11, 284, code, 8, "Sans", ink)
    txt(c, 48, 227, "TITRES", 8, "SansBold", BRONZE_DARK, .7)
    txt(c, 48, 187, "Cormorant Garamond", 26, "Serif", NAVY)
    txt(c, 48, 166, "Élégance calme, grands titres courts.", 9, "Sans", MUTED)
    txt(c, 430, 227, "TEXTES ET INFORMATIONS", 8, "SansBold", BRONZE_DARK, .7)
    txt(c, 430, 190, "Inter", 22, "SansBold", NAVY)
    txt(c, 430, 166, "Lisibilité sur écran et sur papier.", 9, "Sans", MUTED)
    rect(c, 48, 69, 746, 72, ALT)
    mark(c, 66, 87, 37)
    txt(c, 116, 110, "Régis Blanchet", 17, "Serif", NAVY)
    txt(c, 117, 94, "SÉNATEUR DE L’INDRE", 7, "SansBold", BRONZE_DARK, 1)
    txt(c, 402, 111, "Signature constante", 11, "SansBold", NAVY)
    lines(c, 402, 94, "Monogramme RB, nom entier, fonction, date et source si un fait est cité. Pas de logo officiel du Sénat sans autorisation.", 365, 8, 11, "Sans", MUTED)


def social_card(c, x, y, kind):
    w, h = 218, 270
    if kind == 0:
        rect(c, x, y, w, h, NAVY)
        rect(c, x + 18, y + h - 44, 24, 24, WHITE)
        txt(c, x + 23, y + h - 36, "RB", 9, "SerifBold", NAVY)
        txt(c, x + 49, y + h - 36, "RÉGIS BLANCHET", 8, "SansBold", WHITE)
        txt(c, x + 20, y + 184, "FAIT PUBLIC · 06.10.26", 7, "SansBold", "#D7BA92", .5)
        lines(c, x + 20, y + 145, "Une commission pour les territoires.", 178, 20, 25, "Serif", WHITE)
        rect(c, x + 20, y + 50, 44, 2, BRONZE)
        lines(c, x + 20, y + 37, "Membre de la commission de l’aménagement du territoire et du développement durable.", 181, 7.6, 10, "Sans", WHITE)
    elif kind == 1:
        rect(c, x, y, w, h, ALT)
        rect(c, x + 14, y + 65, w - 28, h - 79, "#D7D3CC")
        txt(c, x + 38, y + 174, "PHOTO VALIDÉE", 13, "SansBold", NAVY, .5)
        txt(c, x + 45, y + 153, "lieu + date + crédit", 8, "Sans", MUTED)
        rect(c, x + 14, y + 14, w - 28, 42, WHITE)
        txt(c, x + 26, y + 39, "DANS L’INDRE", 7, "SansBold", BRONZE_DARK, .8)
        txt(c, x + 26, y + 24, "[Commune] · [Sujet]", 11, "SerifBold", NAVY)
    else:
        rect(c, x, y, w, h, CREAM, "#DCD7D0")
        txt(c, x + 18, y + h - 38, "DOSSIER / 01", 8, "SansBold", BRONZE_DARK, .6)
        txt(c, x + 18, y + 175, "[Le sujet]", 23, "Serif", NAVY)
        rule(c, x + 18, y + 155, x + w - 18, BRONZE, 1.5)
        for j, (num, label) in enumerate([("01", "Le constat"), ("02", "La démarche"), ("03", "La suite")]):
            yy = y + 121 - j * 38
            txt(c, x + 18, yy, num, 14, "Serif", BRONZE_DARK)
            txt(c, x + 52, yy + 2, label, 9, "SansBold", NAVY)
        txt(c, x + 18, y + 20, "RÉGIS BLANCHET · INDRE", 7, "SansBold", NAVY, .5)


def page_social(c):
    header(c, "Réseaux sociaux", 3)
    section_title(c, "Trois rendez-vous", "Des formats reconnaissables dans le fil.", "Une famille graphique, trois usages. Les maquettes terrain et dossier gardent des champs à renseigner.")
    kinds = ["01 / FAIT PUBLIC", "02 / TERRAIN", "03 / DOSSIER SUIVI"]
    captions = [
        "Annonce sourcée, date visible, lien vers le document officiel.",
        "Photo réelle, commune, personnes autorisées et crédit.",
        "Trois étapes constantes : constat, démarche, suite.",
    ]
    for i in range(3):
        x = 48 + i * 251
        social_card(c, x, 118, i)
        txt(c, x, 102, kinds[i], 8, "SansBold", BRONZE_DARK, .5)
        lines(c, x, 86, captions[i], 218, 8.2, 11, "Sans", MUTED)
    txt(c, 48, 51, "À décliner en carré 1080 × 1080 ; prévoir aussi un recadrage vertical pour les stories.", 8, "Sans", NAVY)


def page_letter(c):
    header(c, "Lettre et documents", 4)
    section_title(c, "Supports éditoriaux", "Une lettre qui se reconnaît dès la couverture.", "Même signature, mêmes repères. Les contenus du numéro zéro restent à faire valider.")
    x, y, w, h = 48, 72, 260, 313
    rect(c, x + 9, y - 8, w, h, "#E6E0D6")
    rect(c, x, y, w, h, WHITE, "#D9D4CE")
    rect(c, x, y + h - 64, w, 64, NAVY)
    txt(c, x + 22, y + h - 29, "RÉGIS BLANCHET", 11, "SansBold", WHITE, .5)
    txt(c, x + 22, y + h - 47, "SÉNATEUR DE L’INDRE", 7, "SansBold", "#D9B98F", .7)
    txt(c, x + 22, y + 215, "LA LETTRE", 8, "SansBold", BRONZE_DARK, 1)
    txt(c, x + 22, y + 164, "Des faits,", 31, "Serif", NAVY)
    txt(c, x + 22, y + 127, "des suites.", 31, "Serif", NAVY)
    rule(c, x + 22, y + 104, x + 98, BRONZE, 2)
    lines(c, x + 22, y + 81, "[Mois / année] · [Numéro validé]", 215, 9, 13, "Sans", MUTED)
    rect(c, x, y, w, 27, ALT)
    txt(c, x + 22, y + 9, "DOCUMENT DE TRAVAIL", 7, "SansBold", NAVY, .6)

    txt(c, 354, 373, "LETTRE D’INFORMATION", 8, "SansBold", BRONZE_DARK, .8)
    txt(c, 354, 346, "Un sommaire stable", 19, "Serif", NAVY)
    for i, (num, title, desc) in enumerate([
        ("01", "L’essentiel", "Un fait public, daté et relié à sa source."),
        ("02", "Dans l’Indre", "Une rencontre documentée, avec lieu et crédit photo."),
        ("03", "Le dossier", "Constat, démarche, réponse et prochaine étape."),
        ("04", "À suivre", "Ce qui est confirmé, ce qui reste ouvert."),
    ]):
        yy = 306 - i * 49
        rule(c, 354, yy + 24, 787, "#D8D3CB", .7)
        txt(c, 354, yy, num, 17, "Serif", BRONZE_DARK)
        txt(c, 391, yy + 5, title, 10, "SansBold", NAVY)
        txt(c, 391, yy - 9, desc, 8.3, "Sans", MUTED)
    rect(c, 354, 67, 433, 50, ALT)
    txt(c, 369, 97, "MÊME EN-TÊTE POUR LES NOTES, COURRIERS ET DOSSIERS", 8, "SansBold", NAVY)
    txt(c, 369, 81, "Signature, date, objet, contact validé et lien vers la source primaire.", 8, "Sans", MUTED)


def page_presse(c):
    header(c, "Presse et événements", 5)
    section_title(c, "Présence publique", "Le même ton, du communiqué à la salle.", "Les modèles utilisent des champs explicites pour éviter de suggérer qu’un événement est déjà annoncé.")
    rect(c, 48, 173, 445, 208, NAVY)
    rect(c, 48, 173, 6, 208, BRONZE)
    txt(c, 77, 351, "INVITATION / MAQUETTE", 8, "SansBold", "#D9B98F", 1)
    txt(c, 77, 304, "[Titre de la rencontre]", 25, "Serif", WHITE)
    txt(c, 77, 268, "[Date]  ·  [Heure]", 11, "SansBold", WHITE)
    txt(c, 77, 247, "[Lieu et commune]", 11, "Sans", WHITE)
    rule(c, 77, 225, 160, BRONZE, 2)
    txt(c, 77, 197, "RÉGIS BLANCHET · SÉNATEUR DE L’INDRE", 8, "SansBold", WHITE, .45)

    rect(c, 519, 173, 268, 208, WHITE, "#DCD7CF")
    rect(c, 519, 355, 268, 26, ALT)
    txt(c, 534, 365, "COMMUNIQUÉ / MODÈLE", 8, "SansBold", BRONZE_DARK, .6)
    txt(c, 534, 327, "Régis Blanchet", 16, "Serif", NAVY)
    txt(c, 534, 309, "SÉNATEUR DE L’INDRE", 7, "SansBold", BRONZE_DARK, .7)
    rule(c, 534, 294, 770, BRONZE, 1.5)
    txt(c, 534, 276, "[Date] · [Objet vérifié]", 9, "SansBold", NAVY)
    for yy, width in [(254, 219), (241, 231), (228, 192), (204, 229), (191, 208)]:
        rect(c, 534, yy, width, 2, "#CEC9C1")
    txt(c, 534, 179, "CONTACT PRESSE : À CONFIRMER", 7, "SansBold", MUTED)

    txt(c, 48, 137, "RÈGLES DE PRÉSENCE", 8, "SansBold", BRONZE_DARK, .8)
    txt(c, 48, 114, "Invitation", 12, "SansBold", NAVY)
    lines(c, 48, 98, "Une date, un lieu, un objet et une modalité d’accès vérifiés.", 214, 8, 11, "Sans", MUTED)
    txt(c, 299, 114, "Communiqué", 12, "SansBold", NAVY)
    lines(c, 299, 98, "Un fait, une citation validée, un contact presse autorisé.", 214, 8, 11, "Sans", MUTED)
    txt(c, 550, 114, "Signalétique", 12, "SansBold", NAVY)
    lines(c, 550, 98, "Nom et fonction lisibles, peu de texte, pas d’emblème emprunté.", 220, 8, 11, "Sans", MUTED)


def page_decision(c):
    header(c, "Décisions à prendre", 6)
    section_title(c, "Mise en place", "Un kit utile si chacun sait quoi valider.", "Les fichiers joints sont des modèles : ils deviennent des supports du mandat après choix et validation.")
    rect(c, 48, 165, 356, 219, WHITE, "#DED9D2")
    txt(c, 69, 353, "LIVRABLES DE CETTE VERSION", 8, "SansBold", BRONZE_DARK, .8)
    for i, value in enumerate([
        "3 modèles de publication carrée",
        "1 modèle de story / agenda",
        "1 couverture + 1 papier en-tête A4",
        "1 invitation A5 + 1 communiqué A4",
        "1 guide PDF + textes de départ",
    ]):
        yy = 319 - i * 34
        rect(c, 69, yy - 2, 8, 8, BRONZE)
        txt(c, 91, yy - 1, value, 10, "Sans", NAVY)
    rect(c, 428, 165, 359, 219, ALT)
    txt(c, 449, 353, "4 DÉCISIONS À PRENDRE EN ÉQUIPE", 8, "SansBold", BRONZE_DARK, .8)
    for i, (number, value) in enumerate([
        ("01", "Signature exacte et contact à afficher"),
        ("02", "Comptes du mandat et rôles de publication"),
        ("03", "Photographies utilisables et crédits"),
        ("04", "Circuit de relecture avant diffusion"),
    ]):
        yy = 316 - i * 42
        txt(c, 449, yy, number, 16, "Serif", BRONZE_DARK)
        lines(c, 488, yy + 4, value, 274, 9.7, 13, "SansBold", NAVY)
    rect(c, 48, 75, 739, 68, NAVY)
    txt(c, 69, 119, "CIRCUIT CONSEILLÉ", 8, "SansBold", "#D9B98F", .8)
    txt(c, 69, 94, "Fait & source  →  texte  →  image & autorisation  →  validation  →  publication  →  archivage", 10, "Sans", WHITE)
    txt(c, 48, 53, "Source du fait utilisé en exemple : senat.fr/senateurs/news.html (6 octobre 2026).", 7.5, "Sans", MUTED)


def svg(width, height, body, defs=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
<title>Maquette de communication Régis Blanchet - à personnaliser</title>
<defs><style><![CDATA[
.serif {{ font-family: 'Cormorant Garamond', Georgia, serif; }}
.sans {{ font-family: Inter, Arial, sans-serif; }}
]]></style>{defs}</defs>
{body}
</svg>'''


def e(value):
    return escape(value)


def save_svg(name, width, height, body):
    (MODELS / name).write_text(svg(width, height, body), encoding="utf-8")


def build_svgs():
    save_svg("01-post-fait-public-1080.svg", 1080, 1080, f'''
<rect width="1080" height="1080" fill="{NAVY}"/>
<rect x="70" y="70" width="88" height="88" fill="white"/><text x="88" y="128" class="serif" font-size="48" fill="{NAVY}">RB</text><rect x="86" y="138" width="56" height="4" fill="{BRONZE}"/>
<text x="182" y="112" class="sans" font-size="34" font-weight="700" letter-spacing="3" fill="white">RÉGIS BLANCHET</text>
<text x="182" y="150" class="sans" font-size="19" font-weight="700" letter-spacing="3" fill="#D5B894">SÉNATEUR DE L’INDRE</text>
<text x="77" y="292" class="sans" font-size="23" font-weight="700" letter-spacing="3" fill="#D5B894">FAIT PUBLIC · 6 OCTOBRE 2026</text>
<text x="72" y="435" class="serif" font-size="88" fill="white">Une commission pour</text>
<text x="72" y="533" class="serif" font-size="88" fill="white">les territoires.</text>
<rect x="75" y="587" width="130" height="5" fill="{BRONZE}"/>
<text x="75" y="661" class="sans" font-size="29" fill="white">Membre de la commission de l’aménagement</text>
<text x="75" y="706" class="sans" font-size="29" fill="white">du territoire et du développement durable.</text>
<line x1="75" y1="934" x2="1005" y2="934" stroke="#7990B0"/>
<text x="75" y="987" class="sans" font-size="23" fill="white">Source : Sénat · senat.fr/senateurs/news.html</text>
<text x="75" y="1032" class="sans" font-size="17" fill="#D5B894">MAQUETTE DE TRAVAIL · À VALIDER AVANT PUBLICATION</text>''')

    save_svg("02-post-terrain-1080.svg", 1080, 1080, f'''
<rect width="1080" height="1080" fill="{CREAM}"/>
<rect x="55" y="55" width="970" height="725" fill="#DCD9D2"/>
<rect x="78" y="78" width="924" height="679" fill="none" stroke="#B4A99A" stroke-width="2" stroke-dasharray="15 12"/>
<text x="335" y="382" class="sans" font-size="37" font-weight="700" fill="{NAVY}">PHOTO VALIDÉE</text>
<text x="350" y="428" class="sans" font-size="22" fill="{MUTED}">lieu · date · crédit · autorisations</text>
<rect x="55" y="780" width="970" height="245" fill="white"/>
<text x="83" y="834" class="sans" font-size="23" font-weight="700" letter-spacing="4" fill="{BRONZE_DARK}">DANS L’INDRE</text>
<text x="83" y="912" class="serif" font-size="68" fill="{NAVY}">[Commune] · [Sujet]</text>
<text x="83" y="981" class="sans" font-size="21" font-weight="700" fill="{NAVY}">RÉGIS BLANCHET · SÉNATEUR DE L’INDRE</text>
<text x="55" y="1056" class="sans" font-size="15" fill="{MUTED}">MODÈLE · NE PAS PUBLIER AVEC LES CHAMPS ENTRE CROCHETS</text>''')

    save_svg("03-post-dossier-1080.svg", 1080, 1080, f'''
<rect width="1080" height="1080" fill="{CREAM}"/>
<rect x="55" y="55" width="970" height="970" fill="white" stroke="#DCD7D0" stroke-width="2"/>
<text x="90" y="131" class="sans" font-size="26" font-weight="700" letter-spacing="4" fill="{BRONZE_DARK}">DOSSIER SUIVI / 01</text>
<text x="90" y="292" class="serif" font-size="99" fill="{NAVY}">[Le sujet]</text>
<rect x="90" y="337" width="900" height="5" fill="{BRONZE}"/>
<text x="90" y="446" class="serif" font-size="53" fill="{BRONZE_DARK}">01</text><text x="220" y="446" class="sans" font-size="42" font-weight="700" fill="{NAVY}">Le constat</text>
<text x="90" y="572" class="serif" font-size="53" fill="{BRONZE_DARK}">02</text><text x="220" y="572" class="sans" font-size="42" font-weight="700" fill="{NAVY}">La démarche</text>
<text x="90" y="698" class="serif" font-size="53" fill="{BRONZE_DARK}">03</text><text x="220" y="698" class="sans" font-size="42" font-weight="700" fill="{NAVY}">La suite</text>
<line x1="90" y1="901" x2="990" y2="901" stroke="#DCD7D0" stroke-width="2"/>
<text x="90" y="954" class="sans" font-size="23" font-weight="700" letter-spacing="2" fill="{NAVY}">RÉGIS BLANCHET · INDRE</text>
<text x="55" y="1056" class="sans" font-size="15" fill="{MUTED}">MODÈLE · RENSEIGNER LES FAITS, LEUR DATE ET LEUR SOURCE</text>''')

    save_svg("04-story-agenda-1080x1920.svg", 1080, 1920, f'''
<rect width="1080" height="1920" fill="{NAVY}"/>
<rect x="0" y="0" width="1080" height="20" fill="{BRONZE}"/>
<text x="75" y="157" class="sans" font-size="32" font-weight="700" letter-spacing="4" fill="white">RÉGIS BLANCHET</text>
<text x="75" y="205" class="sans" font-size="22" font-weight="700" letter-spacing="3" fill="#D5B894">SÉNATEUR DE L’INDRE</text>
<text x="75" y="430" class="sans" font-size="29" font-weight="700" letter-spacing="5" fill="#D5B894">RENDEZ-VOUS · MAQUETTE</text>
<text x="72" y="608" class="serif" font-size="111" fill="white">[Titre de la</text>
<text x="72" y="724" class="serif" font-size="111" fill="white">rencontre]</text>
<rect x="75" y="802" width="175" height="7" fill="{BRONZE}"/>
<text x="75" y="969" class="sans" font-size="48" font-weight="700" fill="white">[Date] · [Heure]</text>
<text x="75" y="1056" class="sans" font-size="43" fill="white">[Lieu, commune]</text>
<rect x="75" y="1240" width="930" height="320" fill="#1E3D70"/>
<text x="115" y="1324" class="sans" font-size="27" font-weight="700" fill="#D5B894">INFORMATIONS PRATIQUES</text>
<text x="115" y="1406" class="sans" font-size="31" fill="white">[Accès / inscription / public]</text>
<text x="115" y="1476" class="sans" font-size="31" fill="white">[Contact validé]</text>
<text x="75" y="1795" class="sans" font-size="25" fill="white">Visuel de travail : confirmer l’événement avant diffusion.</text>''')

    save_svg("05-couverture-lettre-a4.svg", 1240, 1754, f'''
<rect width="1240" height="1754" fill="white"/>
<rect x="0" y="0" width="1240" height="250" fill="{NAVY}"/>
<text x="90" y="106" class="sans" font-size="54" font-weight="700" letter-spacing="3" fill="white">RÉGIS BLANCHET</text>
<text x="90" y="170" class="sans" font-size="28" font-weight="700" letter-spacing="5" fill="#D5B894">SÉNATEUR DE L’INDRE</text>
<text x="90" y="473" class="sans" font-size="31" font-weight="700" letter-spacing="6" fill="{BRONZE_DARK}">LA LETTRE</text>
<text x="83" y="682" class="serif" font-size="148" fill="{NAVY}">Des faits,</text>
<text x="83" y="841" class="serif" font-size="148" fill="{NAVY}">des suites.</text>
<rect x="90" y="919" width="160" height="7" fill="{BRONZE}"/>
<text x="90" y="1043" class="sans" font-size="38" fill="{MUTED}">[Mois / année] · [Numéro validé]</text>
<rect x="90" y="1200" width="1060" height="365" fill="{ALT}"/>
<text x="138" y="1285" class="sans" font-size="29" font-weight="700" fill="{BRONZE_DARK}">DANS CE NUMÉRO</text>
<text x="138" y="1367" class="serif" font-size="57" fill="{NAVY}">[Le fait] · [Le terrain] · [Le dossier]</text>
<text x="90" y="1686" class="sans" font-size="23" font-weight="700" fill="{NAVY}">DOCUMENT DE TRAVAIL · CONTENUS SOUMIS À VALIDATION</text>''')

    save_svg("06-invitation-a5.svg", 1748, 1240, f'''
<rect width="1748" height="1240" fill="{NAVY}"/>
<rect x="0" y="0" width="18" height="1240" fill="{BRONZE}"/>
<text x="112" y="134" class="sans" font-size="50" font-weight="700" letter-spacing="5" fill="white">RÉGIS BLANCHET</text>
<text x="112" y="205" class="sans" font-size="29" font-weight="700" letter-spacing="4" fill="#D5B894">SÉNATEUR DE L’INDRE</text>
<text x="112" y="420" class="sans" font-size="30" font-weight="700" letter-spacing="6" fill="#D5B894">INVITATION · MAQUETTE</text>
<text x="106" y="597" class="serif" font-size="117" fill="white">[Titre de la rencontre]</text>
<rect x="112" y="661" width="170" height="7" fill="{BRONZE}"/>
<text x="112" y="782" class="sans" font-size="54" font-weight="700" fill="white">[Date]  ·  [Heure]</text>
<text x="112" y="871" class="sans" font-size="48" fill="white">[Lieu et commune]</text>
<line x1="112" y1="1085" x2="1637" y2="1085" stroke="#7990B0" stroke-width="2"/>
<text x="112" y="1146" class="sans" font-size="27" fill="white">[Modalités d’accès et contact validé]</text>''')

    save_svg("07-communique-a4.svg", 1240, 1754, f'''
<rect width="1240" height="1754" fill="white"/>
<rect width="1240" height="178" fill="{NAVY}"/>
<text x="80" y="83" class="sans" font-size="45" font-weight="700" letter-spacing="4" fill="white">RÉGIS BLANCHET</text>
<text x="80" y="131" class="sans" font-size="22" font-weight="700" letter-spacing="4" fill="#D5B894">SÉNATEUR DE L’INDRE</text>
<text x="80" y="253" class="sans" font-size="28" font-weight="700" letter-spacing="5" fill="{BRONZE_DARK}">COMMUNIQUÉ · MODÈLE</text>
<text x="80" y="344" class="serif" font-size="67" fill="{NAVY}">[Titre factuel et vérifié]</text>
<text x="80" y="416" class="sans" font-size="27" fill="{MUTED}">[Date] · [Lieu, si pertinent]</text>
<rect x="80" y="454" width="1080" height="5" fill="{BRONZE}"/>
<text x="80" y="557" class="sans" font-size="30" fill="{NAVY}">[Le fait principal en deux lignes au maximum.]</text>
<text x="80" y="620" class="sans" font-size="27" fill="{MUTED}">[Source primaire et contexte utile.]</text>
<text x="80" y="746" class="sans" font-size="27" fill="{MUTED}">[Développement court : ce qui est établi et ce qui reste à suivre.]</text>
<text x="80" y="809" class="sans" font-size="27" fill="{MUTED}">[Ajouter uniquement une citation relue et approuvée.]</text>
<rect x="80" y="1273" width="1080" height="215" fill="{ALT}"/>
<text x="115" y="1339" class="sans" font-size="24" font-weight="700" fill="{BRONZE_DARK}">POUR EN SAVOIR PLUS</text>
<text x="115" y="1398" class="sans" font-size="25" fill="{NAVY}">[Lien vers la source officielle]</text>
<text x="115" y="1443" class="sans" font-size="25" fill="{NAVY}">[Contact presse autorisé]</text>
<text x="80" y="1681" class="sans" font-size="20" fill="{MUTED}">MODÈLE DE TRAVAIL · NE PAS DIFFUSER AVEC LES CHAMPS ENTRE CROCHETS</text>''')

    save_svg("08-banniere-reseaux-1584x396.svg", 1584, 396, f'''
<rect width="1584" height="396" fill="{NAVY}"/>
<rect x="0" y="0" width="14" height="396" fill="{BRONZE}"/>
<circle cx="1320" cy="170" r="360" fill="none" stroke="#39557D" stroke-width="2"/>
<circle cx="1320" cy="170" r="268" fill="none" stroke="#39557D" stroke-width="2"/>
<text x="100" y="177" class="serif" font-size="94" fill="white">Régis Blanchet</text>
<rect x="105" y="212" width="103" height="5" fill="{BRONZE}"/>
<text x="105" y="272" class="sans" font-size="31" font-weight="700" letter-spacing="5" fill="#D5B894">SÉNATEUR DE L’INDRE</text>
<text x="105" y="352" class="sans" font-size="20" fill="white">MAQUETTE DE BANNIÈRE · À ADAPTER AU CADRAGE DE CHAQUE RÉSEAU</text>''')

    save_svg("09-carte-de-visite-85x55.svg", 1004, 650, f'''
<rect width="1004" height="650" fill="{CREAM}"/>
<rect x="0" y="0" width="1004" height="16" fill="{NAVY}"/>
<rect x="72" y="75" width="84" height="84" fill="{NAVY}"/>
<text x="89" y="128" class="serif" font-size="45" fill="white">RB</text>
<rect x="89" y="142" width="50" height="4" fill="{BRONZE}"/>
<text x="183" y="126" class="serif" font-size="60" fill="{NAVY}">Régis Blanchet</text>
<text x="185" y="165" class="sans" font-size="21" font-weight="700" letter-spacing="3" fill="{BRONZE_DARK}">SÉNATEUR DE L’INDRE</text>
<line x1="74" y1="231" x2="929" y2="231" stroke="#D5CFC6" stroke-width="2"/>
<text x="74" y="327" class="sans" font-size="30" fill="{NAVY}">[Adresse électronique validée]</text>
<text x="74" y="386" class="sans" font-size="30" fill="{NAVY}">[Téléphone validé]</text>
<text x="74" y="445" class="sans" font-size="30" fill="{NAVY}">[Site ou adresse de permanence validé]</text>
<text x="74" y="593" class="sans" font-size="18" fill="{MUTED}">MAQUETTE · À IMPRIMER SEULEMENT APRÈS VALIDATION DES COORDONNÉES</text>''')

    save_svg("10-papier-en-tete-a4.svg", 1240, 1754, f'''
<rect width="1240" height="1754" fill="white"/>
<rect x="0" y="0" width="1240" height="18" fill="{NAVY}"/>
<rect x="80" y="83" width="88" height="88" fill="{NAVY}"/>
<text x="99" y="139" class="serif" font-size="45" fill="white">RB</text>
<rect x="99" y="151" width="49" height="4" fill="{BRONZE}"/>
<text x="197" y="126" class="serif" font-size="58" fill="{NAVY}">Régis Blanchet</text>
<text x="199" y="171" class="sans" font-size="23" font-weight="700" letter-spacing="4" fill="{BRONZE_DARK}">SÉNATEUR DE L’INDRE</text>
<line x1="80" y1="222" x2="1160" y2="222" stroke="#D4CEC4" stroke-width="2"/>
<text x="80" y="319" class="sans" font-size="28" fill="{MUTED}">[Date] · [Destinataire]</text>
<text x="80" y="387" class="sans" font-size="28" font-weight="700" fill="{NAVY}">Objet : [objet du courrier]</text>
<text x="80" y="509" class="sans" font-size="26" fill="{MUTED}">[Corps du courrier validé]</text>
<line x1="80" y1="1613" x2="1160" y2="1613" stroke="#D4CEC4" stroke-width="2"/>
<text x="80" y="1660" class="sans" font-size="21" fill="{NAVY}">[Coordonnées validées] · [Site validé]</text>
<text x="80" y="1715" class="sans" font-size="18" fill="{MUTED}">MODÈLE DE TRAVAIL · RENSEIGNER L’EN-TÊTE ET LE PIED AVANT IMPRESSION</text>''')


def build_pdf():
    register_fonts()
    c = canvas.Canvas(str(PDF), pagesize=(W, H), pageCompression=1)
    c.setTitle("Kit de communication - Régis Blanchet - proposition")
    c.setAuthor("Atelier de travail - aperçu non officiel")
    for page in (page_cover, page_identity, page_social, page_letter, page_presse, page_decision):
        page(c)
        c.showPage()
    c.save()


if __name__ == "__main__":
    build_svgs()
    build_pdf()
    print(PDF)
    print(f"{len(list(MODELS.glob('*.svg')))} modèles SVG dans {MODELS}")

"""Replace les points de la carte de l'Indre sur les coordonnées officielles des mairies.

Source : geo.api.gouv.fr (champ « mairie » = emplacement de la mairie, donc du bourg).
Avant ce script, les points utilisaient le « centre » géométrique de la commune,
qui peut tomber à plusieurs kilomètres du bourg (Argenton, Mézières, Aigurande...).

Usage :  python tools/carte/maj_carte.py            (met à jour data + index.html)
         python tools/carte/maj_carte.py --telecharger   (rafraîchit d'abord communes-indre.json)
"""
import json, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMMUNES = Path(__file__).with_name("communes-indre.json")
DATA = ROOT / "assets/js/rencontres-data.js"
INDEX = ROOT / "index.html"
URL = "https://geo.api.gouv.fr/departements/36/communes?fields=nom,code,centre,population,codesPostaux,mairie&format=json"
VILLES = ["Châteauroux", "Issoudun", "La Châtre", "Le Blanc", "Buzançais"]


def projeter(lon, lat):
    """Même projection que le contour SVG (viewBox 0 0 420 426)."""
    x = 293.212439 * lon - 0.0796140795 * lat - 236.617332
    y = 0.0128972644 * lon - 428.340005 * lat + 20264.7299
    return round(x, 1), round(y, 1)


def charger_communes():
    communes = json.loads(COMMUNES.read_text(encoding="utf-8"))
    return {c["code"]: c for c in communes}, {c["nom"]: c for c in communes}


def position(c):
    lon, lat = (c.get("mairie") or c["centre"])["coordinates"]
    return lon, lat, *projeter(lon, lat)


def maj_svg(texte, rencontres, par_nom):
    q = r'\\?"'  # guillemet simple ou échappé (SVG inclus dans le JS)
    for r in rencontres:
        motif = re.compile(r'(data-id=' + q + re.escape(r["id"]) + q + r'.*?<circle cx=' + q + r')[\d.]+(' + q + r' cy=' + q + r')[\d.]+', re.S)
        texte, n = motif.subn(lambda m: f'{m.group(1)}{r["x"]}{m.group(2)}{r["y"]}', texte, count=1)
        if n != 1:
            raise SystemExit(f"Point introuvable dans le SVG : {r['id']}")
    for nom in VILLES:
        _, _, x, y = position(par_nom[nom])
        motif = re.compile(r'(<g class=' + q + r'city' + q + r'><title>' + re.escape(nom) + r' ·.*?</g>)', re.S)
        m = motif.search(texte)
        if not m:
            raise SystemExit(f"Ville introuvable dans le SVG : {nom}")
        bloc = m.group(1)
        ancien = re.search(r'cx=' + q + r'([\d.]+)' + q + r' cy=' + q + r'([\d.]+)', bloc)
        dx, dy = x - float(ancien.group(1)), y - float(ancien.group(2))
        bloc2 = re.sub(r'(c?[xy]=' + q + r')([\d.]+)', lambda k: k.group(1) + f'{float(k.group(2)) + (dx if "x" in k.group(1) else dy):.1f}', bloc)
        texte = texte[:m.start()] + bloc2 + texte[m.end():]
    return texte


def ecrire(chemin, texte):
    """Fins de ligne LF, comme dans le dépôt Git."""
    chemin.write_text(texte, encoding="utf-8", newline="\n")


def main():
    if "--telecharger" in sys.argv:
        COMMUNES.write_bytes(urllib.request.urlopen(URL, timeout=30).read())
    par_code, par_nom = charger_communes()
    src = DATA.read_text(encoding="utf-8")
    i, j = src.index("["), src.index("\n];") + 2
    rencontres = json.loads(src[i:j])
    for r in rencontres:
        c = par_code[r["insee"]]
        r["lon"], r["lat"], r["x"], r["y"] = position(c)
        r["population"] = c.get("population", r["population"])
    entete = src[:i].replace("(Insee via geo.api.gouv.fr)", "(Insee via geo.api.gouv.fr, points placés sur la mairie)")
    suite = maj_svg(src[j:], rencontres, par_nom)
    ecrire(DATA, entete + json.dumps(rencontres, ensure_ascii=False, indent=1) + suite)
    ecrire(INDEX, maj_svg(INDEX.read_text(encoding="utf-8"), rencontres, par_nom))
    print(f"{len(rencontres)} rencontres et {len(VILLES)} villes replacées sur les mairies.")


if __name__ == "__main__":
    main()

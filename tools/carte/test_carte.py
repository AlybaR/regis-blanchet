"""Contrôle : chaque point de la carte est sur la mairie officielle et à l'intérieur de l'Indre."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from maj_carte import DATA, INDEX, VILLES, charger_communes, position

par_code, par_nom = charger_communes()
src = DATA.read_text(encoding="utf-8")
rencontres = json.loads(src[src.index("["):src.index("\n];") + 2])
html = INDEX.read_text(encoding="utf-8")
polygones = [[tuple(map(float, p.split(","))) for p in re.findall(r"[\d.]+,[\d.]+", d)]
             for d in re.findall(r'<path class="arr" d="([^"]+)"', html)]


def dedans(x, y, poly):
    res = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            res = not res
    return res


erreurs = []
assert polygones, "contour introuvable"
for r in rencontres:
    _, _, x, y = position(par_code[r["insee"]])
    if abs(r["x"] - x) > 0.1 or abs(r["y"] - y) > 0.1:
        erreurs.append(f"{r['nom']} : données pas sur la mairie")
    for nom, texte in (("index.html", html), ("INDRE_SVG", src)):
        m = re.search(r'data-id=\\?"' + re.escape(r["id"]) + r'\\?".*?cx=\\?"([\d.]+)\\?" cy=\\?"([\d.]+)', texte, re.S)
        if not m or abs(float(m.group(1)) - x) > 0.1 or abs(float(m.group(2)) - y) > 0.1:
            erreurs.append(f"{r['nom']} : point mal placé dans {nom}")
    if not any(dedans(x, y, p) for p in polygones):
        erreurs.append(f"{r['nom']} : hors du contour de l'Indre")
for v in VILLES:
    _, _, x, y = position(par_nom[v])
    m = re.search(r'<title>' + re.escape(v) + r' ·.*?cx="([\d.]+)" cy="([\d.]+)"', html, re.S)
    if not m or abs(float(m.group(1)) - x) > 0.1 or abs(float(m.group(2)) - y) > 0.1:
        erreurs.append(f"{v} : ville mal placée")
print("\n".join(erreurs) or f"OK : {len(rencontres)} rencontres + {len(VILLES)} villes sur la mairie, dans l'Indre.")
sys.exit(1 if erreurs else 0)

#!/usr/bin/env python3
"""Mise à jour automatique de la rubrique « Au Sénat » à partir des données officielles du Sénat.

Lit UNIQUEMENT des sources publiques du Sénat (lecture seule, aucun identifiant) :
  1. data.senat.fr  ODSEN_GENERAL.csv / ODSEN_CUR_COMS.csv   -> profil (groupe, commission)
  2. senat.fr       fiche du sénateur                         -> délégations, date d'élection
  3. senat.fr       tableau des activités principales (JSON)  -> participations relevées par le Sénat
  4. data.senat.fr  questions-depuis-un-an.csv                -> questions écrites / orales et réponses

Écrit assets/js/travaux-data.js (window.TRAVAUX = {...}).

Garde-fous :
  - filtrage strict sur le matricule 21652W (et nom + prénom + circonscription pour les questions) ;
  - chaque élément doit avoir une date et un lien https://www.senat.fr/... sinon il est écarté ;
  - aucun texte rédigé : seuls des intitulés officiels sont repris ;
  - les votes (scrutins) ne sont PAS repris (votes de groupe par délégation, voir README) ;
  - si une source est indisponible ou si des éléments déjà publiés disparaissent, le script
    s'arrête en erreur SANS toucher au fichier : le site garde la version précédente ;
  - le fichier n'est réécrit que si les données ont changé (pas de commit inutile).

Usage : python3 tools/senat/maj_travaux.py [--dry-run]
Python 3.8+, bibliothèque standard uniquement.
"""
import csv
import datetime as dt
import hashlib
import html
import io
import json
import os
import re
import sys
import time
import urllib.request

MATRICULE = "21652W"
NOM, PRENOM, CIRCO = "Blanchet", "Régis", "Indre"
DEBUT_MANDAT = "2026-10-01"  # début de la session / du mandat

FICHE = "https://www.senat.fr/senateur/blanchet_regis21652w.html"
TABLEAU = "https://www.senat.fr/calendrier_activite/?matricule=21652W"
URLS = {
    "general": "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
    "coms": "https://data.senat.fr/data/senateurs/ODSEN_CUR_COMS.csv",
    "fiche": FICHE,
    "activites": "https://www.senat.fr/calendrier_activite/json/sen_21652W.json",
    "questions": "https://data.senat.fr/data/questions/questions-depuis-un-an.csv",
}

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SORTIE = os.path.join(RACINE, "assets", "js", "travaux-data.js")
URL_OK = re.compile(r"^https://(www\.|data\.)?senat\.fr/")

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]


class Arret(Exception):
    """Erreur bloquante : on ne publie rien."""


def telecharger(url, essais=3):
    req = urllib.request.Request(url, headers={"User-Agent": "maj-travaux-regis-blanchet/1.0 (site du senateur; lecture open data)"})
    for i in range(essais):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status != 200:
                    raise Arret("HTTP %s" % r.status)
                return r.read()
        except Exception as e:  # réseau, timeout...
            if i == essais - 1:
                raise Arret("Source indisponible : %s (%s)" % (url, e))
            time.sleep(5 * (i + 1))


def csv_senat(octets):
    """CSV data.senat.fr : latin-1, lignes de commentaire commençant par %."""
    texte = octets.decode("latin-1")
    lignes = [l for l in texte.splitlines() if l.strip() and not l.startswith("%")]
    return lignes


def https(url):
    if not url:
        return None
    url = url.strip()
    if url.startswith("/"):
        url = "https://www.senat.fr" + url
    url = re.sub(r"^http://", "https://", url)
    return url if URL_OK.match(url) else None


def date_fr(iso):
    d = dt.date.fromisoformat(iso[:10])
    return "%d %s %d" % (d.day, MOIS[d.month - 1], d.year)


# ---------------------------------------------------------------- profil
def profil():
    gen = list(csv.DictReader(csv_senat(telecharger(URLS["general"]))))
    lignes = [r for r in gen if r.get("Matricule") == MATRICULE]
    if len(lignes) != 1:
        raise Arret("Matricule %s introuvable (ou en double) dans ODSEN_GENERAL" % MATRICULE)
    r = lignes[0]
    if (r.get("Nom usuel"), r.get("Prénom usuel"), r.get("État"), r.get("Circonscription")) != (NOM, PRENOM, "ACTIF", CIRCO):
        raise Arret("Profil inattendu dans ODSEN_GENERAL : %s" % r)

    coms = list(csv.DictReader(csv_senat(telecharger(URLS["coms"]))))
    commissions = sorted({c["Nom commission"] for c in coms if c.get("Matricule") == MATRICULE and not c.get("Fin d'appartenance")})

    # Fiche senat.fr : délégations et date d'élection (enrichissement facultatif)
    delegations, elu_le = [], None
    try:
        t = telecharger(URLS["fiche"]).decode("utf-8", "ignore")
        t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
        txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
        m = re.search(r"Elu le (\d{1,2} \w+ \d{4})", txt)
        elu_le = m.group(1) if m else None
        bloc = re.search(r"Commissions, Délégations et Office Membre (.*?) Mandats locaux", txt)
        if bloc:
            for nom in re.findall(r"(Délégation [^.]*?)(?= Commission| Délégation| Office|$)", bloc.group(1)):
                nom = nom.strip()
                if 10 < len(nom) < 120:
                    delegations.append(nom[0].lower() + nom[1:])
    except Arret:
        pass  # la fiche est un complément : son absence ne bloque pas

    return {
        "matricule": MATRICULE,
        "nom": "Régis Blanchet",
        "circonscription": CIRCO,
        "groupe": "Union Centriste et Indépendants" if r.get("Groupe politique") == "UCI" else r.get("Groupe politique"),
        "courriel_officiel": r.get("Courrier électronique") or None,
        "commissions": commissions,
        "delegations": sorted(set(delegations)),
        "elu_le": elu_le,
        "fiche": FICHE,
    }


# ---------------------------------------------------------------- activités
def nettoie_titre(titre):
    titre = titre.replace("'", "'").strip()
    organe, _, objet = titre.partition(" - ")
    objet = objet.strip()
    objet = re.sub(r"^PPL\b", "Proposition de loi :", objet)
    objet = re.sub(r"^PJL\b", "Projet de loi :", objet)
    objet = re.sub(r"^PPLO\b", "Proposition de loi organique :", objet)
    if organe.startswith("Séance plénière"):
        return "Séance publique", objet or "Séance publique"
    if organe.lower().startswith("commission"):
        if re.match(r"^Réunion( [A-Z]{2,})?$", objet):
            objet = "Réunion de la " + organe[0].lower() + organe[1:]
        return "Commission", objet
    if organe.lower().startswith("délégation"):
        if re.match(r"^Réunion( [A-Z]{2,})?$", objet):
            objet = "Réunion de la " + organe[0].lower() + organe[1:]
        return "Délégation", objet
    return "Activité", (organe + (" : " + objet if objet else "")).strip()


def activites():
    data = json.loads(telecharger(URLS["activites"]).decode("utf-8"))
    if not isinstance(data, list):
        raise Arret("Format inattendu du tableau des activités")
    out = []
    for a in data:
        cls = (a.get("className") or "").upper()
        debut = (a.get("start") or "")[:10]
        if "SUSPENSION" in cls or a.get("allDay") or debut < DEBUT_MANDAT or not a.get("title"):
            continue
        type_, titre = nettoie_titre(a["title"])
        out.append({
            "id": hashlib.sha1((a["start"] + a["title"]).encode()).hexdigest()[:10],
            "date": debut,
            "heure": (a.get("start") or "")[11:16],
            "type": type_,
            "titre": titre,
            "source": TABLEAU,
            "source_libelle": "Tableau des activités principales, senat.fr",
        })
    return out


# ---------------------------------------------------------------- questions
def questions():
    rows = csv.DictReader(csv_senat(telecharger(URLS["questions"])), delimiter=";")
    out = []
    for q in rows:
        if q.get("Nom") != NOM or q.get("Prénom") != PRENOM or q.get("Circonscription") != CIRCO:
            continue
        url = https(q.get("URL Question"))
        if not url or not q.get("Date de publication JO"):
            continue
        nature = {"QE": "Question écrite", "QOSD": "Question orale", "QG": "Question d'actualité",
                  "QC": "Question crible"}.get(q.get("Nature"), "Question")
        out.append({
            "id": q.get("Référence"),
            "date": q["Date de publication JO"][:10],
            "type": nature,
            "titre": q.get("Titre", "").strip(),
            "ministere": q.get("Ministère de dépôt", "").strip(),
            "statut": q.get("Sort", "").strip(),
            "reponse_le": (q.get("Date de réponse JO") or "")[:10] or None,
            "source": url,
            "source_libelle": "Question n° %s, senat.fr" % q.get("Numéro", ""),
        })
    return out


# ---------------------------------------------------------------- écriture
def lire_precedent():
    try:
        with open(SORTIE, encoding="utf-8") as f:
            t = f.read()
        return json.loads(t[t.index("{"): t.rindex("}") + 1])
    except (OSError, ValueError):
        return None


def main():
    dry = "--dry-run" in sys.argv
    nouveau = {"profil": profil(), "activites": activites(), "questions": questions()}
    for cle in ("activites", "questions"):
        nouveau[cle] = [x for x in nouveau[cle] if x["date"] and URL_OK.match(x["source"])]
        nouveau[cle].sort(key=lambda x: (x["date"], x.get("heure", "")), reverse=True)

    precedent = lire_precedent()
    if precedent:
        # Les éléments déjà publiés ne doivent pas disparaître (sauf questions de plus d'un an, fenêtre du fichier source)
        anciens = {x["id"] for x in precedent.get("activites", [])}
        manquants = anciens - {x["id"] for x in nouveau["activites"]}
        if manquants:
            raise Arret("%d activité(s) déjà publiée(s) absentes de la source : arrêt par sécurité" % len(manquants))
        un_an = (dt.date.today() - dt.timedelta(days=360)).isoformat()
        q_anciennes = {x["id"] for x in precedent.get("questions", []) if x["date"] >= un_an}
        if q_anciennes - {x["id"] for x in nouveau["questions"]}:
            raise Arret("Question(s) déjà publiée(s) absentes de la source : arrêt par sécurité")
        comparable = {k: precedent.get(k) for k in ("profil", "activites", "questions")}
        if comparable == nouveau:
            print("Aucun changement.")
            return 0

    nouveau["mis_a_jour_le"] = dt.date.today().isoformat()
    nouveau["mis_a_jour_le_fr"] = date_fr(nouveau["mis_a_jour_le"])
    nouveau["sources"] = [
        {"libelle": "Fiche officielle du sénateur", "url": FICHE},
        {"libelle": "Tableau des activités principales", "url": TABLEAU},
        {"libelle": "Open data du Sénat (data.senat.fr)", "url": "https://data.senat.fr/"},
    ]
    entete = ("/* FICHIER GÉNÉRÉ AUTOMATIQUEMENT par tools/senat/maj_travaux.py — ne pas modifier à la main.\n"
              "   Source : données publiques du Sénat (licence ouverte). */\n")
    contenu = entete + "window.TRAVAUX = " + json.dumps(nouveau, ensure_ascii=False, indent=1) + ";\n"

    n_act = len(nouveau["activites"]) - len((precedent or {}).get("activites", []))
    n_q = len(nouveau["questions"]) - len((precedent or {}).get("questions", []))
    resume = "Au Sénat : %+d activité(s), %+d question(s)" % (n_act, n_q)
    if dry:
        print(contenu[:1500])
    else:
        with open(SORTIE, "w", encoding="utf-8") as f:
            f.write(contenu)
    print(resume)
    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a") as f:
            f.write("resume=%s\n" % resume)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Arret as e:
        print("ARRÊT — rien n'a été modifié : %s" % e, file=sys.stderr)
        sys.exit(1)

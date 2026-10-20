"""Tests hors ligne des garde-fous : python3 tools/senat/test_maj_travaux.py"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maj_travaux as m  # noqa: E402

ENTETE_Q = ("Sort;Nature;Numéro;Référence;Titre;Nom;Prénom;Civilité;Circonscription;Groupe;Type Appartenance;"
            "Date de publication JO;Ministère de dépôt;Date de transmission;Ministère de transmission;"
            "Ministère de réponse;Date de réponse JO;Référence de la question rappelée;Thème(s);Thème QC;URL Question")


def ligne_q(nom="Blanchet", prenom="Régis", circo="Indre", url="http://www.senat.fr/questions/base/2026/qSEQ261000001.html", ref="SEQ261000001"):
    return ("En cours;QE;00001;%s;Desserte ferroviaire POLT;%s;%s;M.;%s;UC;;2026-10-22;Transports;;;;;;Transports;;%s"
            % (ref, nom, prenom, circo, url))


class Faux:
    def __init__(self, sources):
        self.sources = sources

    def __call__(self, url, essais=3):
        for cle, val in self.sources.items():
            if m.URLS[cle] == url:
                return val.encode("latin-1") if cle == "questions" else val.encode("utf-8")
        raise m.Arret("non simulé")


ORIG = {k: getattr(m, k) for k in ("telecharger", "profil", "activites", "questions", "SORTIE")}


class Tests(unittest.TestCase):
    def tearDown(self):
        for k, v in ORIG.items():
            setattr(m, k, v)

    def test_questions_filtre_strict(self):
        csv_q = "\n".join([ENTETE_Q, ligne_q(), ligne_q(prenom="Jean-Pierre", ref="X1"),
                           ligne_q(circo="Loire", ref="X2"), ligne_q(url="https://exemple.com/faux", ref="X3")])
        m.telecharger = Faux({"questions": csv_q})
        q = m.questions()
        self.assertEqual([x["id"] for x in q], ["SEQ261000001"])
        self.assertTrue(q[0]["source"].startswith("https://www.senat.fr/"))
        self.assertEqual(q[0]["type"], "Question écrite")

    def test_titres(self):
        self.assertEqual(m.nettoie_titre("Séance plénière - PPL Stocks de médicaments"),
                         ("Séance publique", "Proposition de loi : Stocks de médicaments"))
        self.assertEqual(m.nettoie_titre("Commission de l'aménagement du territoire - Réunion CATDD")[1],
                         "Réunion de la commission de l'aménagement du territoire")

    def test_activite_disparue_bloque(self):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8")
        tmp.write("window.TRAVAUX = " + json.dumps({"activites": [{"id": "disparue"}], "questions": []}) + ";")
        tmp.close()
        m.SORTIE = tmp.name
        m.profil = lambda: {}
        m.activites = lambda: []
        m.questions = lambda: []
        with self.assertRaises(m.Arret):
            m.main()
        with open(tmp.name, encoding="utf-8") as f:
            self.assertIn("disparue", f.read())  # fichier intact
        os.unlink(tmp.name)


if __name__ == "__main__":
    unittest.main()

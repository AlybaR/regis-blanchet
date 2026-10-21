# Aperçu non officiel du projet de site de Régis Blanchet

Site à partager : https://alybar.github.io/regis-blanchet/

Ce dépôt public contient uniquement les fichiers nécessaires à une démonstration du site. Il est distinct du dépôt de travail privé et du site de campagne préexistant.

Les informations sur le mandat sont liées à la [fiche officielle du Sénat](https://www.senat.fr/senateur/blanchet_regis21652w.html) et aux [résultats des sénatoriales 2026 dans l'Indre](https://senatoriales2026.senat.fr/departement/36-indre). Le numéro zéro de la lettre est une proposition éditoriale à valider. Son mot d'ouverture est imaginé, non signé par Régis Blanchet.

Les deux photographies de la page d'accueil proviennent du [site de campagne préexistant](https://regisblanchet2026.github.io/). Les visuels de la lettre sont des photographies réelles sous licence libre (crédits dans `kit-communication/exemples/photos/CREDITS.md`) ; aucune image n'est générée. Aucun formulaire ni collecte de données n'est intégré.

Les liens Facebook, Instagram et LinkedIn ont été repris des liens publics du site de campagne le 20 octobre 2026. Ils sont présentés comme comptes de campagne, distincts du contact institutionnel à confirmer.

La rubrique « Au Sénat » (accueil et `au-senat.html`) se met à jour seule chaque nuit à partir des données publiques du Sénat : voir [tools/senat/README.md](tools/senat/README.md).

La publication de cet aperçu ne vaut pas validation d'un site officiel du mandat.

Les [propositions éditoriales](PROPOSITIONS_EDITORIALES.md) donnent à l’équipe des exemples d’articles, de lettres et une trame de vérification pour la suite du site.

La [charte en situation](output/pdf/03_charte_en_situation_regis_blanchet.pdf) (6 pages, source : `kit-communication/exemples/planche-exemples.html`) montre la charte appliquée à de vrais contenus publics vérifiés.

Le [kit de communication du mandat](kit-communication/README.md) décline la charte actuelle sur les réseaux, la lettre, la presse et les invitations. Le [dossier PDF](output/pdf/kit-communication-regis-blanchet.pdf) et les modèles sont des propositions de travail à valider avec l’équipe. Le design du site actuel n’a pas été modifié.

## Carte des rencontres (mise à jour du 21 octobre 2026)

Les points de la carte de l'Indre sont placés sur la **mairie** de chaque commune (coordonnées officielles geo.api.gouv.fr), et non plus sur le centre géométrique du territoire communal, qui pouvait tomber à 3 ou 4 km du bourg. Pour ajouter une rencontre : compléter `assets/js/rencontres-data.js` (code Insee), dupliquer un point dans `index.html`, puis lancer `python tools/carte/maj_carte.py` et `python tools/carte/test_carte.py`.

La lettre s'intitule « La lettre de Régis Blanchet ». Elle ne porte plus le logo du groupe Union Centriste (source : `kit-communication/exemples/lettre.html`).

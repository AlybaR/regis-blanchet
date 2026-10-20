# Rubrique « Au Sénat » — mise à jour automatique

## En une phrase

Chaque nuit, un robot GitHub lit les données **publiques** du Sénat sur Régis Blanchet et met à jour la rubrique « Au Sénat » du site (accueil + page `au-senat.html`). Personne n'a rien à faire.

## Ce qui est repris

| Donnée | Source officielle | Affichage |
|---|---|---|
| Groupe, commission | data.senat.fr — `ODSEN_GENERAL.csv`, `ODSEN_CUR_COMS.csv` | Profil |
| Délégations, date d'élection | senat.fr — fiche du sénateur | Profil (complément facultatif) |
| Séances, réunions de commission | senat.fr — tableau des activités principales (`calendrier_activite/json/sen_21652W.json`) | Fil d'activité |
| Questions au Gouvernement et réponses | data.senat.fr — `questions-depuis-un-an.csv` | Fil d'activité |

**Pas repris volontairement : les votes (scrutins).** Au Sénat, beaucoup de votes sont exprimés par le groupe pour tous ses membres. Les afficher automatiquement pourrait laisser croire à une position personnelle. À décider avec le sénateur.

## Garde-fous

- Filtre strict sur le matricule `21652W` (et nom + prénom + Indre pour les questions).
- Aucun texte rédigé : uniquement les intitulés officiels (« PPL » est seulement développé en « Proposition de loi : »).
- Chaque ligne a une date et un lien `https://www.senat.fr/…`, sinon elle est écartée.
- Si une source est en panne ou si un élément déjà publié disparaît : **arrêt sans rien modifier**, le site garde la version précédente et GitHub envoie un courriel d'échec.
- Le fichier n'est réécrit que si les données changent : un commit = une vraie nouveauté, avec un message du type « Au Sénat : +2 activité(s), +1 question(s) ».
- Côté site, les textes sont insérés en texte brut (`textContent`), jamais en HTML.
- Rien n'est publié sur les réseaux sociaux.

## Fichiers

- `tools/senat/maj_travaux.py` — le script (Python 3, bibliothèque standard, aucune clé, aucun mot de passe).
- `tools/senat/test_maj_travaux.py` — tests hors ligne des garde-fous (lancés avant chaque mise à jour).
- `assets/js/travaux-data.js` — **généré**, ne pas modifier à la main.
- `assets/js/travaux.js` — affichage (accueil `#travaux-live` et page `au-senat.html`).
- `.github/workflows/maj-au-senat.yml` — le robot : chaque nuit + bouton manuel.

## Utilisation

- Mettre à jour tout de suite : GitHub > onglet **Actions** > « Mise à jour Au Sénat » > **Run workflow**.
- Couper l'automatisation : même écran > « ··· » > **Disable workflow**. Le site garde les dernières données.
- Annuler une mise à jour : revenir au commit précédent (`git revert <commit>`).
- En local : `python3 tools/senat/maj_travaux.py` (ou `--dry-run` pour voir sans écrire).

## Prochaines briques possibles

1. Amendements (base Ameli, data.senat.fr) et interventions en séance (comptes rendus).
2. Brouillons de posts dans Notion pour chaque nouveauté importante, **toujours validés à la main**.
3. Repérage automatique des textes qui concernent l'Indre.
